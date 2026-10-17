"""The Room's end-to-end encryption (1.0.8), shared by the hub, the Studio client and the tests.

The phone app implements the same formats with libsodium.js (hub/static/room-crypto.js); tests/test_room_crypto.py
checks the two against each other. Everything here is libsodium through PyNaCl (Apache-2.0):

- Device keys: X25519 (crypto_box) to receive keys, Ed25519 (crypto_sign) to sign.
- Space keys: 32 random bytes per space and epoch, used with XChaCha20-Poly1305-IETF. A key is wrapped to each
  recipient device with a sealed box (crypto_box_seal), and the wrap is signed by the device that made it.
- Every item (message, note, file manifest, directory entry, call sheet) is a signed header plus ciphertext; the
  header is the AEAD's associated data, so a ciphertext can't be moved to another space, epoch or item.
- Signed headers hold only ASCII strings, integers, booleans and lists or objects of them, so their canonical JSON
  is the same in Python and JavaScript. Free text only ever travels inside ciphertext.
- Joining: three safety words from a commit-then-reveal exchange (SAS). The joining device commits to its keys and a
  nonce before it sees the executive's nonce, and the executive sends its nonce before it sees the joiner's, so a
  hub in the middle gets one guess at 33 bits per attempt and can't grind keys offline. The founder's signing key is
  part of the words, so the hub can't hand a new device a false root of trust.
- Trust: a device is trusted when its record is signed by a trusted executive device, back to the founder.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from pathlib import Path

import nacl.bindings as nb
from nacl.public import PrivateKey, PublicKey, SealedBox
from nacl.signing import SigningKey, VerifyKey

VERSION = "room-v1"
CHUNK = 4 * 1024 * 1024                     # file chunk size before encryption
WORDS = Path(__file__).with_name("words.txt").read_text(encoding="utf-8").split()
assert len(WORDS) == 2048


# ---------------------------------------------------------------- encoding

def b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _check_ascii(v, path="$"):
    if v is None or isinstance(v, bool) or isinstance(v, int):
        return
    if isinstance(v, str):
        if not v.isascii():
            raise ValueError(f"signed field {path} must be ASCII")
        return
    if isinstance(v, list):
        for i, x in enumerate(v):
            _check_ascii(x, f"{path}[{i}]")
        return
    if isinstance(v, dict):
        for k, x in v.items():
            if not isinstance(k, str) or not k.isascii():
                raise ValueError(f"signed key at {path} must be ASCII")
            _check_ascii(x, f"{path}.{k}")
        return
    raise ValueError(f"signed field {path} has an unsupported type {type(v).__name__}")


def canon(obj) -> bytes:
    """Canonical JSON: sorted keys, no spaces, ASCII only (the JS side produces the same bytes)."""
    _check_ascii(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def new_id(prefix: str = "") -> str:
    return prefix + b64e(os.urandom(12))


def new_key() -> bytes:
    return os.urandom(32)


def now() -> int:
    return int(time.time())


# ---------------------------------------------------------------- device keys

class Device:
    """A device's two key pairs. The private halves never leave the device."""

    def __init__(self, x_sk: bytes | None = None, ed_seed: bytes | None = None, device_id: str | None = None):
        self.x = PrivateKey(x_sk) if x_sk else PrivateKey.generate()
        self.ed = SigningKey(ed_seed) if ed_seed else SigningKey.generate()
        self.id = device_id or new_id("d_")

    @property
    def x_pk(self) -> str:
        return b64e(bytes(self.x.public_key))

    @property
    def ed_pk(self) -> str:
        return b64e(bytes(self.ed.verify_key))

    def public(self) -> dict:
        return {"id": self.id, "x": self.x_pk, "ed": self.ed_pk}

    def secret(self) -> dict:
        return {"id": self.id, "x_sk": b64e(bytes(self.x)), "ed_seed": b64e(bytes(self.ed))}

    @classmethod
    def from_secret(cls, d: dict) -> "Device":
        return cls(b64d(d["x_sk"]), b64d(d["ed_seed"]), d["id"])

    def sign(self, msg: bytes) -> str:
        return b64e(self.ed.sign(msg).signature)

    def unseal(self, sealed_b64: str) -> bytes:
        return SealedBox(self.x).decrypt(b64d(sealed_b64))


