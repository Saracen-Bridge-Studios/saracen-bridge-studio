"use strict";
/* The Room on a phone (1.0.8): crew and cast see their own day, the board, chat and meetings. Served by the hub as an
   installable web app. Every key stays on this phone; the hub only ever sees ciphertext (room-crypto.js). */
const C = window.RoomCrypto;
const $app = () => document.getElementById("app");
function el(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") e.className = v; else if (k === "style") e.style.cssText = v;
    else if (k.startsWith("on") && typeof v === "function") e.addEventListener(k.slice(2).toLowerCase(), v);
    else e.setAttribute(k, v === true ? "" : String(v));
  }
  for (const k of kids.flat(Infinity)) if (k !== null && k !== undefined && k !== false) e.append(k instanceof Node ? k : document.createTextNode(String(k)));
  return e;
}
const put = (n, ...kids) => { n.replaceChildren(...kids.flat(Infinity).filter(k => k !== null && k !== undefined && k !== false)); return n; };
function toast(text, sub) {
  const t = el("div", { class: "toast", role: "status" }, el("b", {}, text), sub ? el("div", {}, sub) : null);
  document.getElementById("toasts").append(t); setTimeout(() => t.remove(), 4500);
}
const hhmm = ts => new Date(ts * 1000).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
const dayLbl = ts => { const d = new Date(ts * 1000), n = new Date(); if (d.toDateString() === n.toDateString()) return "TODAY"; const y = new Date(n - 864e5); if (d.toDateString() === y.toDateString()) return "YESTERDAY"; return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" }).toUpperCase(); };
const ini = n => (n || "?").split(/\s+/).map(x => x[0]).slice(0, 2).join("").toUpperCase();
const bytesTxt = n => n < 1048576 ? `${Math.max(1, Math.round(n / 1024))} KB` : n < 1073741824 ? `${(n / 1048576).toFixed(1)} MB` : `${(n / 1073741824).toFixed(2)} GB`;
const TIERS = { executive: "Executive", producer: "Producer", key: "Key personnel", crew: "Crew", cast: "Cast", guest: "Guest" };

/* ---------------- storage: IndexedDB (ciphertext items and key wraps; the device keys; production names for notifications) ---------------- */
const DB = {
  db: null,
  open() { return new Promise((res, rej) => { const r = indexedDB.open("room", 1);
    r.onupgradeneeded = () => ["kv", "items", "wraps", "names"].forEach(s => r.result.objectStoreNames.contains(s) || r.result.createObjectStore(s));
    r.onsuccess = () => { DB.db = r.result; res(); }; r.onerror = () => rej(r.error); }); },
  tx(store, mode, fn) { return new Promise((res, rej) => { const t = DB.db.transaction(store, mode); const s = t.objectStore(store); const out = fn(s); t.oncomplete = () => res(out && out.result !== undefined ? out.result : out); t.onerror = () => rej(t.error); }); },
  get(store, k) { return new Promise((res, rej) => { const r = DB.db.transaction(store).objectStore(store).get(k); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); }); },
  set(store, k, v) { return DB.tx(store, "readwrite", s => s.put(v, k)); },
  del(store, k) { return DB.tx(store, "readwrite", s => s.delete(k)); },
  all(store) { return new Promise((res, rej) => { const r = DB.db.transaction(store).objectStore(store).getAll(); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); }); },
  clear() { return Promise.all(["kv", "items", "wraps", "names"].map(s => DB.tx(s, "readwrite", st => st.clear()))); },
};

/* ---------------- the client ---------------- */
const R = { dev: null, st: {}, snap: {}, keys: new Map(), items: new Map(), trustEver: { devices: {} }, trustNow: { devices: {} }, words: [], token: null, prod: null, tab: "today", chat: null };
const kk = (s, e) => `${s}|${e}`;
async function saveState() { await DB.set("kv", "state", R.st); }

async function api(method, path, body, raw) {
  const headers = {};
  if (!raw || raw.auth !== false) headers.Authorization = "Bearer " + await bearer();
  let payload;
  if (body instanceof Uint8Array) { payload = body; headers["Content-Type"] = "application/octet-stream"; }
  else if (body !== undefined) { payload = JSON.stringify(body); headers["Content-Type"] = "application/json"; }
  let r = await fetch(path, { method, headers, body: payload });
  if (r.status === 401 && (!raw || raw.auth !== false)) { R.token = null; headers.Authorization = "Bearer " + await bearer(); r = await fetch(path, { method, headers, body: payload }); }
  if (!r.ok) { let msg = r.statusText; try { msg = (await r.json()).detail || msg; } catch (e) { /* not JSON */ } throw new Error(msg); }
  return (r.headers.get("content-type") || "").startsWith("application/json") ? r.json() : new Uint8Array(await r.arrayBuffer());
}
async function bearer() {
  if (R.token && R.token[1] > Date.now() + 60000) return R.token[0];
  if (R.signing) return R.signing;                       /* one sign-in at a time; everyone else waits for it */
  R.signing = signIn().finally(() => { R.signing = null; });
  return R.signing;
}
async function signIn() {
  const ch = (await api("POST", "/api/auth/challenge", { device: R.dev.id }, { auth: false })).challenge;
  const t = await api("POST", "/api/auth/token", { device: R.dev.id, challenge: ch, sig: R.dev.sign(C.canon({ t: "auth", device: R.dev.id, challenge: ch })) }, { auth: false });
  R.token = [t.token, Date.now() + t.expires_in * 1000];
  if (t.status !== R.st.status) { R.st.status = t.status; await saveState(); }
  return t.token;
}

