"""Web Push for the phone app (1.0.8): VAPID (RFC 8292) and aes128gcm payload encryption (RFC 8291), with the
`cryptography` library (Apache-2.0/BSD). A push carries no content: only the production's id. The phone looks the
name up in its own encrypted store and shows "Something new in SHADE"; the push service, and the hub, see nothing else.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import threading
import time
from urllib.parse import urlparse

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def unb64u(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _pub_bytes(key: ec.EllipticCurvePrivateKey | ec.EllipticCurvePublicKey) -> bytes:
    pub = key.public_key() if isinstance(key, ec.EllipticCurvePrivateKey) else key
    return pub.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)


def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    return hmac.new(prk, info + b"\x01", hashlib.sha256).digest()[:length]


def encrypt(payload: bytes, p256dh: str, auth: str, *, salt: bytes | None = None,
            server_key: ec.EllipticCurvePrivateKey | None = None) -> bytes:
    """RFC 8291 aes128gcm: one record, the whole body ready to POST."""
    ua_pub = unb64u(p256dh)
    as_key = server_key or ec.generate_private_key(ec.SECP256R1())
    as_pub = _pub_bytes(as_key)
    shared = as_key.exchange(ec.ECDH(), ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), ua_pub))
    prk_key = hmac.new(unb64u(auth), shared, hashlib.sha256).digest()
    ikm = _hkdf_expand(prk_key, b"WebPush: info\x00" + ua_pub + as_pub, 32)
    salt = salt or os.urandom(16)
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    cek = _hkdf_expand(prk, b"Content-Encoding: aes128gcm\x00", 16)
    nonce = _hkdf_expand(prk, b"Content-Encoding: nonce\x00", 12)
    ct = AESGCM(cek).encrypt(nonce, payload + b"\x02", None)
    return salt + (4096).to_bytes(4, "big") + bytes([len(as_pub)]) + as_pub + ct


def decrypt(body: bytes, ua_key: ec.EllipticCurvePrivateKey, auth: str) -> bytes:
    """What a browser does on receipt (used by the tests to check payloads carry nothing but the id)."""
    salt, idlen = body[:16], body[20]
    as_pub, ct = body[21:21 + idlen], body[21 + idlen:]
    ua_pub = _pub_bytes(ua_key)
    shared = ua_key.exchange(ec.ECDH(), ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), as_pub))
    ikm = _hkdf_expand(hmac.new(unb64u(auth), shared, hashlib.sha256).digest(), b"WebPush: info\x00" + ua_pub + as_pub, 32)
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    pt = AESGCM(_hkdf_expand(prk, b"Content-Encoding: aes128gcm\x00", 16)).decrypt(
        _hkdf_expand(prk, b"Content-Encoding: nonce\x00", 12), ct, None)
    return pt.rstrip(b"\x00")[:-1]


def new_vapid_key() -> str:
    """A new VAPID private key as base64url of the 32-byte scalar (for the deploy kit's .env)."""
    k = ec.generate_private_key(ec.SECP256R1())
    return b64u(k.private_numbers().private_value.to_bytes(32, "big"))


class Push:
    def __init__(self, private_key: str, subject: str, http: httpx.Client | None = None):
        d = int.from_bytes(unb64u(private_key), "big")
        self.key = ec.derive_private_key(d, ec.SECP256R1())
        self.public = b64u(_pub_bytes(self.key))
        self.subject = subject
        self.http = http or httpx.Client(timeout=10)

    def vapid(self, endpoint: str) -> str:
        u = urlparse(endpoint)
        head = b64u(json.dumps({"typ": "JWT", "alg": "ES256"}, separators=(",", ":")).encode())
        body = b64u(json.dumps({"aud": f"{u.scheme}://{u.netloc}", "exp": int(time.time()) + 12 * 3600,
                                "sub": self.subject}, separators=(",", ":")).encode())
        r, s = decode_dss_signature(self.key.sign(f"{head}.{body}".encode(), ec.ECDSA(hashes.SHA256())))
        return f"vapid t={head}.{body}.{b64u(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}, k={self.public}"

    def payload(self, production: str) -> bytes:
        return json.dumps({"p": production}, separators=(",", ":")).encode()

    def send(self, sub: dict, production: str) -> int:
        body = encrypt(self.payload(production), sub["keys"]["p256dh"], sub["keys"]["auth"])
        r = self.http.post(sub["endpoint"], content=body, headers={
            "Authorization": self.vapid(sub["endpoint"]), "Content-Encoding": "aes128gcm", "TTL": "86400",
            "Urgency": "normal", "Content-Type": "application/octet-stream"})
        return r.status_code

    def notify(self, store, users, production: str, wait: bool = False):
        """Push to every subscribed device of these users, in the background. Gone subscriptions are dropped."""
        users = list(users)
        if not users:
            return
        qs = ",".join("?" * len(users))
        rows = store.q(f"SELECT p.device, p.sub FROM push_subs p JOIN devices d ON d.id=p.device "
                       f"WHERE d.status='approved' AND d.user IN ({qs})", users)

        def run():
            for r in rows:
                try:
                    code = self.send(json.loads(r["sub"]), production)
                    if code in (404, 410):
                        with store.lock:
                            store.x("DELETE FROM push_subs WHERE device=?", (r["device"],))
                except Exception:  # noqa: BLE001 - a push is best-effort
                    pass
        if wait:
            run()
        else:
            threading.Thread(target=run, daemon=True, name="room-push").start()