def verify(ed_pk: str, msg: bytes, sig: str) -> bool:
    try:
        VerifyKey(b64d(ed_pk)).verify(msg, b64d(sig))
        return True
    except Exception:  # noqa: BLE001 - any failure is "not verified"
        return False


def seal(x_pk: str, data: bytes) -> str:
    return b64e(SealedBox(PublicKey(b64d(x_pk))).encrypt(data))


def fingerprint(x_pk: str, ed_pk: str) -> str:
    return b64e(hashlib.blake2b(b"room-fp|" + b64d(x_pk) + b64d(ed_pk), digest_size=16).digest())


# ---------------------------------------------------------------- symmetric

def aead_encrypt(key: bytes, plaintext: bytes, aad: bytes) -> str:
    nonce = os.urandom(nb.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES)
    ct = nb.crypto_aead_xchacha20poly1305_ietf_encrypt(plaintext, aad, nonce, key)
    return b64e(nonce + ct)


def aead_decrypt(key: bytes, blob: str | bytes, aad: bytes) -> bytes:
    raw = b64d(blob) if isinstance(blob, str) else blob
    n = nb.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES
    return nb.crypto_aead_xchacha20poly1305_ietf_decrypt(raw[n:], aad, raw[:n], key)


def encrypt_chunk(key: bytes, data: bytes, file_id: str, index: int, count: int) -> bytes:
    """One file chunk; its position and the chunk count are bound in, so chunks can't be reordered or dropped."""
    aad = canon({"f": file_id, "i": index, "n": count, "v": VERSION})
    return b64d(aead_encrypt(key, data, aad))


def decrypt_chunk(key: bytes, blob: bytes, file_id: str, index: int, count: int) -> bytes:
    return aead_decrypt(key, blob, canon({"f": file_id, "i": index, "n": count, "v": VERSION}))


# ---------------------------------------------------------------- items

def seal_item(header: dict, payload, space_keys: dict, device: Device) -> dict:
    """A signed, encrypted item that can belong to several spaces (a board note shared with cast and crew, say).

    header: ASCII fields (id, kind, prod, ref, subject, ts...). space_keys: {space_id: (epoch, key)}.
    The payload is encrypted once under a fresh item key; that key is encrypted under each space's key, so anyone
    who can read any one of the spaces can read the item, and nobody else."""
    item_key = new_key()
    h = dict(header, v=VERSION, by=device.id, spaces=sorted([s, e] for s, (e, _) in space_keys.items()))
    pt = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ct = aead_encrypt(item_key, pt, canon(h))
    keys = {s: aead_encrypt(k, item_key, canon({"item": h["id"], "space": s, "epoch": e})) for s, (e, k) in space_keys.items()}
    it = {"h": h, "ct": ct, "keys": keys}
    it["sig"] = device.sign(item_signed_bytes(it))
    return it


def item_signed_bytes(item: dict) -> bytes:
    return canon(item["h"]) + b"|" + item["ct"].encode("ascii") + b"|" + canon(item["keys"])


def verify_item(item: dict, ed_pk: str) -> bool:
    return verify(ed_pk, item_signed_bytes(item), item["sig"])


def open_item(item: dict, space: str, key: bytes):
    """Decrypt with one space's key. Raises if the key is wrong or anything was altered."""
    epoch = dict((s, e) for s, e in item["h"]["spaces"])[space]
    item_key = aead_decrypt(key, item["keys"][space], canon({"item": item["h"]["id"], "space": space, "epoch": epoch}))
    return json.loads(aead_decrypt(item_key, item["ct"], canon(item["h"])).decode("utf-8"))


def file_key_for(item_payload: dict) -> bytes:
    return b64d(item_payload["file_key"])


# ---------------------------------------------------------------- key wraps

def wrap_key(key: bytes, space: str, epoch: int, recipient: dict, wrapper: Device) -> dict:
    """recipient: {'id','x'}. The sealed box holds the key plus where it belongs, so a wrap can't be replayed elsewhere."""
    inner = canon({"space": space, "epoch": epoch, "device": recipient["id"]}) + b"|" + key
    w = {"space": space, "epoch": epoch, "device": recipient["id"], "sealed": seal(recipient["x"], inner),
         "by": wrapper.id}
    w["sig"] = wrapper.sign(wrap_signed_bytes(w))
    return w


def wrap_signed_bytes(w: dict) -> bytes:
    return canon({k: w[k] for k in ("space", "epoch", "device", "sealed", "by")})