function computeTrust() {
  if (!R.st.founder || !R.snap.devices) return;
  if (R.snap.founder && JSON.stringify(R.snap.founder) !== JSON.stringify(R.st.founder)) throw new Error("The Room's root key doesn't match the one this phone trusts. Stop and tell an executive.");
  const recs = R.snap.devices.map(d => d.record);
  R.trustEver = C.trustedDevices(R.st.founder, recs, R.snap.exec_grants || [], []);
  R.trustNow = C.trustedDevices(R.st.founder, recs, R.snap.exec_grants || [], R.snap.revocations || []);
}
function takeWrap(w) {
  const by = R.trustEver.devices[w.by];
  if (!by || !C.verify(by.ed, C.wrapSigned(w), w.sig)) return false;
  try { R.keys.set(kk(w.space, w.epoch), C.unwrapKey(w, R.dev)); return true; } catch (e) { return false; }
}
function takeItem(it) {
  const by = R.trustEver.devices[it.h.by];
  if (!by || !C.verifyItem(it, by.ed)) return;
  let payload = null;
  for (const [s, e] of it.h.spaces) { const k = R.keys.get(kk(s, e)); if (k) { try { payload = C.openItem(it, s, k); break; } catch (err) { /* next */ } } }
  R.items.set(it.h.id, { h: it.h, seq: it.seq || 0, payload, author: by.user, raw: it });
}
async function loadCache() {
  R.snap = (await DB.get("kv", "snapshot")) || {};
  computeTrust();
  for (const w of await DB.all("wraps")) takeWrap(w);
  for (const it of (await DB.all("items")).sort((a, b) => (a.seq || 0) - (b.seq || 0))) takeItem(it);
}
async function sync() {
  const since = R.snap && R.snap.seq ? R.st.seq || 0 : 0;
  const s = await api("GET", `/api/sync?since=${since}`);
  const notes = since ? ((await DB.get("kv", "notes")) || []) : [];
  R.snap = Object.assign({}, s); delete R.snap.items; delete R.snap.wraps; delete R.snap.deleted;
  R.snap.notifications = notes.concat(s.notifications).slice(-300);
  await DB.set("kv", "notes", R.snap.notifications);
  computeTrust();
  for (const w of s.wraps) if (takeWrap(w)) await DB.set("wraps", kk(w.space, w.epoch), w);
  for (const it of s.items) { takeItem(it); await DB.set("items", it.h.id, it); }
  if (s.wraps.length) for (const r of R.items.values()) if (r.payload === null) takeItem(r.raw);
  for (const id of s.deleted) { R.items.delete(id); await DB.del("items", id); }
  const visible = new Set(s.spaces.map(x => x.id));
  for (const [id, it] of R.items) if (!it.h.spaces.some(([sp]) => visible.has(sp))) { R.items.delete(id); await DB.del("items", id); }
  await DB.set("kv", "snapshot", R.snap);
  R.st.seq = s.seq; await saveState();
  for (const p of s.productions) { const n = names(p.id).production[p.id]; if (n && n.name) await DB.set("names", p.id, n.name); }
  await upkeep();
}
/* keys this phone holds, for devices entitled to them (a conversation you started, say) */
async function upkeep() {
  const t = R.snap.tasks || {};
  const wraps = [];
  for (const task of t.wrap || []) {
    const rec = R.trustNow.devices[task.device], key = R.keys.get(kk(task.space, task.epoch));
    if (rec && rec.user === task.user && key) wraps.push(C.wrapKey(key, task.space, task.epoch, { id: rec.id, x: rec.x }, R.dev));
  }
  for (let i = 0; i < wraps.length; i += 200) await api("POST", "/api/wraps", { wraps: wraps.slice(i, i + 200) }).catch(() => null);
  for (const r of t.rotate || []) {
    const sp = space(r.space); if (!sp || sp.kind !== "dm") continue;
    const key = C.newKey(), e = sp.epoch + 1, w = C.wrapKey(key, sp.id, e, R.dev.public(), R.dev);
    try { await api("POST", `/api/spaces/${sp.id}/rotate`, { epoch: e, wraps: [w] }); R.keys.set(kk(sp.id, e), key); await DB.set("wraps", kk(sp.id, e), w); } catch (err) { /* someone else did it */ }
  }
}

/* ---------------- lookups ---------------- */
const space = id => (R.snap.spaces || []).find(s => s.id === id);
function names(p) {
  const out = { production: {}, space: {}, department: {}, person: {} };
  for (const it of [...R.items.values()].sort((a, b) => a.seq - b.seq)) if (it.h.prod === p && out[it.h.kind] && it.payload) out[it.h.kind][it.h.subject] = it.payload;
  return out;
}
function people(p) {
  const n = names(p), out = {};
  for (const x of R.snap.people || []) if (x.production === p) {
    const info = n.person[x.user] || {};
    out[x.user] = { user: x.user, name: info.name || "Someone", role: info.role || "", tier: x.tier, second_ad: x.second_ad, can_reach: x.can_reach,
      department: x.department ? ((n.department[x.department] || {}).name || "") : "" };
  }
  return out;
}
const myTier = p => !R.snap.me ? "" : R.snap.me.exec ? "executive" : ((R.snap.me.memberships || []).find(m => m.production === p) || {}).tier || "";
function spaceName(sp, ppl, n) {
  if (sp.kind === "dm") { const o = sp.members.filter(u => u !== R.st.user); return o.length === 1 ? (ppl[o[0]] || {}).name || "Private conversation" : o.map(u => (ppl[u] || {}).name).join(" ↔ "); }
  if (sp.kind === "personal") return sp.owner === R.st.user ? "My day" : `${(ppl[sp.owner] || {}).name || "Someone"}'s day`;
  return (n.space[sp.id] || {}).name || "Space";
}
function currentKey(sid) { const sp = space(sid); const k = sp && R.keys.get(kk(sid, sp.epoch)); if (!k) throw new Error("This phone doesn't have that space's key yet. Pull down to refresh in a moment."); return [sp.epoch, k]; }
async function post(spaces, kind, payload, extra = {}) {
  const keys = {}; for (const s of spaces) keys[s] = currentKey(s);
  const h = Object.assign({ id: C.newId("m_"), kind, prod: space(spaces[0]).production, ts: C.now() }, extra.ref ? { ref: extra.ref } : {});
  const it = C.sealItem(h, payload, keys, R.dev);
  const r = await api("POST", "/api/items", { item: it, mentions: extra.mentions || [] });
  it.seq = r.seq; takeItem(it); await DB.set("items", h.id, it);
  return R.items.get(h.id);
}

