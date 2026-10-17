"""Web Push (1.0.8): a push carries the production's id and nothing else, encrypted for the phone (RFC 8291), with a
valid VAPID signature (RFC 8292)."""
import base64
import json
import time

import httpx
import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

from room_hub import push as P
from room_world import shade, space_named


@pytest.fixture(scope="module")
def w(tmp_path_factory):
    sent = []

    def handler(req: httpx.Request):
        sent.append(req)
        return httpx.Response(201)
    pusher = P.Push(P.new_vapid_key(), "mailto:room@example.com", http=httpx.Client(transport=httpx.MockTransport(handler)))
    world = shade(tmp_path_factory.mktemp("push"), push=pusher)
    world.sent, world.pusher = sent, pusher
    return world


def subscribe(c):
    key = ec.generate_private_key(ec.SECP256R1())
    auth = P.b64u(b"0123456789abcdef")
    pub = P.b64u(key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint))
    c._req("POST", "/api/push/subscribe", json={"subscription": {"endpoint": f"https://push.example.com/{c.me}",
                                                                 "keys": {"p256dh": pub, "auth": auth}}})
    return key, auth


def wait_for(sent, n, timeout=5):
    end = time.time() + timeout
    while len(sent) < n and time.time() < end:
        time.sleep(0.05)
    return sent


def test_pushes_carry_only_the_production(w):
    key, auth = subscribe(w.lea)
    assert w.tim._req("GET", "/api/push/key")["key"] == w.pusher.public
    dm = w.alex.dm(w.shade, w.lea.me)
    w.alex.post([dm], "msg", {"text": "ZZPICKUPCHANGEDZZ"})
    req = wait_for(w.sent, 1)[-1]
    assert str(req.url) == f"https://push.example.com/{w.lea.me}"
    assert req.headers["Content-Encoding"] == "aes128gcm" and req.headers["TTL"] == "86400"
    body = req.content
    assert b"ZZPICKUPCHANGEDZZ" not in body and b"ZZSHADEZZ" not in body
    assert json.loads(P.decrypt(body, key, auth)) == {"p": w.shade}          # nothing but the production's id
    # the VAPID header: a JWT for the push service's origin, signed with the hub's key
    t, k = [x.split("=", 1)[1] for x in req.headers["Authorization"].removeprefix("vapid ").split(", ")]
    head, claims, sig = t.split(".")
    assert json.loads(P.unb64u(claims))["aud"] == "https://push.example.com" and k == w.pusher.public
    raw = P.unb64u(sig)
    pub = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), P.unb64u(k))
    pub.verify(encode_dss_signature(int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big")),
               f"{head}.{claims}".encode(), ec.ECDSA(hashes.SHA256()))


def test_people_who_cant_see_it_get_no_push(w):
    subscribe(w.grip)
    n = len(w.sent)
    cam = space_named(w.dp, w.shade, "ZZCAMERAZZ")
    w.dp.post([cam], "msg", {"text": "x"}, mentions=[w.grip.me])          # the grip can't see Camera
    time.sleep(0.4)
    assert all(w.grip.me not in str(r.url) for r in w.sent[n:])


def test_rfc8291_round_trip_with_a_fixed_salt():
    ua = ec.generate_private_key(ec.SECP256R1())
    pub = P.b64u(ua.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint))
    auth = P.b64u(b"\x01" * 16)
    body = P.encrypt(b'{"p":"p_x"}', pub, auth, salt=b"\x02" * 16)
    assert body[:16] == b"\x02" * 16 and int.from_bytes(body[16:20], "big") == 4096 and body[20] == 65
    assert P.decrypt(body, ua, auth) == b'{"p":"p_x"}'
