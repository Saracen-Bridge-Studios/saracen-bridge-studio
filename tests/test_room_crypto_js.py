"""The phone app's crypto (room-crypto.js on libsodium.js) against the Python side (room_crypto on PyNaCl), both ways:
signatures, sealed key wraps, items in several spaces, file chunks, device records and trust, commitments and the
safety words. Runs the JS under Node; skipped where Node isn't installed."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

import room_crypto as rc

STATIC = Path(__file__).resolve().parents[1] / "engine" / "room_hub" / "static"
NODE = shutil.which("node")

JS = r"""
const vm = require('vm'), fs = require('fs'), path = require('path');
const dir = process.argv[2], input = JSON.parse(fs.readFileSync(0, 'utf8'));
const ctx = { console, crypto: require('crypto').webcrypto, setTimeout, clearTimeout };   // the vm's own typed arrays only
ctx.window = ctx; ctx.self = ctx; vm.createContext(ctx);
for (const f of ['vendor/libsodium.js', 'vendor/libsodium-wrappers.js']) vm.runInContext(fs.readFileSync(path.join(dir, f), 'utf8'), ctx);
ctx.sodium.ready.then(() => { try {
  vm.runInContext(fs.readFileSync(path.join(dir, 'room-crypto.js'), 'utf8'), ctx);
  const C = ctx.RoomCrypto, out = {};
  const words = fs.readFileSync(path.join(dir, 'words.txt'), 'utf8').split(/\s+/).filter(Boolean);
  // read what Python made
  const me = C.device(input.js_secret);
  out.pub = me.public();
  out.item_ok = C.verifyItem(input.item, input.py_ed);
  out.item_s1 = C.openItem(input.item, 's_1', C.b64d(input.k1));
  out.item_s2 = C.openItem(input.item, 's_2', C.b64d(input.k2));
  out.wrap_ok = C.verify(input.py_ed, C.wrapSigned(input.wrap), input.wrap.sig);
  out.wrap_key = C.b64e(C.unwrapKey(input.wrap, me));
  out.chunk = ctx.sodium.to_string(C.decryptChunk(C.b64d(input.k1), C.b64d(input.chunk), 'f_1', 1, 3));
  out.trust = Object.keys(C.trustedDevices(input.founder, input.records, input.grants, input.revokes).devices).sort();
  out.commit = C.commitment(input.joiner, C.b64d(input.nonce));
  out.words = C.safetyWords(words, input.joiner, input.approver, input.founder_ed, C.b64d(input.nonce), C.b64d(input.nonce2));
  out.canon = ctx.sodium.to_string(C.canon(input.canon_obj));
  // make things for Python to read
  const k = C.newKey();
  out.k = C.b64e(k);
  out.js_item = C.sealItem({ id: 'm_js', kind: 'msg', prod: 'p_1', ts: 5 }, { text: 'Hëllo from JS', n: [1, 2] }, { s_9: [3, k] }, me);
  out.js_wrap = C.wrapKey(k, 's_9', 3, { id: input.py_pub.id, x: input.py_pub.x }, me);
  out.js_record = C.deviceRecord(input.py_pub, 'u_py', me, 7);
  out.js_chunk = C.b64e(C.encryptChunk(k, ctx.sodium.from_string('part two'), 'f_2', 1, 2));
  out.js_sig = me.sign(ctx.sodium.from_string('hello'));
  process.stdout.write(JSON.stringify(out));
} catch (e) { process.stderr.write('JSERROR ' + e.message + ' @ ' + (e.stack || '').split('\n').filter(l => /evalmachine|t\.js/.test(l)).slice(0, 4).join(' | ')); process.exit(1); } });
"""


@pytest.mark.skipif(not NODE, reason="Node isn't installed")
def test_js_and_python_read_each_other(tmp_path):
    py, js = rc.Device(), rc.Device()
    k1, k2 = rc.new_key(), rc.new_key()
    item = rc.seal_item({"id": "m_1", "kind": "note", "prod": "p_1", "ts": 1}, {"title": "Ünïcode ✓", "n": 3},
                        {"s_1": (1, k1), "s_2": (4, k2)}, py)
    e2 = rc.Device()
    founder = rc.device_record(py.public(), "u_f", py)
    records = [rc.device_record(e2.public(), "u_e2", py), rc.device_record(js.public(), "u_js", e2)]
    grants = [rc.exec_grant("u_e2", True, py)]
    n1, n2 = b"\x07" * 32, b"\x09" * 32
    inp = {"js_secret": js.secret(), "py_ed": py.ed_pk, "py_pub": py.public(), "item": item, "k1": rc.b64e(k1),
           "k2": rc.b64e(k2), "wrap": rc.wrap_key(k1, "s_1", 2, js.public(), py),
           "chunk": rc.b64e(rc.encrypt_chunk(k1, b"chunk one", "f_1", 1, 3)), "founder": founder, "records": records,
           "grants": grants, "revokes": [], "joiner": js.public(), "approver": e2.public(), "founder_ed": py.ed_pk,
           "nonce": rc.b64e(n1), "nonce2": rc.b64e(n2), "canon_obj": {"b": [1, None, True], "a": "x/y\"z", "c": {"z": 0, "y": -3}}}
    (tmp_path / "t.js").write_text(JS)
    r = subprocess.run([NODE, str(tmp_path / "t.js"), str(STATIC)], input=json.dumps(inp), capture_output=True, text=True,
                       timeout=120)
    assert r.returncode == 0, r.stderr[r.stderr.find("JSERROR"):][:600]
    out = json.loads(r.stdout)
    # JS reads Python
    assert out["pub"] == js.public()
    assert out["item_ok"] and out["item_s1"] == {"title": "Ünïcode ✓", "n": 3} and out["item_s2"] == out["item_s1"]
    assert out["wrap_ok"] and out["wrap_key"] == rc.b64e(k1) and out["chunk"] == "chunk one"
    assert out["trust"] == sorted([py.id, e2.id, js.id])
    assert out["commit"] == rc.commitment(js.public(), n1)
    assert out["words"] == rc.safety_words(js.public(), e2.public(), py.ed_pk, n1, n2)
    assert out["canon"].encode() == rc.canon(inp["canon_obj"])
    # Python reads JS
    k = rc.b64d(out["k"])
    assert rc.verify_item(out["js_item"], js.ed_pk) and rc.open_item(out["js_item"], "s_9", k) == {"text": "Hëllo from JS", "n": [1, 2]}
    assert rc.unwrap_key(out["js_wrap"], py) == k and rc.verify(js.ed_pk, rc.wrap_signed_bytes(out["js_wrap"]), out["js_wrap"]["sig"])
    assert rc.verify(js.ed_pk, rc.canon(out["js_record"]["r"]), out["js_record"]["sig"])
    assert rc.decrypt_chunk(k, rc.b64d(out["js_chunk"]), "f_2", 1, 2) == b"part two"
    assert rc.verify(js.ed_pk, b"hello", out["js_sig"])