/* ---------------- call sheets: my day ---------------- */
function today(p) {
  const sheets = {};
  for (const it of R.items.values()) if (it.h.kind === "callsheet" && it.h.prod === p && it.payload) (sheets[it.payload.lineage] = sheets[it.payload.lineage] || []).push(Object.assign({ item: it.h.id, seq: it.seq, ts: it.h.ts }, it.payload));
  let latest = Object.values(sheets).map(v => v.sort((a, b) => b.version - a.version)[0]);
  if (!latest.length) return null;
  const mine = latest.filter(x => (x.people || []).includes(R.st.user));     /* the sheets you're on come first */
  if (mine.length) latest = mine;
  const d = new Date().toISOString().slice(0, 10);
  const s = latest.filter(x => x.date && x.date >= d).sort((a, b) => a.date < b.date ? -1 : a.date > b.date ? 1 : b.seq - a.seq)[0] || latest.sort((a, b) => b.seq - a.seq)[0];
  let row = null;
  for (const it of [...R.items.values()].sort((a, b) => a.seq - b.seq)) if (it.h.kind === "callsheet_row" && it.payload && it.payload.lineage === s.lineage && it.payload.version === s.version && it.payload.user === R.st.user) row = it.payload;
  const confirmed = (R.snap.confirmations || []).some(c => c.item === s.item && c.user === R.st.user);
  return Object.assign({}, s, { row, confirmed, onSheet: (s.people || []).includes(R.st.user) });
}

