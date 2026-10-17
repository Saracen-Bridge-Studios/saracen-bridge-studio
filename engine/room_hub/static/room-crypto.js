/* The Room's end-to-end encryption in the browser (1.0.8): the same formats as engine/room_crypto (Python, PyNaCl),
   on libsodium.js (ISC). tests/test_room_crypto_js.py runs this file under Node and checks every format against the
   Python side in both directions. Needs the global `sodium` (libsodium-wrappers), ready. */
(function (root) {
  "use strict";
  const S = () => root.sodium;
  const VERSION = "room-v1";
  const CHUNK = 4 * 1024 * 1024;
  /* libsodium's own UTF-8 helpers, so every byte array is the same realm's Uint8Array (matters in workers and tests) */
  const enc = { encode: x => S().from_string(x) }, dec = { decode: x => S().to_string(x) };
  const b64e = b => S().to_base64(b, S().base64_variants.URLSAFE_NO_PADDING);
  const b64d = s => S().from_base64(s, S().base64_variants.URLSAFE_NO_PADDING);
  const cat = (...parts) => { const n = parts.reduce((a, p) => a + p.length, 0); const out = new Uint8Array(n); let o = 0; for (const p of parts) { out.set(p, o); o += p.length; } return out; };
  const bytes = s => typeof s === "string" ? enc.encode(s) : s;

  function check(v, path) {
    if (v === null || typeof v === "boolean") return;
    if (typeof v === "number") { if (!Number.isInteger(v)) throw new Error(`signed field ${path} must be an integer`); return; }
    if (typeof v === "string") { if (!/^[\x00-\x7f]*$/.test(v)) throw new Error(`signed field ${path} must be ASCII`); return; }
    if (Array.isArray(v)) { v.forEach((x, i) => check(x, `${path}[${i}]`)); return; }
    if (typeof v === "object") { for (const [k, x] of Object.entries(v)) { check(k, path); check(x, `${path}.${k}`); } return; }
    throw new Error(`signed field ${path} has an unsupported type`);
  }
  /* canonical JSON: sorted keys, no spaces, ASCII (matches Python json.dumps(sort_keys, separators, ensure_ascii)) */
  function canonStr(v) {
    if (v === null) return "null";
    if (typeof v === "boolean" || typeof v === "number") return JSON.stringify(v);
    if (typeof v === "string") return JSON.stringify(v).replace(/\x7f/g, "\x7f");
    if (Array.isArray(v)) return "[" + v.map(canonStr).join(",") + "]";
    return "{" + Object.keys(v).sort().map(k => JSON.stringify(k) + ":" + canonStr(v[k])).join(",") + "}";
  }
  function canon(obj) { check(obj, "$"); return enc.encode(canonStr(obj)); }
  const newId = (prefix = "") => prefix + b64e(S().randombytes_buf(12));
  const newKey = () => S().randombytes_buf(32);
  const now = () => Math.floor(Date.now() / 1000);

  /* ---------- devices ---------- */
  function device(secret) {
    const s = S();
    const x_sk = secret ? b64d(secret.x_sk) : s.randombytes_buf(32);
    const ed_seed = secret ? b64d(secret.ed_seed) : s.randombytes_buf(32);
    const ed = s.crypto_sign_seed_keypair(ed_seed);
    const d = { id: secret ? secret.id : newId("d_"), x_sk, x_pk_raw: s.crypto_scalarmult_base(x_sk), ed_seed, ed_sk: ed.privateKey, ed_pk_raw: ed.publicKey };
    d.x_pk = b64e(d.x_pk_raw); d.ed_pk = b64e(d.ed_pk_raw);
    d.public = () => ({ id: d.id, x: d.x_pk, ed: d.ed_pk });
    d.secret = () => ({ id: d.id, x_sk: b64e(x_sk), ed_seed: b64e(ed_seed) });
    d.sign = msg => b64e(s.crypto_sign_detached(msg, d.ed_sk));
    d.unseal = sealed => s.crypto_box_seal_open(b64d(sealed), d.x_pk_raw, d.x_sk);
    return d;
  }
  function verify(ed_pk, msg, sig) { try { return S().crypto_sign_verify_detached(b64d(sig), msg, b64d(ed_pk)); } catch (e) { return false; } }
  const seal = (x_pk, data) => b64e(S().crypto_box_seal(data, b64d(x_pk)));

  /* ---------- symmetric ---------- */
  function aeadEncrypt(key, pt, aad) {
    const s = S(); const nonce = s.randombytes_buf(24);
    return b64e(cat(nonce, s.crypto_aead_xchacha20poly1305_ietf_encrypt(pt, aad, null, nonce, key)));
  }
  function aeadDecrypt(key, blob, aad) {
    const raw = typeof blob === "string" ? b64d(blob) : blob;
    return S().crypto_aead_xchacha20poly1305_ietf_decrypt(null, raw.subarray(24), aad, raw.subarray(0, 24), key);
  }
  const chunkAad = (f, i, n) => canon({ f, i, n, v: VERSION });
  const encryptChunk = (key, data, f, i, n) => b64d(aeadEncrypt(key, data, chunkAad(f, i, n)));
  const decryptChunk = (key, blob, f, i, n) => aeadDecrypt(key, blob, chunkAad(f, i, n));

  /* ---------- items (one or more spaces) ---------- */
  const itemSigned = it => cat(canon(it.h), enc.encode("|" + it.ct + "|"), canon(it.keys));
  function sealItem(header, payload, spaceKeys, dev) {
    const itemKey = newKey();
    const spaces = Object.entries(spaceKeys).map(([s, [e]]) => [s, e]).sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : a[1] - b[1]);
    const h = Object.assign({}, header, { v: VERSION, by: dev.id, spaces });
    const ct = aeadEncrypt(itemKey, enc.encode(JSON.stringify(payload)), canon(h));
    const keys = {};
    for (const [s, [e, k]] of Object.entries(spaceKeys)) keys[s] = aeadEncrypt(k, itemKey, canon({ item: h.id, space: s, epoch: e }));
    const it = { h, ct, keys };
    it.sig = dev.sign(itemSigned(it));
    return it;
  }
  const verifyItem = (it, ed_pk) => verify(ed_pk, itemSigned(it), it.sig);
  function openItem(it, space, key) {
    const epoch = (it.h.spaces.find(x => x[0] === space) || [])[1];
    const itemKey = aeadDecrypt(key, it.keys[space], canon({ item: it.h.id, space, epoch }));
    return JSON.parse(dec.decode(aeadDecrypt(itemKey, it.ct, canon(it.h))));
  }

  /* ---------- key wraps ---------- */
  const wrapSigned = w => canon({ space: w.space, epoch: w.epoch, device: w.device, sealed: w.sealed, by: w.by });
  function wrapKey(key, space, epoch, recipient, wrapper) {
    const inner = cat(canon({ space, epoch, device: recipient.id }), enc.encode("|"), key);
    const w = { space, epoch, device: recipient.id, sealed: seal(recipient.x, inner), by: wrapper.id };
    w.sig = wrapper.sign(wrapSigned(w));
    return w;
  }
  function unwrapKey(w, me) {
    const inner = me.unseal(w.sealed);
    const head = inner.subarray(0, inner.length - 33), sep = inner[inner.length - 33], key = inner.slice(inner.length - 32);
    const want = canonStr({ space: w.space, epoch: w.epoch, device: me.id });
    if (sep !== 124 || canonStr(JSON.parse(dec.decode(head))) !== want) throw new Error("key wrap is for another space, epoch or device");
    return key;
  }

  /* ---------- records and trust ---------- */
  const record = (r, by) => ({ r, sig: by.sign(canon(r)) });
  const deviceRecord = (pub, user, approver, ts) => record({ t: "device", id: pub.id, user, x: pub.x, ed: pub.ed, by: approver.id, ts: ts || now() }, approver);
  const execGrant = (user, on, by, ts) => record({ t: "exec", user, on: !!on, by: by.id, ts: ts || now() }, by);
  const revocation = (device, by, ts) => record({ t: "revoke", device, by: by.id, ts: ts || now() }, by);
  function trustedDevices(founder, records, grants, revokes) {
    const f = founder.r;
    if (f.by !== f.id || !verify(f.ed, canon(f), founder.sig)) throw new Error("founder record is not self-signed");
    const trusted = { [f.id]: f }, execs = { [f.user]: true };
    let pr = [...records], pg = [...grants].sort((a, b) => a.r.ts - b.r.ts), changed = true;
    while (changed) {
      changed = false;
      for (const g of [...pg]) {
        const by = trusted[g.r.by];
        if (by && execs[by.user] && verify(by.ed, canon(g.r), g.sig)) { if (g.r.user !== f.user) execs[g.r.user] = g.r.on; pg = pg.filter(x => x !== g); changed = true; }
      }
      for (const rec of [...pr]) {
        const r = rec.r, by = trusted[r.by];
        if (trusted[r.id]) { pr = pr.filter(x => x !== rec); continue; }
        if (by && execs[by.user] && verify(by.ed, canon(r), rec.sig)) { trusted[r.id] = r; pr = pr.filter(x => x !== rec); changed = true; }
      }
    }
    for (const v of revokes) {
      const r = v.r, by = trusted[r.by];
      if (by && execs[by.user] && r.device !== f.id && verify(by.ed, canon(r), v.sig)) delete trusted[r.device];
    }
    return { devices: trusted, execs: new Set(Object.entries(execs).filter(([, on]) => on).map(([u]) => u)) };
  }

  /* ---------- joining: commitment and safety words ---------- */
  const hash = msg => S().crypto_generichash(32, msg);
  const commitment = (pub, nonce) => b64e(hash(cat(enc.encode("room-commit|"), canon({ x: pub.x, ed: pub.ed }), enc.encode("|"), nonce)));
  function safetyWords(words, joiner, approver, founderEd, nJ, nA) {
    const h = hash(cat(enc.encode("room-sas|"), canon({ j: [joiner.x, joiner.ed], a: [approver.x, approver.ed], f: founderEd }), enc.encode("|"), nJ, enc.encode("|"), nA));
    const v = Math.floor((((h[0] * 256 + h[1]) * 256 + h[2]) * 256 + h[3]) * 2 + Math.floor(h[4] / 128));   /* the first 33 bits */
    return [words[Math.floor(v / 4194304) % 2048], words[Math.floor(v / 2048) % 2048], words[v % 2048]];
  }

  root.RoomCrypto = { VERSION, CHUNK, b64e, b64d, canon, canonStr, newId, newKey, now, device, verify, seal, aeadEncrypt, aeadDecrypt,
    encryptChunk, decryptChunk, sealItem, verifyItem, openItem, wrapKey, unwrapKey, wrapSigned, deviceRecord, execGrant, revocation,
    trustedDevices, commitment, safetyWords, randomBytes: n => S().randombytes_buf(n) };
})(typeof window !== "undefined" ? window : globalThis);