def unwrap_key(w: dict, me: Device) -> bytes:
    inner = me.unseal(w["sealed"])                 # canonical header, "|", then the 32-byte key
    head, sep, key = inner[:-33], inner[-33:-32], inner[-32:]
    if sep != b"|" or json.loads(head) != {"space": w["space"], "epoch": w["epoch"], "device": me.id}:
        raise ValueError("key wrap is for another space, epoch or device")
    return key


# ---------------------------------------------------------------- device records and trust

def device_record(dev_public: dict, user: str, approver: Device, ts: int | None = None) -> dict:
    r = {"t": "device", "id": dev_public["id"], "user": user, "x": dev_public["x"], "ed": dev_public["ed"],
         "by": approver.id, "ts": ts or now()}
    return {"r": r, "sig": approver.sign(canon(r))}


def exec_grant(user: str, on: bool, by: Device, ts: int | None = None) -> dict:
    r = {"t": "exec", "user": user, "on": bool(on), "by": by.id, "ts": ts or now()}
    return {"r": r, "sig": by.sign(canon(r))}


def revocation(device_id: str, by: Device, ts: int | None = None) -> dict:
    r = {"t": "revoke", "device": device_id, "by": by.id, "ts": ts or now()}
    return {"r": r, "sig": by.sign(canon(r))}


def trusted_devices(founder: dict, records: list[dict], grants: list[dict], revokes: list[dict]) -> dict:
    """Devices this client can trust, by id -> record. founder: the founder device's signed record (self-signed),
    already pinned by the safety words. A device counts when its record is signed by a trusted device whose user is
    an executive (the founder's user always is). Revocations signed by a trusted executive device remove a device;
    the devices it approved earlier stay trusted."""
    f = founder["r"]
    if f["by"] != f["id"] or not verify(f["ed"], canon(f), founder["sig"]):
        raise ValueError("founder record is not self-signed")
    trusted = {f["id"]: f}
    execs = {f["user"]: True}
    pending_r, pending_g = list(records), sorted(grants, key=lambda g: g["r"]["ts"])
    changed = True
    while changed:
        changed = False
        for g in list(pending_g):
            r, by = g["r"], trusted.get(g["r"]["by"])
            if by and execs.get(by["user"]) and verify(by["ed"], canon(r), g["sig"]):
                if r["user"] != f["user"]:          # the founder stays an executive
                    execs[r["user"]] = r["on"]
                pending_g.remove(g)
                changed = True
        for rec in list(pending_r):
            r, by = rec["r"], trusted.get(rec["r"]["by"])
            if r["id"] in trusted:
                pending_r.remove(rec)
                continue
            if by and execs.get(by["user"]) and verify(by["ed"], canon(r), rec["sig"]):
                trusted[r["id"]] = r
                pending_r.remove(rec)
                changed = True
    for v in revokes:
        r, by = v["r"], trusted.get(v["r"]["by"])
        if by and execs.get(by["user"]) and r["device"] != f["id"] and verify(by["ed"], canon(r), v["sig"]):
            trusted.pop(r["device"], None)
    return {"devices": trusted, "execs": {u for u, on in execs.items() if on}}


# ---------------------------------------------------------------- joining: safety words

def commitment(dev_public: dict, nonce: bytes) -> str:
    return b64e(hashlib.blake2b(b"room-commit|" + canon({"x": dev_public["x"], "ed": dev_public["ed"]}) + b"|" + nonce,
                                digest_size=32).digest())


def check_commitment(dev_public: dict, nonce: bytes, c: str) -> bool:
    return commitment(dev_public, nonce) == c


def safety_words(joiner: dict, approver: dict, founder_ed: str, n_joiner: bytes, n_approver: bytes) -> list[str]:
    """Three words both screens show. Both sides compute this from what they saw; they match only if neither side's
    keys, nor the founder's key, were swapped on the way."""
    h = hashlib.blake2b(b"room-sas|" + canon({"j": [joiner["x"], joiner["ed"]], "a": [approver["x"], approver["ed"]],
                                               "f": founder_ed}) + b"|" + n_joiner + b"|" + n_approver,
                        digest_size=32).digest()
    v = int.from_bytes(h[:5], "big") >> 7         # 33 bits
    return [WORDS[(v >> 22) & 2047], WORDS[(v >> 11) & 2047], WORDS[v & 2047]]