/* ---------------- screens ---------------- */
async function boot() {
  try { await window.sodium.ready; } catch (e) { put($app(), el("p", { class: "boot" }, "This browser can't run the Room's encryption.")); return; }
  R.words = (await (await fetch("/app/words.txt")).text()).split(/\s+/).filter(Boolean);
  await DB.open();
  R.st = (await DB.get("kv", "state")) || {};
  const secret = await DB.get("kv", "device");
  if (secret) R.dev = C.device(secret);
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/app/sw.js").catch(() => null);
  const join = /[#?&]join=([A-Za-z0-9_-]+)/.exec(location.hash + location.search);
  if (join && R.st.status !== "approved") return joinScreen(join[1]);
  if (!R.dev || !R.st.status) return put($app(), el("div", { class: "intro" }, el("img", { src: "/app/icons/icon-192.png", alt: "", class: "logo" }), el("h1", {}, "The Room"),
    el("p", {}, "Open the invite link you were sent on this phone to join your production.")));
  if (R.st.status === "pending") return wordsScreen();
  await loadCache().catch(() => null);
  home();
  sync().then(home).catch(e => toast("Couldn't refresh", e.message));
  live();
}

function isIOS() { return /iPhone|iPad|iPod/.test(navigator.userAgent); }
function standalone() { return matchMedia("(display-mode: standalone)").matches || navigator.standalone === true; }

function joinScreen(token) {
  const name = el("input", { type: "text", autocomplete: "name", placeholder: "Your name", "aria-label": "Your name" });
  put($app(), el("div", { class: "intro" }, el("img", { src: "/app/icons/icon-192.png", alt: "", class: "logo" }), el("h1", {}, "Join the Room"),
    el("p", {}, "Your production's private, encrypted hub: your day, the board, chat and meetings."),
    isIOS() && !standalone() ? el("div", { class: "note" }, el("b", {}, "On iPhone, add it to your home screen first. "), "Notifications only work from the home screen: tap Share, then Add to Home Screen, then open the Room from there and tap the link again.") : null,
    el("label", { class: "f" }, "Your name", name),
    el("button", { type: "button", class: "btn primary big", onclick: async ev => {
      ev.currentTarget.disabled = true;
      try {
        R.dev = C.device(); await DB.set("kv", "device", R.dev.secret());
        const nonce = C.randomBytes(32);
        const r = await api("POST", "/api/join", { token, device: R.dev.public(), commit: C.commitment(R.dev.public(), nonce) }, { auth: false });
        R.st = { user: r.user, status: "pending", nonce: C.b64e(nonce), joinFounder: r.founder, profile: { name: name.value.trim() } };
        await saveState(); history.replaceState(null, "", "/app/"); wordsScreen();
      } catch (e) { toast("Couldn't join", e.message); ev.currentTarget.disabled = false; }
    } }, "Join"),
    el("p", { class: "muted" }, "Everything is encrypted on this phone before it leaves.")));
}

async function wordsScreen() {
  const box = el("div", { class: "intro" });
  put($app(), box);
  const tick = async () => {
    let s;
    try { s = await api("GET", "/api/join/state"); } catch (e) { put(box, el("h1", {}, "Joining"), el("p", {}, e.message)); return setTimeout(tick, 5000); }
    if (s.status === "approved") return finishJoin(s);
    if (s.status !== "pending") { put(box, el("h1", {}, "Not approved"), el("p", {}, "The invite was declined. Ask for a new one."), el("button", { type: "button", class: "btn", onclick: async () => { await DB.clear(); location.href = "/app/"; } }, "Start again")); return; }
    if (!s.approver) put(box, el("h1", {}, "Waiting for an executive"), el("p", {}, "Call the executive who approves new phones and ask them to press Check next to your name. Your safety words appear here then."));
    else {
      if (!s.revealed) await api("POST", "/api/join/reveal", { nonce: R.st.nonce });
      const w = C.safetyWords(R.words, R.dev.public(), s.approver, R.st.joinFounder.r.ed, C.b64d(R.st.nonce), C.b64d(s.n_approver));
      R.st.joinApprover = s.approver; await saveState();
      put(box, el("h1", {}, "Your safety words"), el("div", { class: "words" }, w.map(x => el("span", {}, x))),
        el("p", {}, "Read these to the executive on the call. If their screen shows the same three words in the same order, they approve this phone."),
        el("p", { class: "muted" }, "If the words are different, say so and stop."));
    }
    setTimeout(tick, 2500);
  };
  tick();
}

async function finishJoin(s) {
  if (JSON.stringify(s.founder) !== JSON.stringify(R.st.joinFounder)) return put($app(), el("div", { class: "intro" }, el("h1", {}, "Stop"), el("p", {}, "The Room's root key changed while joining. Don't use this phone; ask for a new invite.")));
  const a = R.st.joinApprover, rec = s.record;
  if (!a || rec.r.by !== a.id || !C.verify(a.ed, C.canon(rec.r), rec.sig)) return put($app(), el("div", { class: "intro" }, el("h1", {}, "Stop"), el("p", {}, "The approval wasn't signed by the executive you checked words with.")));
  Object.assign(R.st, { status: "approved", founder: s.founder }); delete R.st.nonce; delete R.st.joinFounder; delete R.st.joinApprover;
  await saveState();
  await sync().catch(() => null);
  setupScreen();
}

/* after joining: the oversight notice, notifications, the microphone */
function setupScreen() {
  const meter = el("div", { class: "meter", role: "img", "aria-label": "Microphone level" }, Array.from({ length: 16 }, () => el("span")));
  put($app(), el("div", { class: "intro" }, el("h1", {}, "You're in"),
    el("div", { class: "note" }, el("b", {}, "Oversight. "), "Executives on this production can read every space, file and private message in the Room. Every read is recorded in the audit log."),
    el("button", { type: "button", class: "btn big", onclick: async ev => { const ok = await enablePush(); ev.currentTarget.textContent = ok ? "Notifications on" : "Notifications not available"; ev.currentTarget.disabled = true; } }, "Turn on notifications"),
    isIOS() && !standalone() ? el("p", { class: "muted" }, "On iPhone, notifications work once the Room is on your home screen.") : null,
    el("button", { type: "button", class: "btn big", onclick: async ev => { const ok = await micCheck(meter); ev.currentTarget.textContent = ok ? "Microphone found" : "Microphone blocked"; } }, "Check my microphone"), meter,
    el("button", { type: "button", class: "btn primary big", onclick: () => { home(); live(); } }, "Open the Room")));
}
async function enablePush() {
  try {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) return false;
    if ((await Notification.requestPermission()) !== "granted") return false;
    const { key } = await api("GET", "/api/push/key");
    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: C.b64d(key) });
    await api("POST", "/api/push/subscribe", { subscription: sub.toJSON() });
    return true;
  } catch (e) { return false; }
}
async function micCheck(meter) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: { deviceId: "default", noiseSuppression: true, echoCancellation: true } });
    const ctx = new AudioContext(), an = ctx.createAnalyser(); an.fftSize = 512; ctx.createMediaStreamSource(stream).connect(an);
    const buf = new Uint8Array(512); let level = 0, n = 0;
    const tick = () => { an.getByteTimeDomainData(buf); let pk = 0; for (const v of buf) pk = Math.max(pk, Math.abs(v - 128));
      level += (Math.min(1, pk / 64) - level) * 0.3; [...meter.children].forEach((b, i) => b.classList.toggle("on", i / 16 < level));
      if (++n < 90) setTimeout(tick, 66); else { stream.getTracks().forEach(t => t.stop()); ctx.close(); } };
    tick(); return true;
  } catch (e) { return false; }
}

/* ---------------- home: Today / Board / Chat / Meet ---------------- */
function home() {
  const prods = (R.snap.productions || []).filter(p => !p.archived);
  if (!prods.length) return put($app(), el("div", { class: "intro" }, el("h1", {}, "The Room"), el("p", {}, "You aren't on a production yet.")));
  if (!R.prod || !prods.some(p => p.id === R.prod)) R.prod = R.st.prod && prods.some(p => p.id === R.st.prod) ? R.st.prod : prods[0].id;
  const p = R.prod, n = names(p), ppl = people(p), tier = myTier(p), cast = tier === "cast";
  const me = ppl[R.st.user] || { name: (R.st.profile || {}).name || "You" };
  const tabs = [["today", cast ? "My day" : "Today"], ["board", "Board"], ["chat", "Chat"], ["meet", "Meet"]];
  const body = el("main", { class: "body" });
  put($app(),
    el("header", { class: "top" },
      el("button", { type: "button", class: "prod", "aria-label": "Switch production", onclick: () => prodSheet(prods) }, (n.production[p] || {}).name || "Production", " ▾"),
      cast ? el("span", { class: "tag" }, "CAST") : el("span", { class: "enc" }, "ENCRYPTED"),
      el("span", { class: "grow" }), el("span", { class: "av" }, ini(me.name))),
    body,
    el("nav", { class: "tabs", "aria-label": "App" }, tabs.map(([id, label]) => el("button", { type: "button", "aria-pressed": String(R.tab === id), onclick: () => { R.tab = id; R.chat = null; home(); } }, label))));
  ({ today: todayTab, board: boardTab, chat: chatTab, meet: meetTab })[R.tab](body, p, ppl, n, tier);
}
function prodSheet(prods) {
  const sheet = el("div", { class: "sheet", role: "dialog", "aria-label": "Productions" }, el("h2", {}, "Your productions"),
    prods.map(x => el("button", { type: "button", class: "row-btn", "aria-pressed": String(x.id === R.prod), onclick: async () => { R.prod = x.id; R.st.prod = x.id; await saveState(); sheet.remove(); home(); } }, (names(x.id).production[x.id] || {}).name || "Production")),
    el("button", { type: "button", class: "btn", onclick: () => sheet.remove() }, "Close"));
  document.body.append(sheet);
}

function todayTab(body, p, ppl, n, tier) {
  const cs = today(p);
  if (!cs) return put(body, el("p", { class: "muted pad" }, "No call sheet yet. It appears here when the production office publishes one."));
  const row = cs.row || {};
  const cast = tier === "cast";
  const big = cast ? row.pickup : row.call;
  const steps = [["Pickup", row.pickup, row.driver ? `Driver: ${row.driver}` : "Your driver texts when outside", row.pickup_address], ["Hair and make-up", row.hmu], ["Costume", row.costume], ["On set", row.on_set]].filter(s => s[1]);
  const full = el("div", { class: "card", hidden: true }, el("div", { class: "lbl" }, "Call sheet"),
    el("p", {}, `Unit call ${cs.unit_call} · v${cs.version}`), cs.weather_cover ? el("p", {}, `Weather cover: ${cs.weather_cover}`) : null,
    cs.base ? el("p", {}, `Base and parking: ${cs.base}`) : null, cs.hospital ? el("p", {}, `Nearest hospital: ${cs.hospital}`) : null,
    cs.notes ? el("p", { class: "pre" }, cs.notes) : null,
    cs.pdf ? el("button", { type: "button", class: "btn", onclick: () => openFile(cs.pdf.id) }, `Open ${cs.pdf.name}`) : null);
  put(body,
    el("div", { class: "eyebrow" }, `${cs.date && cs.date !== new Date().toISOString().slice(0, 10) ? "COMING UP" : "TODAY"} · ${cs.day.toUpperCase()} · CALL SHEET v${cs.version}`),
    el("div", { class: "hero" }, el("span", { class: "time" }, big || cs.unit_call), el("span", { class: "muted" }, big ? (cast ? "pickup" : "your call") : "unit call")),
    el("div", { class: "muted small" }, cast ? (row.driver ? `Driver: ${row.driver}${row.pickup_address ? " · from " + row.pickup_address : ""}` : "") : `Unit call ${cs.unit_call}${(ppl[R.st.user] || {}).department ? " · " + ppl[R.st.user].department : ""} · posted ${hhmm(cs.ts)}`),
    cast && steps.length ? el("div", { class: "card" }, steps.map(([w, t, extra]) => el("div", { class: "step" }, el("span", { class: "t" }, t), el("span", {}, el("b", {}, w), extra ? el("small", {}, extra) : null)))) : null,
    !cast ? el("div", { class: "card" }, el("div", { class: "lbl" }, "Location"), el("b", {}, cs.location || "—"),
      cs.weather_cover ? el("div", { class: "muted small" }, `Weather cover: ${cs.weather_cover}`) : null,
      el("div", { class: "row" }, cs.location ? el("a", { class: "btn", href: `https://maps.google.com/?q=${encodeURIComponent(cs.location)}`, target: "_blank", rel: "noopener" }, "Directions") : null,
        el("button", { type: "button", class: "btn", onclick: () => { full.hidden = !full.hidden; } }, "Full call sheet"))) : null,
    el("div", { class: "card" }, el("div", { class: "lbl" }, cast ? "Your scenes" : "Scenes today"),
      (cs.scenes || []).map(s => el("div", { class: "scene" }, el("span", { class: "no" }, s.no), el("span", {}, el("b", {}, s.slug), el("small", {}, [s.pages ? `${s.pages} pages` : "", s.note].filter(Boolean).join(" · "))))),
      cast ? el("div", { class: "row" }, el("button", { type: "button", class: "btn", onclick: () => { R.tab = "chat"; R.chat = sidesSpace(p); home(); } }, "Open sides"),
        el("button", { type: "button", class: "btn", onclick: () => message2ndAD(p, ppl) }, "Message 2nd AD")) : null),
    full,
    cs.onSheet ? el("button", { type: "button", class: "btn " + (cs.confirmed ? "done" : "primary") + " big", "aria-pressed": String(cs.confirmed), disabled: cs.confirmed, onclick: async () => {
      try { await api("POST", "/api/confirm", { item: cs.item, version: cs.version }); await sync(); home(); } catch (e) { toast("Couldn't confirm", e.message); } } },
      cs.confirmed ? `Confirmed: ${cast ? "pickup at " + (row.pickup || cs.unit_call) : "see you at " + (row.call || cs.unit_call)}` : cast ? "Got it, I'll be ready" : "Got it, I'll be there") : null,
    el("p", { class: "muted small center" }, cast ? "Only you and the production office see your pickup details." : cs.confirmed ? "The production office can see you've confirmed." : `Tap to let the production office know you've seen v${cs.version}.`));
}
function sidesSpace(p) { const sp = (R.snap.spaces || []).find(s => s.production === p && s.kind === "personal" && s.owner === R.st.user); return sp ? sp.id : null; }
async function message2ndAD(p, ppl) {
  const ad = Object.values(ppl).find(x => x.second_ad && x.can_reach);
  if (!ad) return toast("No 2nd AD to message yet");
  try { R.chat = await startDM(p, ad.user); R.tab = "chat"; home(); } catch (e) { toast("Couldn't start the conversation", e.message); }
}
async function startDM(p, user) {
  const existing = (R.snap.spaces || []).find(s => s.kind === "dm" && s.production === p && s.members.includes(user) && s.members.includes(R.st.user));
  if (existing) return existing.id;
  const sid = C.newId("s_"), key = C.newKey(), w = C.wrapKey(key, sid, 1, R.dev.public(), R.dev);
  const r = await api("POST", "/api/spaces", { id: sid, production: p, kind: "dm", audience: {}, members: [R.st.user, user], owner: null, wraps: [w] });
  if (r.existing) return r.id;
  R.keys.set(kk(sid, 1), key); await DB.set("wraps", kk(sid, 1), w);
  if (!(R.st.oversightDM)) { toast("Oversight", "Executives can read private messages too, and every read is logged."); R.st.oversightDM = true; await saveState(); }
  await sync();
  return sid;
}

function boardTab(body, p, ppl, n) {
  const upd = {};
  for (const it of [...R.items.values()].sort((a, b) => a.seq - b.seq)) if (it.h.kind === "note_update" && it.payload) upd[it.h.ref] = Object.assign(upd[it.h.ref] || {}, it.payload);
  const sname = Object.fromEntries((R.snap.spaces || []).map(s => [s.id, spaceName(s, ppl, n)]));
  const notes = [...R.items.values()].filter(it => it.h.kind === "note" && it.h.prod === p && it.payload).map(it => Object.assign({ id: it.h.id, ts: it.h.ts, seq: it.seq, author: (ppl[it.author] || {}).name || "Someone", spaces: it.h.spaces.map(([s]) => sname[s]).filter(Boolean) }, it.payload, upd[it.h.id] || {}))
    .sort((a, b) => (!!b.pinned - !!a.pinned) || b.seq - a.seq);
  put(body, el("div", { class: "eyebrow" }, "PRODUCTION BOARD"), el("h1", {}, "What you need to know"),
    notes.length ? notes.map(x => el("article", { class: "note" + (x.pinned ? " pinned" : "") }, el("div", { class: "meta" }, el("span", {}, x.spaces.join(" · ").toUpperCase()), el("span", {}, dayLbl(x.ts))),
      el("h3", {}, x.title), x.body ? el("p", {}, x.body) : null, el("div", { class: "meta" }, el("span", { class: "status" }, x.status || "Open"), el("span", {}, x.author))))
      : el("p", { class: "muted" }, "Nothing on the board yet."));
}

function chatTab(body, p, ppl, n) {
  const spaces = (R.snap.spaces || []).filter(s => s.production === p && s.member && (s.kind === "channel" || s.kind === "dm" || (s.kind === "personal" && s.owner === R.st.user)));
  if (!R.chat || !spaces.some(s => s.id === R.chat)) {
    return put(body, el("div", { class: "eyebrow" }, "CHAT"), el("h1", {}, "Spaces"),
      spaces.map(s => el("button", { type: "button", class: "row-btn", onclick: () => { R.chat = s.id; home(); } }, s.kind === "dm" ? "" : s.kind === "personal" ? "" : "# ", spaceName(s, ppl, n))),
      el("div", { class: "eyebrow", style: "margin-top:18px" }, "START A CONVERSATION"),
      Object.values(ppl).filter(x => x.can_reach).map(x => el("button", { type: "button", class: "row-btn", onclick: async () => { try { R.chat = await startDM(p, x.user); home(); } catch (e) { toast("Couldn't start it", e.message); } } }, x.name, el("small", {}, TIERS[x.tier] || ""))));
  }
  const sp = space(R.chat), sname = spaceName(sp, ppl, n);
  const msgs = [...R.items.values()].filter(it => it.h.spaces.some(([s]) => s === sp.id) && ["msg", "file", "callsheet_row"].includes(it.h.kind)).sort((a, b) => a.seq - b.seq).slice(-200);
  const input = el("input", { type: "text", placeholder: `Message ${sp.kind === "channel" ? "#" + sname : sname}`, "aria-label": "Message" });
  const send = async () => { const t = input.value.trim(); if (!t) return; input.disabled = true;
    const mentions = Object.values(ppl).filter(x => t.toLowerCase().includes("@" + x.name.toLowerCase())).map(x => x.user);
    try { await post([sp.id], "msg", { text: t }, { mentions }); input.value = ""; home(); } catch (e) { toast("Not sent", e.message); input.disabled = false; } };
  input.addEventListener("keydown", e => { if (e.key === "Enter") send(); });
  const file = el("input", { type: "file", hidden: true, onchange: async () => { const f = file.files[0]; if (f) { toast("Encrypting and sending", f.name); try { await upload(sp.id, f); home(); } catch (e) { toast("Couldn't send it", e.message); } } } });
  put(body, el("div", { class: "chat-head" }, el("button", { type: "button", class: "btn sm", onclick: () => { R.chat = null; home(); } }, "‹ Spaces"), el("b", {}, sp.kind === "channel" ? "# " + sname : sname),
      sp.kind !== "personal" ? el("button", { type: "button", class: "btn sm", onclick: () => huddle(sp.id) }, "Huddle") : null),
    el("div", { class: "msgs" }, msgs.length ? msgs.map(it => {
      const who = ppl[it.author] || {}, pl = it.payload || {};
      return el("div", { class: "msg" }, el("span", { class: "av sm" }, ini(who.name)), el("div", {}, el("div", { class: "mh" }, el("b", {}, who.name || "Someone"), el("span", {}, hhmm(it.h.ts))),
        it.h.kind === "msg" ? el("div", {}, it.payload ? pl.text : "This message can't be opened on this phone yet.")
          : it.h.kind === "file" ? el("button", { type: "button", class: "file", onclick: () => openFile(it.h.ref) }, pl.name, el("small", {}, bytesTxt(pl.size || 0)))
          : el("div", { class: "muted small" }, "Your times for the call sheet are on " + (myTier(p) === "cast" ? "My day" : "Today") + ".")));
    }) : el("p", { class: "muted" }, "No messages yet.")),
    el("div", { class: "composer" }, el("button", { type: "button", class: "btn sq", "aria-label": "Attach a file or photo", onclick: () => file.click() }, "+"), file, input, el("button", { type: "button", class: "btn primary", onclick: send }, "Send")));
  const m = body.querySelector(".msgs"); m.scrollTop = m.scrollHeight;
}

/* ---------------- files ---------------- */
async function upload(sid, f) {
  const n = Math.max(1, Math.ceil(f.size / C.CHUNK));
  const lineage = ([...R.items.values()].find(it => it.h.kind === "file" && it.payload && it.payload.name === f.name && it.h.spaces.some(([s]) => s === sid)) || {}).payload;
  const meta = await api("POST", "/api/files", { space: sid, lineage: lineage ? lineage.lineage : null, chunks: n, size: f.size });
  const key = C.newKey(), digest = [];
  for (let i = 0; i < n; i++) {
    const part = new Uint8Array(await f.slice(i * C.CHUNK, (i + 1) * C.CHUNK).arrayBuffer());
    digest.push(part);
    await api("PUT", `/api/files/${meta.id}/chunks/${i}`, C.encryptChunk(key, part, meta.id, i, n));
  }
  const whole = new Uint8Array(await f.arrayBuffer());
  const sha = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", whole))).map(b => b.toString(16).padStart(2, "0")).join("");
  await post([sid], "file", { name: f.name, size: f.size, file_key: C.b64e(key), chunks: n, version: meta.version, lineage: meta.lineage, sha256: sha, note: "" }, { ref: meta.id });
}
async function openFile(fid) {
  const it = [...R.items.values()].find(x => x.h.kind === "file" && x.h.ref === fid && x.payload);
  if (!it) return toast("That file isn't on this phone yet");
  const pl = it.payload, key = C.b64d(pl.file_key), parts = [];
  try {
    for (let i = 0; i < pl.chunks; i++) parts.push(C.decryptChunk(key, await api("GET", `/api/files/${fid}/chunks/${i}`), fid, i, pl.chunks));
    const blob = new Blob(parts);
    const sha = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", await blob.arrayBuffer()))).map(b => b.toString(16).padStart(2, "0")).join("");
    if (sha !== pl.sha256) throw new Error("The file didn't arrive intact.");
    const a = el("a", { href: URL.createObjectURL(blob), download: pl.name }); document.body.append(a); a.click(); a.remove();
  } catch (e) { toast("Couldn't open it", e.message); }
}

/* ---------------- meetings and huddles ---------------- */
const MEET = { room: null, info: null };
async function meetTab(body, p) {
  put(body, el("div", { class: "eyebrow" }, "MEETINGS"), el("p", { class: "muted" }, "Loading…"));
  let list = [];
  try { list = await api("GET", `/api/meetings?production=${encodeURIComponent(p)}`); } catch (e) { put(body, el("p", { class: "muted" }, e.message)); return; }
  const ppl = people(p), n = names(p), inCall = MEET.room && MEET.info ? MEET.info.id : "";
  const where = m => { const it = R.items.get(m.item), sp = it && it.h.spaces.length === 1 && space(it.h.spaces[0][0]); return sp ? (sp.kind === "dm" ? "" : "# ") + spaceName(sp, ppl, n) : ""; };
  /* huddles show only while someone is in one; the call you're in shows at the top, not again in the list */
  const rows = list.map(m => Object.assign({}, m, (R.items.get(m.item) || {}).payload || {}))
    .filter(m => m.title && m.id !== inCall && (m.kind === "meeting" || m.here > 0));
  const here = m => m.here > 0 ? ` · ${m.here} in it` : "";
  put(body, el("div", { class: "eyebrow" }, "MEETINGS"),
    MEET.room ? meetingNow() : null,
    rows.length ? rows.map(m => el("div", { class: "card" }, el("b", {}, m.kind === "huddle" ? `${where(m) || "Private"} huddle` : m.title),
      el("div", { class: "muted small" }, (m.starts ? new Date(m.starts).toLocaleString("en-GB", { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) : "Now") + here(m)),
      el("div", { class: "row" }, el("button", { type: "button", class: "btn primary", onclick: () => joinMeeting(m.id) }, m.kind === "huddle" ? "Join" : "Join to watch"),
        m.starts ? el("button", { type: "button", class: "btn", onclick: () => ics(m) }, "Add to my calendar") : null)))
      : el("p", { class: "muted" }, MEET.room ? "No other meetings right now." : "No meetings right now."),
    el("div", { class: "card mic" }, el("b", {}, "Microphone found automatically"), el("div", { class: "muted small" }, "Your phone's microphone, or your earbuds when they're connected.")));
}
function ics(m) {
  const start = new Date(m.starts), end = new Date(start.getTime() + (m.minutes || 60) * 60000);
  const f = d => d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
  const text = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Saracen Bridge//Room 1.0.8//EN", "BEGIN:VEVENT", `UID:${m.id}@room`, `DTSTAMP:${f(new Date())}`, `DTSTART:${f(start)}`, `DTEND:${f(end)}`,
    `SUMMARY:${String(m.title).replace(/[,;\\]/g, " ")}`, "DESCRIPTION:Join from the Room.", "END:VEVENT", "END:VCALENDAR", ""].join("\r\n");
  const a = el("a", { href: URL.createObjectURL(new Blob([text], { type: "text/calendar" })), download: "meeting.ics" }); document.body.append(a); a.click(); a.remove();
}
async function huddle(sid) {
  try {
    const list = await api("GET", `/api/meetings?production=${encodeURIComponent(R.prod)}`);
    let m = list.find(x => x.kind === "huddle" && (R.items.get(x.item) || { h: { spaces: [] } }).h.spaces.length === 1 && R.items.get(x.item).h.spaces[0][0] === sid);
    if (!m) { const it = await post([sid], "huddle", { title: "Huddle", starts: null, minutes: 60, agenda: "", media_key: C.b64e(C.randomBytes(32)) }); m = { id: (await api("POST", "/api/meetings", { item: it.h.id })).id }; }
    R.tab = "meet"; home(); await joinMeeting(m.id);
  } catch (e) { toast("Couldn't start the huddle", e.message); }
}
async function joinMeeting(mid) {
  const L = window.LivekitClient;
  if (!L) return toast("Meetings didn't load", "Check your connection and reopen the Room.");
  if (!L.isE2EESupported()) return toast("This browser can't encrypt calls", "The Room only holds encrypted calls. Update your browser or phone.");
  try {
    const t = await api("POST", `/api/meetings/${mid}/token`), st = await api("GET", `/api/meetings/${mid}`);
    const it = R.items.get(st.item);
    if (!it || !it.payload || !it.payload.media_key) throw new Error("This phone can't open the meeting's key yet.");
    if (MEET.room) await MEET.room.disconnect();
    const kp = new L.ExternalE2EEKeyProvider(); await kp.setKey(C.b64d(it.payload.media_key).buffer);
    const room = new L.Room({ encryption: { keyProvider: kp, worker: new Worker("/app/vendor/livekit-client.e2ee.worker.js") },
      audioCaptureDefaults: { deviceId: "default", noiseSuppression: true, echoCancellation: true, autoGainControl: true } });
    const sp = it.h.spaces.length === 1 && space(it.h.spaces[0][0]);
    const label = t.kind === "huddle" ? `${sp ? (sp.kind === "dm" ? "" : "# ") + spaceName(sp, people(R.prod), names(R.prod)) : "Private"} huddle` : it.payload.title;
    MEET.room = room; MEET.info = Object.assign({}, t, { id: mid, title: label, hand: false });
    const sink = document.getElementById("audio-sink") || document.body.appendChild(el("div", { id: "audio-sink", hidden: true }));
    room.on(L.RoomEvent.TrackSubscribed, track => { if (track.kind === "audio") sink.append(track.attach()); })
      .on(L.RoomEvent.ParticipantPermissionsChanged, async (prev, pp) => { if (pp === room.localParticipant) { MEET.info.on_stage = !!(pp.permissions && pp.permissions.canPublish); if (MEET.info.on_stage) { await room.localParticipant.setMicrophoneEnabled(true).catch(() => null); toast("You're on stage", "Your microphone is on."); } if (R.tab === "meet") home(); } })
      .on(L.RoomEvent.Disconnected, () => { MEET.room = null; if (R.tab === "meet") home(); });
    navigator.mediaDevices && navigator.mediaDevices.addEventListener && navigator.mediaDevices.addEventListener("devicechange", () => { if (MEET.room && MEET.info.on_stage) MEET.room.switchActiveDevice("audioinput", "default").catch(() => null); });
    await room.setE2EEEnabled(true); await room.connect(t.url, t.token);
    if (t.on_stage) await room.localParticipant.setMicrophoneEnabled(true);
    R.tab = "meet"; home();
  } catch (e) { toast("Couldn't join", e.message); }
}
function meetingNow() {
  const i = MEET.info;
  return el("div", { class: "card live" }, el("div", { class: "eyebrow" }, i.kind === "huddle" ? "IN A HUDDLE" : "IN A MEETING"), el("h2", {}, i.title || "Meeting"),
    el("p", { class: "muted small" }, i.on_stage ? "You're on stage: your microphone is open." : i.hand ? "Hand raised. An executive can bring you on stage to speak." : "You're watching. Raise your hand if you need to speak."),
    el("div", { class: "row" },
      !i.on_stage ? el("button", { type: "button", class: "btn", "aria-pressed": String(!!i.hand), onclick: async () => { i.hand = !i.hand; await MEET.room.localParticipant.setAttributes({ hand: i.hand ? "up" : "" }).catch(() => null); home(); } }, i.hand ? "Lower hand" : "Raise hand") : null,
      i.on_stage ? el("button", { type: "button", class: "btn", onclick: async () => { i.muted = !i.muted; await MEET.room.localParticipant.setMicrophoneEnabled(!i.muted); home(); } }, i.muted ? "Unmute" : "Mute") : null,
      el("button", { type: "button", class: "btn", onclick: async () => { await MEET.room.disconnect(); MEET.room = null; home(); } }, "Leave")));
}

/* ---------------- live updates ---------------- */
let LIVE = null;
function live() {
  if (LIVE) return;
  const url = location.origin.replace(/^http/, "ws") + "/api/live";
  const open = async () => {
    try {
      const ws = new WebSocket(url); LIVE = ws;
      ws.onopen = async () => ws.send(JSON.stringify({ token: await bearer() }));
      ws.onmessage = async ev => { const m = JSON.parse(ev.data); if (m.seq > (R.st.seq || 0)) { const before = (R.snap.notifications || []).length; await sync().catch(() => null);
        const fresh = (R.snap.notifications || []).slice(before); if (fresh.length && document.visibilityState === "visible") toast("Something new", "Pull down or open the tab to see it.");
        if (!document.activeElement || !document.activeElement.matches("input, textarea")) home(); } };
      ws.onclose = () => { LIVE = null; setTimeout(live, 5000); };
    } catch (e) { LIVE = null; setTimeout(live, 5000); }
  };
  open();
}
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible" && R.st.status === "approved") sync().then(home).catch(() => null); });
boot();
