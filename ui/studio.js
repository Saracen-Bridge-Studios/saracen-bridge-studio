"use strict";
/* Saracen Bridge Studio UI (0.4 "Screening Room"): a launcher of independent tools, like Jon's GPT list.
   Plain DOM, no build step. Components: icons, toasts, modal, command palette (Ctrl/Cmd+K). */

function el(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "style") e.style.cssText = v;
    else if (k === "html") e.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") e.addEventListener(k.slice(2).toLowerCase(), v);
    else e.setAttribute(k, v === true ? "" : String(v));
  }
  for (const k of kids.flat(Infinity)) if (k !== null && k !== undefined && k !== false) e.append(k instanceof Node ? k : document.createTextNode(String(k)));
  return e;
}
const fmt = (n, d = 0) => (n === null || n === undefined || n === "") ? "—" : Number(n).toLocaleString("en-GB", { minimumFractionDigits: d, maximumFractionDigits: d });
const plural = (n, one, many) => `${fmt(n)} ${Number(n) === 1 ? one : (many || one + "s")}`;
const pct = n => (n === null || n === undefined) ? "—" : (n * 100).toFixed(1) + "%";
const api = {
  async get(p) { const r = await fetch(p); if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText); return r.json(); },
  async post(p, body) { const r = await fetch(p, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.detail || r.statusText); return j; },
  async put(p, body) { const r = await fetch(p, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); return r.json(); },
  async form(p, fd) { const r = await fetch(p, { method: "POST", body: fd }); const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.detail || r.statusText); return j; },
};
let CAT = null, AI = { connected: false, reason: "" }, VERSION = "";
const app = () => document.getElementById("app");
const toolById = id => CAT.tools.find(t => t.id === id);
const keep = k => k !== null && k !== undefined && k !== false;
function put(node, ...kids) { node.replaceChildren(...kids.flat(Infinity).filter(keep)); return node; }
function errBox(e) { return el("div", { class: "err" }, String(e.message || e)); }

/* ---------------- icons: one family, 1.5 stroke, round caps, 24 grid ---------------- */
const ICONS = {
  home: "M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z",
  coverage: "M7 3h7l4 4v14H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14 3v4h4M9.5 11h6M9.5 14.5h6M9.5 18h3.5",
  lookbook: "M3.5 6.5h12v12h-12zM8.5 3.5h12v12M3.5 15l3.5-3.5 3 3 2-2 3.5 3.5",
  casting: "M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM3 21v-1a6 6 0 0 1 12 0v1M18.5 4l1 2.1 2.3.3-1.7 1.6.4 2.3-2-1.1-2 1.1.4-2.3-1.7-1.6 2.3-.3z",
  schedule: "M4 9h16v11a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM4 9l1.2-4.2a1 1 0 0 1 1.2-.7l13 3.4M8.5 4.9l-1.2 4.1M13.3 6.2l-1.1 2.8M8 13.5h3M8 17h6",
  incentives: "M12 21s-6.5-5.4-6.5-11a6.5 6.5 0 0 1 13 0c0 5.6-6.5 11-6.5 11zM9.8 12.4l4.4-4.4M10 8.6h.01M14 12h.01",
  bfi: "M12 3.5l2.4 4.9 5.4.8-3.9 3.8.9 5.4-4.8-2.6-4.8 2.6.9-5.4L4.2 9.2l5.4-.8z",
  sales: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM3.5 9h17M3.5 15h17M12 3c2.4 2.4 3.5 5.6 3.5 9s-1.1 6.6-3.5 9c-2.4-2.4-3.5-5.6-3.5-9S9.6 5.4 12 3z",
  brand: "M3.5 12.5V4.5a1 1 0 0 1 1-1h8l8 8-9 9zM8 8h.01",
  finance: "M12 7.5c4.1 0 7.5-1.1 7.5-2.5S16.1 2.5 12 2.5 4.5 3.6 4.5 5 7.9 7.5 12 7.5zM4.5 5v5c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5V5M4.5 10v5c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5v-5M4.5 15v4c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5v-4",
  greenlight: "M9 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zM12 7.5h.01M12 12h.01M12 16.5h.01M7 7.5H4.5M7 12H4.5M19.5 7.5H17M19.5 12H17",
  agreement: "M5 21h14M6.5 17.5l9.8-9.8a2.1 2.1 0 0 0-3-3L3.5 14.5V17.5zM12.5 6l3 3",
  aiden: "M3.5 5.5h7v6h-7zM13.5 5.5h7v6h-7zM3.5 14.5h7v4h-7zM13.5 14.5h7v4h-7z",
  frat: "M3.5 5.5h17v13h-17zM10 9.5v5l4.5-2.5z",
  library: "M4 7h16M4 7l1.2-3h13.6L20 7M4 7v12a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V7M9.5 11h5",
  settings: "M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0M16 4v4M10 10v4M18 16v4",
  search: "M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15zM21 21l-5.2-5.2",
  sparkle: "M12 3.5l1.6 4.9 4.9 1.6-4.9 1.6L12 16.5l-1.6-4.9L5.5 10l4.9-1.6zM18.5 15.5l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7z",
  check: "M5 12.5l4.5 4.5L19 7.5",
  x: "M6 6l12 12M18 6L6 18",
  alert: "M12 4l9 16H3zM12 10v4.5M12 17.5h.01",
  info: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 11v5.5M12 7.5h.01",
  arrow: "M5 12h14M13.5 6.5 19 12l-5.5 5.5",
  clock: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5.2l3.3 2",
  download: "M12 3.5V15M7 10l5 5 5-5M4.5 15v4a1.5 1.5 0 0 0 1.5 1.5h12a1.5 1.5 0 0 0 1.5-1.5v-4",
  upload: "M12 15.5V4M7 8.5 12 3.5l5 5M4.5 15v4a1.5 1.5 0 0 0 1.5 1.5h12a1.5 1.5 0 0 0 1.5-1.5v-4",
  file: "M7 3h7l4 4v14H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14 3v4h4",
  doc: "M7 3h7l4 4v14H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14 3v4h4M9.5 12h6M9.5 15.5h6",
  folder: "M3.5 7a1.5 1.5 0 0 1 1.5-1.5h4l2 2h8a1.5 1.5 0 0 1 1.5 1.5v8.5A1.5 1.5 0 0 1 19 19H5a1.5 1.5 0 0 1-1.5-1.5z",
  reel: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM12 5.5h.01M12 18.5h.01M5.5 12h.01M18.5 12h.01",
  play: "M8 5.5v13l10.5-6.5z",
  external: "M14 4h6v6M20 4l-9 9M18 14.5V19a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h4.5",
  agents: "M4 8.5h16V19a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM9 8.5V6a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 6v2.5M4 13.5h16M11 13.5v2h2v-2",
  cloud: "M7 18.5h10.5a4 4 0 0 0 .6-7.95A6 6 0 0 0 6.6 9.1 4.75 4.75 0 0 0 7 18.5z",
  chat: "M4.5 5.5h15v10h-8l-4.5 3.5v-3.5h-2.5z",
  lock: "M6.5 11h11v9h-11zM9 11V8a3 3 0 0 1 6 0v3",
  send: "M4 12 20 4l-4 16-4.5-6.5zM11.5 13.5 20 4",
  stop: "M7 7h10v10H7z",
  trash: "M5 7h14M10 7V4.5h4V7M7 7l1 13h8l1-13",
  eye: "M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12zM12 14.75a2.75 2.75 0 1 0 0-5.5 2.75 2.75 0 0 0 0 5.5z",
  plus: "M12 5v14M5 12h14",
  users: "M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM3 21v-1a6 6 0 0 1 12 0v1M16 3.5a4 4 0 0 1 0 7.5M21 21v-1a6 6 0 0 0-4-5.6",
};
function icon(name, cls) {
  const ns = "http://www.w3.org/2000/svg";
  const s = document.createElementNS(ns, "svg");
  s.setAttribute("viewBox", "0 0 24 24"); s.setAttribute("class", "i" + (cls ? " " + cls : "")); s.setAttribute("aria-hidden", "true");
  const p = document.createElementNS(ns, "path"); p.setAttribute("d", ICONS[name] || ICONS.file); s.append(p);
  return s;
}
const toolIcon = t => icon(ICONS[t.id] ? t.id : "file");

/* ---------------- the crest in 3D: traced vectors (ui/brand/marks.js), metal in SVG, depth in CSS ---------------- */
const CALM = matchMedia("(prefers-reduced-motion: reduce)").matches;
let LOGO_N = 0;
function goldLayer(kind, id, opt) {
  const M = window.SB_MARKS, T = kind === "crest" ? M.crestT : M.wordT, d = kind === "crest" ? M.crest : M.word;
  const depth = opt.depth ?? 11, step = opt.step ?? 2.2;
  const ext = Array.from({ length: depth }, (_, k) => `<use href="#${id}-s" transform="translate(${(depth - k) * step * .35} ${(depth - k) * step})" fill="url(#${id}-side)"/>`).join("");
  const sweep = CALM || opt.still ? "" : `<animateTransform attributeName="gradientTransform" type="translate" values="-3200 0;3200 0;3200 0" keyTimes="0;.45;1" dur="${opt.sweep || 7}s" begin="${opt.delay || 0}s" repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .2 1;0 0 1 1"/>`;
  return `<svg class="sb3d-layer l-${kind}" viewBox="${M.vb}" aria-hidden="true" overflow="visible"><defs>
    <g id="${id}-s" transform="${T}"><path d="${d}"/></g>
    <linearGradient id="${id}-face" gradientUnits="userSpaceOnUse" x1="0" y1="${kind === "crest" ? 78 : 884}" x2="0" y2="${kind === "crest" ? 804 : 1028}">
      <stop offset="0" stop-color="#fff8dc"/><stop offset=".14" stop-color="#ffe28e"/><stop offset=".34" stop-color="#f4c351"/><stop offset=".5" stop-color="#cf9227"/>
      <stop offset=".58" stop-color="#94621a"/><stop offset=".68" stop-color="#dba73c"/><stop offset=".84" stop-color="#ffe6a0"/><stop offset="1" stop-color="#f3c55a"/></linearGradient>
    <linearGradient id="${id}-side" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8c5c12"/><stop offset="1" stop-color="#3e2705"/></linearGradient>
    <linearGradient id="${id}-sheen" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="900" y2="420">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".44" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fffaf0" stop-opacity=".9"/>
      <stop offset=".56" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>${sweep}</linearGradient>
    <filter id="${id}-bevel" x="-2%" y="-2%" width="104%" height="104%" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceAlpha" stdDeviation="${kind === "crest" ? 4 : 2.6}" result="b"/>
      <feSpecularLighting in="b" surfaceScale="${kind === "crest" ? 7 : 5}" specularConstant="1.15" specularExponent="26" lighting-color="#fff3d2" result="sp"><feDistantLight azimuth="225" elevation="48"/></feSpecularLighting>
      <feComposite in="sp" in2="SourceAlpha" operator="in" result="spi"/>
      <feComposite in="SourceGraphic" in2="spi" operator="arithmetic" k1="0" k2="1" k3=".85" k4="0"/></filter>
    <filter id="${id}-drop" x="-10%" y="-10%" width="120%" height="140%"><feDropShadow dx="0" dy="${kind === "crest" ? 26 : 16}" stdDeviation="${kind === "crest" ? 16 : 10}" flood-color="#05020a" flood-opacity=".75"/></filter>
    <filter id="${id}-glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="14"/></filter>
  </defs>
  <use href="#${id}-s" fill="#f2c04d" opacity="${opt.glow ?? .28}" filter="url(#${id}-glow)"/>
  <g filter="url(#${id}-drop)">${ext}</g>
  <use href="#${id}-s" fill="url(#${id}-face)" filter="url(#${id}-bevel)"/>
  <use href="#${id}-s" fill="url(#${id}-sheen)" style="mix-blend-mode:screen"/></svg>`;
}
function logo3d(opt = {}) {
  if (!window.SB_MARKS) return el("img", { src: "/ui/logo.png", alt: "Saracen Bridge", style: "width:100%" });
  const id = `sbm${++LOGO_N}`;
  const stage = el("div", { class: "sb3d-stage", html: `<div class="sb3d-plate"></div>${goldLayer("crest", id + "c", opt)}${goldLayer("word", id + "w", { ...opt, delay: (opt.delay || 0) + .35, glow: .18, depth: 9, step: 1.3 })}<div class="sb3d-glare"></div>` });
  const box = el("div", { class: "sb3d" + (opt.cls ? " " + opt.cls : ""), role: "img", "aria-label": "Saracen Bridge" }, stage, opt.sub ? el("div", { class: "sb3d-sub" }, opt.sub) : null);
  if (!CALM && opt.tilt !== false) {
    const max = opt.max || 9;
    box.addEventListener("pointermove", e => {
      const r = stage.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      box.classList.add("live");
      box.style.setProperty("--ry", `${(x - .5) * 2 * max}deg`); box.style.setProperty("--rx", `${(.5 - y) * 2 * max * .8}deg`);
      box.style.setProperty("--gx", `${x * 100}%`); box.style.setProperty("--gy", `${y * 100}%`);
    });
    box.addEventListener("pointerleave", () => { box.classList.remove("live"); box.style.setProperty("--rx", "0deg"); box.style.setProperty("--ry", "0deg"); });
  }
  return box;
}

/* ---------------- toasts ---------------- */
function toast(kind, title, body, ms) {
  const host = document.getElementById("toasts");
  const ic = { ok: "check", bad: "alert", info: "info", ai: "sparkle" }[kind] || "info";
  const t = el("div", { class: `toast ${kind}`, role: kind === "bad" ? "alert" : "status" },
    el("div", { class: "ti" }, icon(ic)), el("div", {}, el("div", { class: "tt" }, title), body ? el("div", { class: "tb" }, body) : null),
    el("button", { type: "button", class: "x", "aria-label": "Dismiss", onclick: () => close() }, icon("x")));
  let timer = null, left = ms || (kind === "bad" ? 9000 : 5000), started = Date.now();
  const close = () => { clearTimeout(timer); t.classList.add("out"); setTimeout(() => t.remove(), 170); };
  const arm = () => { started = Date.now(); timer = setTimeout(close, left); };
  t.addEventListener("mouseenter", () => { clearTimeout(timer); left -= Date.now() - started; });
  t.addEventListener("mouseleave", arm);
  host.append(t); arm();
  while (host.children.length > 4) host.firstElementChild.remove();
  if (kind === "ok" && typeof jonMood === "function") jonMood("hop", 700);
  if (kind === "bad" && typeof jonOffer === "function") {
    jonMood("concern", 2600);
    const what = [title, typeof body === "string" ? body : body && body.textContent].filter(Boolean).join(". ");
    setTimeout(() => jonOffer("error", "That didn't work. Want me to look at why?", { label: "Ask Jonny", run: () => jonAsk(`I got this message: "${what}". What does it mean, and what should I do?`) }, true), 1400);
  }
  return close;
}

/* ---------------- modal ---------------- */
function modal({ icon: ic = "info", title, body, actions = [] }) {
  return new Promise(resolve => {
    const prev = document.activeElement;
    const done = v => { scrim.classList.add("out"); setTimeout(() => { scrim.remove(); prev && prev.focus && prev.focus(); }, 160); document.removeEventListener("keydown", onKey); resolve(v); };
    const onKey = e => { if (e.key === "Escape") done(null); };
    const btns = actions.map(([label, value, primary]) => el("button", { type: "button", class: "btn" + (primary ? " primary" : ""), onclick: () => done(value) }, label));
    const scrim = el("div", { class: "scrim", onclick: e => { if (e.target === scrim) done(null); } },
      el("div", { class: "modal", role: "dialog", "aria-modal": "true", "aria-label": title },
        el("div", { class: "mi" }, icon(ic)), el("h3", {}, title), [].concat(body || []).map(b => typeof b === "string" ? el("p", {}, b) : b),
        el("div", { class: "actions" }, btns)));
    document.body.append(scrim); document.addEventListener("keydown", onKey);
    (btns.find((b, i) => actions[i][2]) || btns[0])?.focus();
  });
}

/* ---------------- command palette (Ctrl/Cmd+K, or /): opens instantly, no animation ---------------- */
let PAL = null;
let AGENTS_PROJECT = "", SALES_AGENTS = null;             /* the film last compared on Sales Agents */
function openPalette() {
  if (PAL) return;
  const input = el("input", { type: "text", placeholder: "Search tools, your scripts and actions", "aria-label": "Search", autocomplete: "off", spellcheck: "false" });
  const res = el("div", { class: "res", role: "listbox" });
  const scrim = el("div", { class: "palette-scrim", onclick: () => close() });
  const box = el("div", { class: "palette", role: "dialog", "aria-label": "Command palette" },
    el("div", { class: "q" }, icon("search"), input, el("kbd", {}, "Esc")), res,
    el("div", { class: "foot" }, el("span", {}, el("kbd", {}, "↑"), el("kbd", {}, "↓"), "move"), el("span", {}, el("kbd", {}, "Enter"), "open"), el("span", {}, el("kbd", {}, "Esc"), "close")));
  const base = [
    ...CAT.tools.map(t => ({ group: "Tools", label: t.name, hint: t.external ? "App" : t.group, ic: ICONS[t.id] ? t.id : "file", go: () => { location.hash = `#/tool/${t.id}`; }, words: `${t.name} ${t.tagline} ${t.group}` })),
    { group: "Go to", label: "Home", ic: "home", go: () => { location.hash = "#/"; } },
    { group: "Go to", label: "Library", ic: "library", go: () => { location.hash = "#/library"; } },
    { group: "Go to", label: "Settings", ic: "settings", go: () => { location.hash = "#/settings"; } },
    { group: "Actions", label: "Write coverage for every script without it", ic: "sparkle", go: () => writeMissing() },
    { group: "Actions", label: "Ask Jonny a question", ic: "chat", hint: navigator.platform.startsWith("Mac") ? "⌘ J" : "Ctrl J", go: () => askToggle(true) },
    { group: "Actions", label: "Test the AI engine", ic: "sparkle", go: () => testEngine() },
    { group: "Actions", label: "Add scripts to Script Coverage", ic: "upload", go: () => { location.hash = "#/tool/coverage"; } },
  ];
  let items = [], sel = 0, recent = [];
  api.get("/api/runs?limit=40").then(r => { recent = r.runs.map(x => ({ group: "Your work", label: x.title, hint: (toolById(x.tool) || { name: x.tool }).name, ic: "doc", go: () => { location.hash = `#/run/${x.tool}/${x.id}`; }, words: `${x.title} ${x.tool}` })); draw(); }).catch(() => {});
  const draw = () => {
    const q = input.value.trim().toLowerCase();
    const pool = q ? [...base, ...recent] : [...base.filter(i => i.group !== "Tools" || true).slice(0, 12), ...recent.slice(0, 5)];
    items = q ? pool.filter(i => (i.label + " " + (i.words || "") + " " + (i.hint || "")).toLowerCase().includes(q)).slice(0, 30) : pool;
    sel = Math.min(sel, Math.max(items.length - 1, 0));
    let last = null;
    put(res, items.length ? items.map((it, i) => [it.group !== last ? (last = it.group, el("div", { class: "grp" }, it.group)) : null,
      el("div", { class: "item", role: "option", "aria-selected": String(i === sel), onmousemove: () => { if (sel !== i) { sel = i; mark(); } }, onclick: () => run(i) },
        el("span", { class: "ic" }, icon(it.ic)), el("span", { class: "lab" }, it.label), it.hint ? el("span", { class: "hint" }, it.hint) : null)])
      : el("div", { class: "empty" }, "Nothing matches “" + input.value + "”."));
  };
  const mark = () => [...res.querySelectorAll(".item")].forEach((n, i) => { n.setAttribute("aria-selected", String(i === sel)); if (i === sel) n.scrollIntoView({ block: "nearest" }); });
  const run = i => { const it = items[i]; close(); it && it.go(); };
  const close = () => { scrim.remove(); box.remove(); PAL = null; };
  input.addEventListener("input", () => { sel = 0; draw(); });
  input.addEventListener("keydown", e => {
    if (e.key === "ArrowDown") { e.preventDefault(); sel = Math.min(sel + 1, items.length - 1); mark(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); sel = Math.max(sel - 1, 0); mark(); }
    else if (e.key === "Enter") { e.preventDefault(); run(sel); }
    else if (e.key === "Escape") { e.preventDefault(); close(); }
  });
  document.body.append(scrim, box); PAL = { close }; draw(); input.focus();
}
document.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); PAL ? PAL.close() : openPalette(); }
  else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "j") { e.preventDefault(); askToggle(); }
  else if (e.key === "/" && !PAL && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName)) { e.preventDefault(); openPalette(); }
});



/* ---------------- Jonny (Tim, 15 Oct; was Jon): the Studio's helper character (an original cartoon clapperboard, the Studio's Clippy) ----------------
   Parts carry classes the CSS animates: blink (eyes), look (pupils follow the pointer), talk (the clapper snaps), think,
   wave, hop, concern. Lessons from Clippy built in: he offers, never insists; one tip per page; never while you type;
   "Not now" snoozes that kind of tip; three ignored tips in a row and he stays quiet for the session; tips can be
   switched off. */
let JON_N = 0;
function jonSvg(mini) {
  const id = `jn${++JON_N}`;
  const g = `url(#${id}g)`;
  return `<svg class="jon-svg" viewBox="${mini ? "30 30 140 150" : "0 20 200 175"}" aria-hidden="true"><defs>
    <linearGradient id="${id}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff1c2"/><stop offset=".35" stop-color="#f6cf63"/><stop offset=".7" stop-color="#d79e2f"/><stop offset="1" stop-color="#a8761a"/></linearGradient>
    <linearGradient id="${id}s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2d1b48"/><stop offset="1" stop-color="#140b22"/></linearGradient>
    <clipPath id="${id}c"><path d="M44 58 L156 40 L160 60 L48 78 Z"/></clipPath></defs>
  ${mini ? "" : `<ellipse class="j-shadow" cx="100" cy="186" rx="50" ry="6.5" fill="#000" opacity=".45"/>`}
  <g class="j-fig">
    ${mini ? "" : `<path d="M74 168 q-2 12 -14 12 h-6 q-6 0 -4 -6 l4 -6z M126 168 q2 12 14 12 h6 q6 0 4 -6 l-4 -6z" fill="${g}"/>
    <g class="j-arm-l"><path d="M42 112 q-20 4 -22 22" stroke="#f2c04d" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="20" cy="136" r="7" fill="${g}"/></g>
    <g class="j-arm-r"><path d="M158 112 q22 -6 26 -26" stroke="#f2c04d" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="184" cy="84" r="7" fill="${g}"/></g>`}
    <rect x="40" y="78" width="120" height="94" rx="14" fill="url(#${id}s)" stroke="${g}" stroke-width="4"/>
    <g class="j-clap"><g clip-path="url(#${id}c)"><rect x="40" y="36" width="124" height="46" fill="#120a1e"/>
      <g fill="${g}"><path d="M50 36 l14 0 l-14 46 l-14 0z"/><path d="M78 36 l14 0 l-14 46 l-14 0z"/><path d="M106 36 l14 0 l-14 46 l-14 0z"/><path d="M134 36 l14 0 l-14 46 l-14 0z"/><path d="M162 36 l14 0 l-14 46 l-14 0z"/></g></g>
      <path d="M44 58 L156 40 L160 60 L48 78 Z" fill="none" stroke="${g}" stroke-width="3" stroke-linejoin="round"/></g>
    <circle cx="47" cy="77" r="5" fill="${g}"/>
    <g class="j-eyes"><ellipse cx="78" cy="114" rx="15" ry="17" fill="#fbf6ec"/><ellipse cx="122" cy="114" rx="15" ry="17" fill="#fbf6ec"/>
      <g class="j-pupils"><circle cx="79" cy="117" r="8" fill="#1a0f2a"/><circle cx="123" cy="117" r="8" fill="#1a0f2a"/>
      <circle cx="82" cy="113" r="3" fill="#fff"/><circle cx="126" cy="113" r="3" fill="#fff"/></g></g>
    <g class="j-brows"><path class="j-brow-l" d="M64 92 q12 -8 26 -2" stroke="#f2c04d" stroke-width="4" fill="none" stroke-linecap="round"/>
      <path class="j-brow-r" d="M110 90 q14 -6 26 2" stroke="#f2c04d" stroke-width="4" fill="none" stroke-linecap="round"/></g>
    <path class="j-smile" d="M84 142 q16 14 32 0" stroke="#f2c04d" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <path class="j-open" d="M86 140 q14 -2 28 0 q-2 16 -14 16 q-12 0 -14 -16z" fill="#2a0f12" stroke="#f2c04d" stroke-width="3.5" stroke-linejoin="round"/>
    <path class="j-flat" d="M86 146 q14 -5 28 0" stroke="#f2c04d" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    ${mini ? "" : `<path d="M54 160 h40 M106 160 h40" stroke="rgba(242,192,77,.35)" stroke-width="2"/>`}
  </g></svg>`;
}
const JON = { dock: null, bubble: null, moodTimer: null, blinkTimer: null };
function jonMood(m, ms) {   // talk | think | wave | hop | concern | null
  document.querySelectorAll(".jon").forEach(n => ["talk", "think", "wave", "hop", "concern"].forEach(k => n.classList.toggle(k, k === m)));
  clearTimeout(JON.moodTimer);
  if (m && ms) JON.moodTimer = setTimeout(() => jonMood(null), ms);
}
function jonBlink() {
  clearTimeout(JON.blinkTimer);
  JON.blinkTimer = setTimeout(() => {
    document.querySelectorAll(".jon").forEach(n => { n.classList.add("blink"); setTimeout(() => n.classList.remove("blink"), 150); });
    jonBlink();
  }, 2400 + Math.random() * 3800);
}
function jonDock() {
  if (JON.dock) return JON.dock;
  const dock = el("button", { type: "button", class: "jon jon-dock", "aria-label": `Ask Jonny (${navigator.platform.startsWith("Mac") ? "Command J" : "Ctrl J"})`, title: `Ask Jonny · ${navigator.platform.startsWith("Mac") ? "⌘ J" : "Ctrl J"}`, html: jonSvg(false), onclick: () => { jonHide(); askToggle(true); } });
  document.body.append(dock);
  if (!CALM) {
    let raf = 0;
    document.addEventListener("pointermove", e => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        document.querySelectorAll(".jon").forEach(n => {
          const r = n.getBoundingClientRect(); if (!r.width) return;
          const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height * .55), d = Math.hypot(dx, dy) || 1;
          const k = Math.min(1, d / 260);
          n.style.setProperty("--px", `${(dx / d) * 4.5 * k}px`); n.style.setProperty("--py", `${(dy / d) * 4 * k}px`);
        });
      });
    }, { passive: true });
    jonBlink();
  }
  JON.dock = dock;
  return dock;
}

/* the coach: offers help when someone looks stuck */
const COACH = { page: "", shown: false, count: 0, ignored: 0, snoozed: new Set(), lastInput: 0, lastActive: Date.now(), routeAt: 0, clicks: [], started: false };
const tipsOn = () => { try { return localStorage.getItem("jon-tips") !== "off"; } catch (e) { return true; } };
/* how Jonny's answers appear: "stream" (steady, line by line) or "finished" (only when complete). Tim, 15 Oct. */
function askReveal() { try { return localStorage.getItem("jonny-reveal") === "finished" ? "finished" : "stream"; } catch (e) { return "stream"; } }
function setTips(on) { try { localStorage.setItem("jon-tips", on ? "on" : "off"); } catch (e) { /* private window */ } }
function jonHide() { if (JON.bubble) { const b = JON.bubble; JON.bubble = null; b.classList.add("out"); setTimeout(() => b.remove(), 160); } }
function jonAsk(q) { jonHide(); askToggle(true); setTimeout(() => ASK.node && ASK.node.send(q), 80); }
function jonOffer(type, text, action, force) {
  const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || "") || Date.now() - COACH.lastInput < 4000;
  if (!tipsOn() || ASK.open || PAL || document.hidden || JON.bubble || typing || COACH.count >= 5 || COACH.ignored >= 3 || COACH.snoozed.has(type)) return false;
  if (COACH.shown && !force) return false;
  COACH.shown = true; COACH.count++;
  jonDock();
  let settled = false;
  const done = accepted => { if (settled) return; settled = true; COACH.ignored = accepted ? 0 : COACH.ignored + 1; jonHide(); };
  const b = el("div", { class: "jon-bubble", role: "status" },
    el("div", { class: "txt" }, text),
    el("div", { class: "acts" },
      action ? el("button", { type: "button", class: "btn sm primary", onclick: () => { done(true); action.run(); } }, action.label) : null,
      el("button", { type: "button", class: "btn sm quiet", onclick: () => { COACH.snoozed.add(type); done(false); } }, "Not now"),
      el("button", { type: "button", class: "off", title: "Jonny stays quiet until you turn tips back on in Settings", onclick: () => { setTips(false); done(false); toast("info", "Jonny will keep quiet", "Turn his tips back on in Settings. He's still here if you click him."); } }, "Turn off tips")));
  document.body.append(b); JON.bubble = b;
  jonMood("wave", 1900);
  setTimeout(() => { if (JON.bubble === b) done(false); }, 16000);
  return true;
}
function coachRoute() {
  COACH.page = location.hash || "#/"; COACH.shown = false; COACH.routeAt = Date.now(); jonHide();
  const [, kind, id] = COACH.page.split("/"); const t = kind === "tool" ? toolById(id) : null;
  if (!t || t.external) return;
  let seen = false;
  try { seen = !!localStorage.getItem("jon-seen-" + id); localStorage.setItem("jon-seen-" + id, "1"); } catch (e) { seen = true; }
  if (!seen) setTimeout(() => { if (COACH.page === `#/tool/${id}`) jonOffer("intro", `First time in ${t.name}? I can walk you through it, one step at a time.`, { label: "Show me", run: () => jonAsk(`Walk me through ${t.name}, step by step.`) }); }, 4500);
}
function coachStart() {
  jonDock();
  const touch = () => { COACH.lastActive = Date.now(); };
  ["pointerdown", "scroll", "wheel"].forEach(ev => document.addEventListener(ev, touch, { passive: true, capture: true }));
  document.addEventListener("keydown", e => {             // typing in a field: Jon waits (Esc, arrows and shortcuts don't count)
    touch();
    const t = e.target, editable = t && (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable);
    if (editable && !e.ctrlKey && !e.metaKey && (e.key.length === 1 || e.key === "Backspace" || e.key === "Delete")) COACH.lastInput = Date.now();
  }, true);
  document.addEventListener("click", e => {             // the same button again and again: probably stuck
    const btn = e.target.closest && e.target.closest("main button"); if (!btn) return;
    const now = Date.now(); COACH.clicks = COACH.clicks.filter(c => now - c.t < 12000 && c.b === btn).concat([{ t: now, b: btn }]);
    if (COACH.clicks.length >= 3) {
      COACH.clicks = [];
      const label = btn.textContent.trim();
      setTimeout(() => jonOffer("stuck", `"${label}" isn't doing what you expect? Tell me what you're after and I'll help.`, { label: "Ask Jonny", run: () => jonAsk(`I keep pressing "${label}" on this page and it isn't doing what I expect. What should I check?`) }), 600);
    }
  }, true);
  setInterval(() => {                                     // a long pause on a tool page with fields to fill
    const [, kind, id] = (location.hash || "#/").split("/"); const t = kind === "tool" ? toolById(id) : null;
    if (t && !t.external && Date.now() - COACH.lastActive > 90000 && app().querySelector("input, select")) {
      COACH.lastActive = Date.now();
      jonOffer("idle", `Still with me? If ${t.name} has you stuck, I can help.`, { label: "Help me", run: () => jonAsk(`I'm on ${t.name} and not sure what to do next. What should I fill in first?`) });
    }
  }, 5000);
  new MutationObserver(muts => {                          // a preliminary or failing result appears after the user acts
    if (Date.now() - COACH.routeAt < 2500) return;
    for (const m of muts) for (const n of m.addedNodes) {
      if (n.nodeType !== 1) continue;
      const sel = ".note.FAIL, .note.PRELIMINARY, .pill.FAIL:not(.st)";   /* .st: a job or file status, not a result (Tim, 13 Oct) */
      const hit = n.matches?.(sel) ? n : n.querySelector?.(sel);
      if (hit) {
        const what = hit.classList.contains("PRELIMINARY") ? "preliminary" : "a fail";
        clearTimeout(COACH.resTimer);
        COACH.resTimer = setTimeout(() => jonOffer("result", `That result is ${what}. Want me to explain what's behind it and what would change it?`, { label: "Explain it", run: () => jonAsk("Explain the result on this page: what's behind it, and what would change it?") }), 1200);
        return;
      }
    }
  }).observe(app(), { childList: true, subtree: true });
}

/* ---------------- Ask Jonny: the assistant drawer (local Gemma; the user's cloud AI only if they switched it on) ---------------- */
const ASK = { open: false, msgs: [], busy: null, share: true, node: null };
function mdLite(text) {
  /* Jonny's answers as simple formatting. Tim, 15 Oct: "seeing some json in here". Gemma sometimes fences a formula or
     data in ``` (often ```json), writes LaTeX ($$ \text{...} $$) or a markdown table; none of that was understood here, so
     the raw symbols showed. Fences are shown as a quiet box without the markers or language name, JSON as a readable
     list, LaTeX as plain words, tables as tables (1.0.7). */
  const esc = t => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const latex = t => t.replace(/\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$([^$\n]+?)\$/g, (m, a, b, c, d) => (a || b || c || d)
    .replace(/\\(?:text|mathrm|textbf|mathbf|operatorname)\{([^}]*)\}/g, "$1").replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, "($1) / ($2)")
    .replace(/\\times|\\cdot/g, "×").replace(/\\(?:left|right)/g, "").replace(/\\%/g, "%").replace(/\\[a-zA-Z]+/g, "").replace(/[{}]/g, "").replace(/\s+/g, " ").trim());
  const inline = t => esc(latex(t))
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<i>$2</i>")
    .replace(/\[([^\]]+)\]\((#\/[a-z0-9\/_-]*|https?:\/\/[^\s)]+)\)/gi, (m, t, u) => {
      const own = u.match(/^https?:\/\/(?:127\.0\.0\.1|localhost)(?::\d+)?\/?(?:ui\/?)?(#\/[a-z0-9\/_-]*)$/i);   // the model sometimes writes the full local address
      if (own) u = own[1];
      return u.startsWith("#") ? `<a class="go" href="${u}">${t}</a>` : `<a href="${u}" target="_blank" rel="noopener">${t}</a>`;
    });
  const label = k => String(k).replace(/_/g, " ").replace(/^./, c => c.toUpperCase());
  const jsonView = v => Array.isArray(v) ? `<ul>${v.map(x => `<li>${typeof x === "object" && x ? jsonView(x) : inline(String(x))}</li>`).join("")}</ul>`
    : v && typeof v === "object" ? `<ul>${Object.entries(v).map(([k, x]) => `<li><b>${esc(label(k))}:</b> ${typeof x === "object" && x ? jsonView(x) : inline(String(x))}</li>`).join("")}</ul>`
    : inline(String(v));
  const asJson = t => { const s = t.trim(); if (!/^[[{][\s\S]*[\]}]$/.test(s)) return null; try { const v = JSON.parse(s); return v && typeof v === "object" ? v : null; } catch (e) { return null; } };
  const out = []; let list = null, code = null, table = null;
  const closeList = () => { if (list) { out.push(`</${list.kind}>`); list = null; } };
  const closeTable = () => { if (table) { out.push(`<div class="md-table"><table>${table.map((r, i) => `<tr>${r.map(c => i ? `<td>${inline(c)}</td>` : `<th>${inline(c)}</th>`).join("")}</tr>`).join("")}</table></div>`); table = null; } };
  const lines = text.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trimEnd();
    if (/^\s*```/.test(line)) {                       // a fence opens or closes; its language name ("json") is never shown
      if (code === null) { closeList(); closeTable(); code = []; }
      else { const body = code.join("\n"), j = asJson(body); out.push(j ? `<div class="md-data">${jsonView(j)}</div>` : body.trim() ? `<div class="md-code">${esc(latex(body.trim()))}</div>` : ""); code = null; }
      continue;
    }
    if (code !== null) { code.push(line); continue; }
    if (/^\s*\|.*\|\s*$/.test(line)) {                // a markdown table row
      closeList();
      if (/^\s*\|[\s:|-]+\|\s*$/.test(line)) continue;  // the |---|---| separator
      (table = table || []).push(line.trim().slice(1, -1).split("|").map(c => c.trim()));
      continue;
    }
    closeTable();
    const j = asJson(line);
    if (j) { closeList(); out.push(`<div class="md-data">${jsonView(j)}</div>`); continue; }
    const li = line.match(/^\s*(?:[-*•]|(\d+)[.)])\s+(.*)$/);
    if (li) { const kind = li[1] ? "ol" : "ul"; if (!list || list.kind !== kind) { closeList(); list = { kind };
      out.push(kind === "ol" && li[1] !== "1" ? `<ol start="${Number(li[1])}">` : `<${kind}>`); }   /* "4." after a bullet list stays 4 */
      out.push(`<li>${inline(li[2])}</li>`); continue; }
    closeList();
    const h = line.match(/^#{1,4}\s+(.*)$/);
    if (h) out.push(`<p class="h">${inline(h[1])}</p>`);
    else if (/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/.test(line)) continue;   // horizontal rules
    else if (line.trim()) out.push(`<p>${inline(line)}</p>`);
  }
  if (code !== null && code.join("").trim()) {             // a fence still being written: data isn't shown half-done
    const body = code.join("\n").trim();
    out.push(/^[[{]/.test(body) ? `<div class="md-code muted">Writing…</div>` : `<div class="md-code">${esc(latex(body))}</div>`);
  }
  closeList(); closeTable();
  return out.join("");
}
function askSuggestions() {
  const h = location.hash || "#/", [, kind, a] = h.split("/"), t = kind === "tool" ? toolById(a) : null;
  if (t) return [`Walk me through ${t.name}, step by step`, `What do I need before I use ${t.name}?`, "Explain what's on this page"];
  if (kind === "run") return ["Explain this result in plain English", "What should I do next with this?", "What are the weak spots here?"];
  return ["I have a new script. Where do I start?", "How does the incentive calculator work?", "Help me sharpen my logline"];
}
function askEngineLine() {
  const c = AI.cloud || {};
  if (c.active && c.active.chat) return el("span", { class: "eng cloud" }, el("span", { class: "tag" }, "Cloud"), `${c.name} · ${c.model}`);
  if (AI.connected) return el("span", { class: "eng", title: AI.description || "" }, el("span", { class: "dot ok" }), "Local compute · on this computer");
  return el("span", { class: "eng" }, el("span", { class: "dot warn" }), "No AI engine connected");
}
function askBuild() {
  const list = el("div", { class: "ask-list", role: "log", "aria-live": "polite" });
  const input = el("textarea", { rows: 1, placeholder: "Ask about this page, a tool, or your film…", "aria-label": "Message" });
  const send = el("button", { type: "button", class: "ask-send", "aria-label": "Send" }, icon("send"));
  const share = el("button", { type: "button", class: "ask-share", "aria-pressed": "true", title: "Let Jonny read the page you're on" }, icon("eye"), el("span", {}, "Reads this page"));
  const head = el("div", { class: "ask-head" },
    el("span", { class: "jon jon-avatar", html: jonSvg(true) }),
    el("div", { class: "grow" }, el("div", { class: "ttl" }, "Ask Jonny"), el("div", { class: "sub" })),
    el("button", { type: "button", class: "icon-btn", title: "New conversation", "aria-label": "New conversation", onclick: () => { if (ASK.busy) ASK.busy.abort(); ASK.msgs = []; draw(); } }, icon("trash")),
    el("button", { type: "button", class: "icon-btn", title: "Close (Esc)", "aria-label": "Close", onclick: () => askToggle(false) }, icon("x")));
  const box = el("aside", { class: "ask", "aria-label": "Ask Jonny", "aria-hidden": "true" }, head, list,
    el("div", { class: "ask-compose" }, el("div", { class: "field" }, input, send), el("div", { class: "meta" }, share, el("span", { class: "hint" }, "Enter to send · Shift+Enter new line"))));
  const grow = () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 160) + "px"; };
  input.addEventListener("input", grow);
  input.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); go(); } });
  box.addEventListener("keydown", e => { if (e.key === "Escape") askToggle(false); });
  share.addEventListener("click", () => { ASK.share = !ASK.share; share.setAttribute("aria-pressed", String(ASK.share)); share.lastChild.textContent = ASK.share ? "Reads this page" : "Page not shared"; });
  send.addEventListener("click", () => ASK.busy ? ASK.busy.abort() : go());
  list.addEventListener("click", e => { const a = e.target.closest("a.go"); if (a && matchMedia("(max-width: 820px)").matches) askToggle(false); });
  /* Each message is built once and then updated in place (1.0.7). Tim, 15 Oct: the answer "flashes" as it types. Every
     update rebuilt the whole conversation 25 times a second, so each message replayed its fade-in, a blinking caret
     restarted, and half-written markdown (** and [links]) flickered in and out: a photosensitivity risk, and hard to read.
     Now finished lines are shown formatted and never change; the line being written is plain text, updated at most
     about 7 times a second; nothing blinks. In Settings, answers can instead appear only when they're finished. */
  const nodeOf = m => {
    if (m._el) return m._el;
    if (m.role === "user") return (m._el = el("div", { class: "msg me" }, m.content));
    const tag = el("span", { class: "tag", style: "display:none" }, "Cloud"), wait = el("span", { class: "wait" });
    const done = el("div", { class: "done" }), tail = el("p", { class: "tail" }), status = el("div", { class: "writing" });
    const srcs = el("div", {});
    m._parts = { tag, wait, done, tail, status, srcs, shown: null };
    return (m._el = el("div", { class: "msg ai" }, el("div", { class: "who" }, el("span", { class: "jon jon-mini", html: jonSvg(true) }), "Jonny", tag, wait),
      el("div", { class: "body" }, done, tail), status, srcs));
  };
  const plainTail = t => /^\s*(```|\|)/.test(t) ? "" : t.replace(/^\s*[-*]\s+/, "• ").replace(/\*|__|`/g, "").replace(/^\s*#+\s*/, "").replace(/\[([^\]]*)\]\([^)]*\)?/g, "$1").replace(/\[([^\]]*)$/, "$1");
  const paint = m => {
    if (m.role === "user") return;
    const p = m._parts;
    m._el.classList.toggle("err", !!m.error);
    p.tag.style.display = m.cloud ? "" : "none";             /* .tag's own display would beat the hidden attribute */
    p.wait.textContent = m.waiting || "";
    const setDone = html => { if (p.shown !== html) { p.done.innerHTML = html; p.shown = html; } };
    if (m.error) { setDone(mdLite(m.error)); p.tail.textContent = ""; p.status.textContent = ""; return; }
    if (m.live) {
      const hold = askReveal() === "finished", cut = m.content.lastIndexOf("\n");
      setDone(hold || cut < 0 ? "" : mdLite(m.content.slice(0, cut)));
      p.tail.textContent = hold ? "" : plainTail(m.content.slice(cut + 1));
      p.status.textContent = !m.content ? "Jonny is thinking…" : hold ? "Jonny is writing. The answer appears when it's finished." : "";
      return;
    }
    setDone(mdLite(m.content || "")); p.tail.textContent = ""; p.status.textContent = "";
    if (m.sources && m.sources.length && !p.srcs.childNodes.length) put(p.srcs, el("div", { class: "srcs" }, el("span", { class: "lbl" }, "From Saracen Bridge's documents"),
      [...new Set(m.sources.map(x => x.title))].slice(0, 4).map(t => el("span", { class: "src", title: t }, icon("doc"), t))));
  };
  const nearBottom = () => list.scrollHeight - list.scrollTop - list.clientHeight < 80;
  const draw = () => {
    put(head.querySelector(".sub"), askEngineLine());
    send.replaceChildren(icon(ASK.busy ? "stop" : "send")); send.classList.toggle("busy", !!ASK.busy); send.setAttribute("aria-label", ASK.busy ? "Stop" : "Send");
    if (!ASK.msgs.length) {
      const off = !AI.connected && !(AI.cloud && AI.cloud.active && AI.cloud.active.chat);
      return put(list, el("div", { class: "ask-empty" },
        el("div", { class: "jon jon-hero", html: jonSvg(false) }),
        el("div", { class: "hello" }, "I'm Jonny. How can I help with ", el("em", {}, "your film?")),
        el("p", {}, "I know every tool in the Studio and Saracen Bridge's own methods, and I can see the page you're on. Ask me how to do something, what a result means, or for notes on the project."),
        off ? el("div", { class: "notice", style: "margin:6px 0 0" }, el("div", { class: "ic" }, icon("sparkle")), el("div", { class: "grow" }, el("div", {}, "No AI engine yet"), el("div", { class: "sub" }, "Connect Gemma, or your own cloud AI, in Settings.")), el("a", { class: "btn sm", href: "#/settings", onclick: () => askToggle(false) }, "Set up"))
          : el("div", { class: "sugs" }, askSuggestions().map(q => el("button", { type: "button", class: "sug", onclick: () => { input.value = q; go(); } }, icon("arrow"), q)))));
    }
    const stick = nearBottom() || ASK.msgs.some(m => !m._el);
    const want = ASK.msgs.map(nodeOf);
    [...list.children].forEach(n => { if (!want.includes(n)) n.remove(); });       // the empty state, or a cleared chat
    want.forEach(n => { if (n.parentNode !== list) list.append(n); });              // only new messages are added (and fade in once)
    ASK.msgs.forEach(paint);
    if (stick) list.scrollTop = list.scrollHeight;
  };
  async function go() {
    const q = input.value.trim();
    if (!q || ASK.busy) return;
    input.value = ""; grow();
    ASK.msgs.push({ role: "user", content: q });
    const reply = { role: "assistant", content: "", live: true };
    ASK.msgs.push(reply);
    const ctrl = new AbortController(); ASK.busy = ctrl; jonMood("think"); draw();
    const crumbs = [...document.querySelectorAll("#topbar .crumbs > *")].map(n => n.textContent).filter(t => t !== "/").join(" / ");
    const page = ASK.share ? { title: crumbs || document.title, path: location.hash || "#/", text: (app().innerText || "").slice(0, 6000) } : null;
    const slow = setTimeout(() => { if (!reply.content) { reply.waiting = "Warming up the engine. The first answer loads the model."; draw(); } }, 3500);
    try {
      const r = await fetch("/api/assist/chat", { method: "POST", headers: { "Content-Type": "application/json" }, signal: ctrl.signal,
        body: JSON.stringify({ messages: ASK.msgs.filter(m => m !== reply && !m.error).map(({ role, content }) => ({ role, content })), page }) });
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
      reply.cloud = r.headers.get("X-Cloud") === "1";
      try { reply.sources = JSON.parse(decodeURIComponent(r.headers.get("X-Sources") || "[]")); } catch (e) { reply.sources = []; }
      jonMood("talk");
      const rd = r.body.getReader(), dec = new TextDecoder();
      let last = 0;
      for (;;) {
        const { value, done } = await rd.read();
        if (done) break;
        reply.content += dec.decode(value, { stream: true }); reply.waiting = null;
        const cut = reply.content.indexOf("\u0000");
        if (cut >= 0) { reply.error = reply.content.slice(cut + 1); reply.content = reply.content.slice(0, cut); break; }
        if (performance.now() - last > 150) { last = performance.now(); draw(); }
      }
      if (!reply.content.trim() && !reply.error) reply.error = "No answer came back. Try asking again.";
    } catch (e) {
      if (e.name === "AbortError") { reply.content += reply.content ? "\n\n*Stopped.*" : "*Stopped.*"; }
      else reply.error = e.message + (/settings|key|engine/i.test(e.message) ? "\n\n[Open Settings](#/settings)" : "");
    } finally {
      clearTimeout(slow); reply.live = false; reply.waiting = null; ASK.busy = null; jonMood(reply.error ? "concern" : null, reply.error ? 2500 : 0); draw(); input.focus();
    }
  }
  document.body.append(box);
  ASK.node = { box, draw, input, send: q => { input.value = q; grow(); go(); } };
  return ASK.node;
}
function askToggle(force) {
  const n = ASK.node || askBuild();
  ASK.open = force === undefined ? !ASK.open : !!force;
  n.box.classList.toggle("open", ASK.open); n.box.setAttribute("aria-hidden", String(!ASK.open));
  document.body.classList.toggle("asking", ASK.open);
  if (ASK.open) jonHide();
  if (ASK.open) { n.draw(); setTimeout(() => n.input.focus(), 60); }
}

/* ---------------- status of a tool ---------------- */
const runsOn = () => (AI.cloud && AI.cloud.active && AI.cloud.active.writing) ? `${AI.cloud.name}, your cloud account` : "local compute";
const aiWrites = () => AI.connected || !!(AI.cloud && AI.cloud.active && AI.cloud.active.writing);
function status(t) {
  // needs_ai = AI parts not built yet; ai_built = built, and they run once an AI engine is connected
  const built = t.ai_built || [];
  if (t.coming_soon) return ["soon", "Coming soon"];
  if (t.external) return ["ext", "Opens app"];
  if (built.length && !aiWrites()) return ["ai", "Needs AI engine"];
  if (!t.needs_ai.length) return ["ready", "Ready"];
  if (t.ready.length || built.length) return ["partial", "Ready · more coming"];   // Tim, 13 Oct: "what does core ready mean?"
  return ["soon", "Coming soon"];
}
const stateTag = t => { const [c, label] = status(t); return el("span", { class: "state " + c }, el("span", { class: "dot" }), label); };

function table(headers, rows) {
  const tb = rows instanceof HTMLTableSectionElement ? rows : el("tbody", {}, rows);
  const th = h => h.startsWith("#") && h.length > 1 ? el("th", { scope: "col", class: "num" }, h.slice(1)) : el("th", { scope: "col" }, h);
  return sideScroll(el("div", { class: "scroll" }, el("table", {}, el("thead", {}, el("tr", {}, headers.map(th))), tb)));
}
/* A table wider than its card (Tim, 13 Oct: crew rates' week column was out of reach, its scrollbar 27,000 px down):
   the box keeps its own scrollbars in view, a fade marks hidden columns, and arrow buttons move across. */
function sideScroll(box) {
  const left = el("button", { type: "button", class: "side-arrow l", "aria-label": "Show the columns on the left", onclick: () => box.scrollBy({ left: -box.clientWidth * .7, behavior: "smooth" }) }, icon("arrow"));
  const right = el("button", { type: "button", class: "side-arrow r", "aria-label": "Show more columns", onclick: () => box.scrollBy({ left: box.clientWidth * .7, behavior: "smooth" }) }, icon("arrow"));
  const wrap = el("div", { class: "scroll-wrap" }, box, left, right);
  const mark = () => {
    const more = box.scrollWidth - box.clientWidth > 4;
    wrap.classList.toggle("more-right", more && box.scrollLeft + box.clientWidth < box.scrollWidth - 4);
    wrap.classList.toggle("more-left", more && box.scrollLeft > 4);
  };
  box.addEventListener("scroll", mark, { passive: true });
  if (window.ResizeObserver) new ResizeObserver(mark).observe(box);
  setTimeout(mark, 0);
  return wrap;
}

/* ---------------- frame: nav, top bar, engine chip ---------------- */
function buildNav(route) {
  const nav = document.getElementById("nav");
  const link = (href, label, ic, n) => el("a", { href, "aria-current": route === href ? "page" : null }, el("span", { class: "ic" }, icon(ic)), el("span", {}, label), n ? el("span", { class: "n" }, n) : null);
  put(nav, link("#/", "Home", "home"),
    CAT.groups.map(g => [el("div", { class: "grp" }, g), CAT.tools.filter(t => t.group === g && t.menu !== false).map(t => link(`#/tool/${t.id}`, t.name, ICONS[t.id] ? t.id : "file"))]),
    el("div", { class: "grp" }, "Studio"), link("#/room", "Room", "users", typeof roomBadge === "function" ? roomBadge() : null),
    link("#/library", "Library", "library"), link("#/settings", "Settings", "settings"));
}
const prettyModel = m => String(m || "").replace(/\.gguf$/i, "").replace(/[-_](it|instruct)([-_].*)?$/i, "").split(/[-_:\s]+/).filter(Boolean)
  .map((w, i) => /^\d+(\.\d+)?[bkm]$/i.test(w) || /^e\d+b$/i.test(w) ? w.toUpperCase() : i === 0 ? w[0].toUpperCase() + w.slice(1) : w).join(" ");
function engineChip() {
  /* Tim, 13 Oct: no model names here. Local compute (this computer) or cloud compute (the user's own AI account), one click apart. */
  const foot = document.getElementById("side-foot");
  const c = AI.cloud || {}, cloud = !!c.enabled;
  const dl = AI.download || {};
  const pct = dl.total_bytes ? Math.floor(100 * (dl.done_bytes || 0) / dl.total_bytes) : 0;
  const sub = cloud ? `${c.name || "Cloud"} · your own account` : dl.active ? `Downloading ${dl.model_name || "Gemma"} · ${pct}%`
    : AI.connected ? "Runs on this computer" : dl.state === "paused" || dl.state === "waiting" ? `${dl.model_name || "Gemma"} download paused · ${pct}%`
    : dl.state === "error" ? "Gemma download stopped: see Settings" : "No local engine yet";
  /* Tim, 13 Oct: "private" was said twice. One status light instead: green while everything stays on this computer,
     red with the words gone dark while Cloud is on. */
  const privacy = cloud ? `Cloud is on: questions and writing go to ${c.name || "your cloud AI"}. Switch to Local compute to keep everything on this computer.`
    : "Private and offline: nothing leaves this computer.";
  put(foot,
    el("div", { class: "compute", role: "group", "aria-label": "Where the AI runs" },
      el("button", { type: "button", "aria-pressed": String(!cloud), title: AI.connected ? AI.description : AI.reason, onclick: () => setCompute(false) },
        el("span", { class: "dot " + (AI.connected ? "ok" : "warn") }), "Local compute"),
      el("button", { type: "button", "aria-pressed": String(cloud), onclick: () => setCompute(true) }, icon("cloud"), "Cloud")),
    el("a", { class: "compute-sub", href: "#/settings" }, sub,
      !cloud && (dl.active || dl.state === "paused" || dl.state === "waiting") ? el("span", { class: "dl-bar" + (dl.active ? " live" : "") }, el("i", { style: `width:${pct}%` })) : null),
    el("div", { class: "ver" }, el("span", {}, VERSION ? `v${VERSION}` : ""),
      el("span", { class: "privacy " + (cloud ? "off" : "on"), role: "status", title: privacy, "aria-label": privacy },
        el("i", { class: "lamp", "aria-hidden": "true" }), "Private · offline")));
}
async function setCompute(on) {
  const c = AI.cloud || {};
  if (!!c.enabled === on) return;
  if (on && !c.has_key) {
    toast("info", "Connect your cloud AI first", "Paste your Claude, ChatGPT or Gemini key in Settings, then switch to Cloud.");
    location.hash = "#/settings";
    return;
  }
  if (on && !(await modal({ icon: "cloud", title: `Switch to cloud compute (${c.name})?`,
    body: ["What you ask Jonny, and the page you're on, goes to your cloud AI account and is billed to it. Scripts go too only if you ticked Writing tools in Settings.",
      "Switch back to Local compute at any time."], actions: [["Stay local", false], ["Use cloud", true, true]] }))) return;
  try {
    await api.put("/api/cloud", { provider: c.provider, enabled: on });
    AI = await api.get("/api/ai/status");
    engineChip(); if (ASK.node) ASK.node.draw();
    toast(on ? "ai" : "ok", on ? `Cloud compute on: ${AI.cloud.name}` : "Local compute", on ? "Answers are marked Cloud." : "Everything runs on this computer again.");
  } catch (e) { toast("bad", "Couldn't switch", e.message); }
}
let JOBS_ACTIVE = 0;
function topbar(crumbs) {
  const bar = document.getElementById("topbar");
  put(bar, el("div", { class: "crumbs" }, crumbs.map((c, i) => [i ? el("span", { class: "sep" }, "/") : null, i === crumbs.length - 1 ? el("b", {}, c) : el("span", {}, c)])),
    el("button", { type: "button", class: "search-trigger", onclick: openPalette, "aria-label": `Search (${navigator.platform.startsWith("Mac") ? "Command K" : "Ctrl K"})` }, icon("search"), el("span", {}, "Search tools, scripts, actions"), el("kbd", {}, navigator.platform.startsWith("Mac") ? "⌘ K" : "Ctrl K")),
    el("div", { class: "top-actions" },
      el("a", { class: "icon-btn", href: "#/tool/coverage", title: JOBS_ACTIVE ? `${plural(JOBS_ACTIVE, "job")} in the queue` : "Coverage queue", "aria-label": "Coverage queue" }, icon("reel"), JOBS_ACTIVE ? el("span", { class: "badge" }, JOBS_ACTIVE) : null),
      el("a", { class: "icon-btn", href: "#/library", title: "Library", "aria-label": "Library" }, icon("library")),
      el("a", { class: "icon-btn", href: "#/settings", title: "Settings", "aria-label": "Settings" }, icon("settings"))));
}
async function pollJobs() {
  try { const r = await api.get("/api/jobs?kind=coverage&limit=1"); const n = (r.counts.queued || 0) + (r.counts.running || 0); if (n !== JOBS_ACTIVE) { JOBS_ACTIVE = n; const b = document.querySelector('.icon-btn[aria-label="Coverage queue"]'); if (b) { b.querySelector(".badge")?.remove(); if (n) b.append(el("span", { class: "badge" }, n)); } } } catch (e) { /* engine busy */ }
}

async function route() {
  const h = location.hash || "#/";
  buildNav(h.startsWith("#/run/") || h.startsWith("#/library") ? "#/library" : h.startsWith("#/room") ? "#/room" : h);
  engineChip();
  const [, kind, a, b] = h.split("/");
  const page = app(); page.classList.remove("page-enter"); void page.offsetWidth; page.classList.add("page-enter");
  if (COACH.started) coachRoute();
  const sh = document.querySelector(".main"); if (sh) { sh.style.scrollBehavior = "auto"; sh.scrollTop = 0; sh.style.scrollBehavior = ""; } window.scrollTo(0, 0);
  try {
    if (!kind) return await home();
    if (kind === "tool") return await tool(a);
    if (kind === "library") return await library(a);
    if (kind === "settings") return await settings();
    if (kind === "room") return await roomRoute(a, b);
    if (kind === "run") return await runView(a, b);
    await home();
  } catch (e) { put(app(), errBox(e)); }
}

/* ---------------- home ---------------- */
function ago(ts) {
  const d = new Date(String(ts).replace(" ", "T")); const m = (Date.now() - d) / 60000;
  if (!isFinite(m)) return "";
  if (m < 1) return "just now"; if (m < 60) return `${Math.round(m)} min ago`; if (m < 24 * 60) return `${Math.round(m / 60)} h ago`;
  if (m < 48 * 60) return "yesterday"; return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}
const stagger = (nodes) => nodes.map((n, i) => (n.style.setProperty("--i", i), n));
let SUITE_FILTER = "All";
async function home() {
  topbar(["Studio", "Home"]);
  const { runs: recent, total } = await api.get("/api/runs?limit=8").catch(() => ({ runs: [], total: 0 }));
  const own = CAT.tools.filter(t => !t.external);
  const working = own.filter(t => ["ready", "partial"].includes(status(t)[0])).length;
  const today = new Date().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" });
  const engine = AI.connected ? "Local compute" : null;   /* Tim, 13 Oct: no model names on screen; Settings has them */
  const cloudOn = !!(AI.cloud && AI.cloud.active && (AI.cloud.active.chat || AI.cloud.active.writing)), aiOn = AI.connected || cloudOn;
  const suite = el("div", { class: "suite stagger" });
  const chips = el("div", { class: "chips", role: "group", "aria-label": "Filter tools" });
  const drawSuite = () => {
    [...chips.children].forEach(c => c.setAttribute("aria-pressed", String(c.dataset.g === SUITE_FILTER)));
    put(suite, stagger(CAT.tools.filter(t => t.menu !== false && (SUITE_FILTER === "All" || t.group === SUITE_FILTER)).map(tile)));
  };
  ["All", ...CAT.groups].forEach(g => chips.append(el("button", { type: "button", class: "chip", "data-g": g, onclick: () => { SUITE_FILTER = g; drawSuite(); } }, g)));
  put(app(),
    el("section", { class: "marquee" },
      el("div", { class: "aurora", "aria-hidden": "true" }, el("i"), el("i"), el("i")),
      el("div", { class: "mq" },
        el("div", {},
          el("div", { class: "eyebrow" }, "Saracen Bridge Studio", el("span", { class: "opt" }, `· ${today}`)),
          el("h1", {}, "What are you working ", el("em", {}, "on?")),
          el("p", { class: "lede" }, "Every Saracen Bridge tool in one place. Run privately on this computer for the most security, or on Cloud for the most power: whatever goes to the cloud leaves this computer, and that always carries some risk."),
          el("div", { class: "mq-actions" },
            el("a", { class: "btn primary", href: "#/tool/coverage" }, icon("upload"), "Read a script"),
            el("button", { type: "button", class: "btn ghost", onclick: openPalette }, icon("search"), "Find anything", el("kbd", {}, navigator.platform.startsWith("Mac") ? "⌘ K" : "Ctrl K")),
            el("a", { class: "btn quiet", href: "#/library" }, "Library", icon("arrow")))),
        el("div", { class: "ledger" },
          el("div", {}, el("span", { class: "v" }, working, el("small", {}, `/ ${own.length}`)), el("span", { class: "l" }, "Tools working now")),
          el("a", { href: "#/library" }, el("span", { class: "v" }, fmt(total || 0)), el("span", { class: "l" }, "Saved in the library"), el("span", { class: "r" }, icon("arrow"))),
          el("a", { href: "#/settings" }, el("span", { class: "v" }, aiOn ? "On" : "Off"), el("span", { class: "l" }, AI.connected ? engine : cloudOn ? `${AI.cloud.name} · cloud` : "AI writing"),
            el("span", { class: "r" }, el("span", { class: "dot " + (aiOn ? "ok" : "warn") }), aiOn ? "" : "Set it up"))))),
    recent.length ? [el("div", { class: "section-title" }, "Continue", el("small", {}, "recent work")),
      el("div", { class: "continue stagger" }, stagger(recent.slice(0, 4).map(recentCard)))] : null,
    el("div", { class: "suite-head" }, el("div", { class: "section-title" }, "The Suite", el("small", {}, `${CAT.tools.length} tools`)), chips),
    suite);
  drawSuite();
}
function tile(t) {
  const a = el("a", { class: "tile", href: `#/tool/${t.id}` },
    el("div", { class: "top" }, el("span", { class: "glyph" }, toolIcon(t)), el("span", { class: "code" }, t.group)),
    el("div", { class: "t" }, t.name), el("div", { class: "d" }, t.tagline),
    el("div", { class: "foot" }, stateTag(t), el("span", { class: "go" }, icon("arrow"))));
  a.addEventListener("pointermove", e => {
    const r = a.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
    a.style.setProperty("--mx", `${e.clientX - r.left}px`); a.style.setProperty("--my", `${e.clientY - r.top}px`);
    if (CALM || e.pointerType !== "mouse") return;
    a.classList.add("tilting"); a.style.setProperty("--try", `${(x - .5) * 9}deg`); a.style.setProperty("--trx", `${(.5 - y) * 7}deg`);
  });
  a.addEventListener("pointerleave", () => { a.classList.remove("tilting"); a.style.setProperty("--try", "0deg"); a.style.setProperty("--trx", "0deg"); });
  return a;
}
function recentCard(r) {
  const s = r.summary || {};
  const t = toolById(r.tool);
  const facts = s.score !== undefined ? `${s.verdict} · ${s.score} / 100` : s.verdict ? `${s.verdict} · ${Number(s.composite).toFixed(1)} / 10` : s.pages !== undefined ? plural(s.pages, "page") : s.scene_count !== undefined ? `${s.scene_count} scenes · ${s.speaking_roles} roles` : (t ? t.name : r.tool);
  return el("a", { class: "recent-card", href: `#/run/${r.tool}/${r.id}` },
    el("span", { class: "ic" }, t ? toolIcon(t) : icon("doc")),
    el("div", { class: "t" }, r.title), el("div", { class: "f" }, el("b", {}, ago(r.created)), ` · ${facts}`));
}
const VERDICT_PILL = { Recommend: "PASS", Consider: "PRELIMINARY", Pass: "FAIL", Strong: "PASS", "Good with Revisions": "PRELIMINARY", "Needs Work": "WARN", "Not Yet Sales-Ready": "FAIL" };
function runList(runs) {
  return el("div", { class: "card flush list" }, runs.map(r => {
    const s = r.summary || {};
    const facts = s.scene_count !== undefined ? `${s.format} · ${s.pages_estimated ? "~" : ""}${fmt(s.pages)} pp · ${s.scene_count} scenes · ${s.speaking_roles} roles` : s.pages !== undefined ? `${s.pages}-page look book` : "";
    const v = s.verdict ? el("span", { class: "pill " + (VERDICT_PILL[s.verdict] || ""), style: "margin-left:10px" }, s.score !== undefined ? `${s.verdict} ${s.score}` : `${s.verdict} ${Number(s.composite).toFixed(1)}`) : null;
    return el("a", { href: `#/run/${r.tool}/${r.id}` },
      el("span", {}, el("span", { class: "ttl" }, r.title), v, el("span", { class: "meta" }, `${(toolById(r.tool) || { name: r.tool }).name}${facts ? " · " + facts : ""}`)),
      el("span", { class: "when" }, String(r.created).replace("T", " ").slice(0, 16)));
  }));
}

/* ---------------- tool page ---------------- */
async function tool(id) {
  const t = toolById(id);
  if (!t) return home();
  topbar([t.group, t.name]);
  const panel = el("div", { class: "card wide" });
  const history = el("div", {});
  const li = (cls, ic, items) => el("ul", { class: "plain " + cls }, items.map(n => el("li", {}, icon(ic), el("span", {}, n))));
  put(app(),
    el("h1", {}, t.name), el("p", { class: "lede" }, t.tagline),
    ((t.ai_built || []).length && !aiWrites()) ? el("div", { class: "notice" }, el("div", { class: "ic" }, icon("sparkle")),
      el("div", { class: "grow" }, el("div", {}, "Connect the AI engine to switch on: ", t.ai_built.map(x => /^(Saracen|BFI|AI|A\.I|F\.R|[A-Z]{2})/.test(x) ? x : x[0].toLowerCase() + x.slice(1)).join("; ")), el("div", { class: "sub" }, "Everything else on this page works now.")),
      el("a", { class: "btn sm", href: "#/settings" }, "Set up")) : null,
    el("div", { class: "cols" + (t.external ? " solo" : "") }, panel,
      t.external ? null : el("div", { class: "card side-card" },
        t.ready.length ? el("section", {}, el("h2", {}, "Works now"), li("ok", "check", t.ready)) : null,
        (t.ai_built || []).length ? el("section", {}, el("h2", {}, aiWrites() ? "Written by the AI engine" : "With the AI engine ", aiWrites() ? null : el("small", {}, "not connected")), li("ai", "sparkle", t.ai_built)) : null,
        t.needs_ai.length ? el("section", {}, el("h2", {}, "Coming soon"), li("soon", "clock", t.needs_ai)) : null,
        el("section", {}, el("h2", {}, "What it needs"), li("need", "file", t.needs)))),
    history);
  await (PANELS[id] || PANELS.ai_only)(panel, t);
  if (!t.external) {
    const { runs, total } = await api.get(`/api/runs?tool=${id}&limit=20`).catch(() => ({ runs: [], total: 0 }));
    if (runs.length) put(history, el("div", { class: "section-title" }, "History", el("small", {}, `${fmt(total)} saved`)), runList(runs),
      total > runs.length ? el("p", {}, el("a", { href: `#/library/${id}` }, `See all ${fmt(total)} in the Library`)) : null);
  }
}
function tabs(container, defs, start = 0) {
  const body = el("div", { style: "margin-top:20px" });
  const bar = el("div", { class: "tabs", role: "group" });
  const show = i => { [...bar.children].forEach((b, j) => b.setAttribute("aria-pressed", String(i === j))); put(body);
    container.closest(".cols")?.classList.toggle("wide-panel", !!defs[i][2]); defs[i][1](body); };   /* [label, draw, wide] */
  defs.forEach(([label], i) => bar.append(el("button", { type: "button", onclick: () => show(i) }, label)));
  container.append(bar, body); show(Math.min(start, defs.length - 1));
}

/* a multi-tick dropdown closes when you click anywhere else (1.1.3) */
document.addEventListener("click", e => document.querySelectorAll("details.ms[open]").forEach(d => { if (!d.contains(e.target)) d.removeAttribute("open"); }));

/* ---------------- shared: script intake ---------------- */
function scriptIntake(box, toolId, after) {
  const results = el("div", {});
  const input = el("input", { type: "file", multiple: true, accept: ".pdf,.fdx,.fountain,.spmd,.txt", style: "display:none" });
  const folder = el("input", { type: "file", webkitdirectory: true, style: "display:none" });
  const drop = el("div", { class: "drop" }, el("div", { class: "art" }, icon("upload")), el("div", { class: "big" }, "Drop scripts here"),
    el("p", {}, "PDF, Final Draft (.fdx) or Fountain. Add one or a thousand: scripts already read are skipped, so a stopped batch picks up where it left off."),
    el("div", { class: "row" }, el("button", { type: "button", class: "btn primary", onclick: () => input.click() }, "Choose files"),
      el("button", { type: "button", class: "btn", onclick: () => folder.click() }, icon("folder"), "Choose a folder")));
  const rows = [];
  async function run(files) {
    const list = [...files].filter(f => /\.(pdf|fdx|fountain|spmd|txt)$/i.test(f.name));
    if (!list.length) return toast("bad", "No scripts in that selection", "Use PDF, Final Draft (.fdx) or Fountain files.");
    let skipped = 0;
    const tbl = el("tbody", {});
    const prog = el("div", { style: "margin-top:18px" }, el("div", { class: "muted small", style: "margin-bottom:8px" }), el("div", { class: "clapper" }));
    put(results, prog, el("div", { class: "card flush", style: "margin-top:14px" }, el("div", { class: "scroll" }, el("table", {}, el("thead", {}, el("tr", {}, ["Script", "Format", "#Pages", "#Scenes", "#Speaking roles", "#INT / EXT", "#Day / Night", ""].map(h => h.startsWith("#") ? el("th", { class: "num" }, h.slice(1)) : el("th", {}, h)))), tbl))));
    let base = "";
    const ocrTick = setInterval(async () => {          /* 1.0.6: a scanned script is read page by page; say how far it is */
      try {
        const o = await api.get("/api/tools/script/ocr");
        prog.firstChild.textContent = base + o.reading.map(r => ` Scanned script${r.file ? ` (${r.file})` : ""}: reading page ${Math.min(r.done + 1, r.pages)} of ${r.pages} by OCR.`).join("");
      } catch (e) { /* the line keeps its last text */ }
    }, 1500);
    for (let i = 0; i < list.length; i += 10) {
      base = `Reading ${Math.min(i + 10, list.length)} of ${list.length}…`;
      prog.firstChild.textContent = base;
      const fd = new FormData(); fd.append("tool", toolId);
      list.slice(i, i + 10).forEach(f => fd.append("files", f, f.name));
      try {
        for (const r of await api.form("/api/tools/script/intake", fd)) {
          rows.push(r);
          if (r.duplicate) skipped++;
          tbl.append(r.error ? el("tr", {}, el("td", {}, r.file), el("td", { colspan: 7 }, el("span", { class: "pill FAIL st" }, r.error))) :
            el("tr", {}, el("td", {}, el("b", {}, r.title), r.duplicate ? el("div", { class: "small muted" }, "Already in the Library") : null,
                (r.int || 0) + (r.ext || 0) === 0 ? el("div", { class: "small warn-text" }, "No INT./EXT. scene headings: this may be a treatment or a pitch deck. A deck belongs in ",
                  el("a", { href: "#/tool/lookbook" }, "Look Book Analytics"), ".") : null,
                /OCR/.test(r.format || "") ? el("div", { class: "small muted" }, "Scanned: read by OCR. Check names and headings against the script.") : null), el("td", {}, r.format), el("td", { class: "num" }, r.pages_estimated ? `~${fmt(r.pages)}` : fmt(r.pages)),
              el("td", { class: "num" }, r.scene_count), el("td", { class: "num" }, r.speaking_roles), el("td", { class: "num" }, `${r.int} / ${r.ext}`),
              el("td", { class: "num" }, `${r.day} / ${r.night}`), el("td", {}, el("a", { href: `#/run/${toolId}/${r.run_id}` }, "Open"))));
        }
      } catch (e) { tbl.append(el("tr", {}, el("td", { colspan: 8 }, errBox(e)))); }
    }
    clearInterval(ocrTick);
    const failed = rows.filter(r => r.error).length, saved = rows.length - skipped - failed;
    put(prog, el("div", { class: "muted small" }, `${plural(saved, "script")} read and saved to the Library.` + (skipped ? ` ${skipped} already there, skipped.` : "") + (failed ? ` ${failed} could not be read.` : "")));
    toast(failed && !saved ? "bad" : "ok", `${saved} script${saved === 1 ? "" : "s"} added to the Library`, [skipped ? `${skipped} already there, skipped. ` : "", failed ? `${failed} could not be read.` : ""].join("") || "Open any row to see its breakdown.");
    if (after) { const extra = after(rows); if (extra) results.append(extra); }
  }
  input.addEventListener("change", () => input.files.length && run(input.files));
  folder.addEventListener("change", () => folder.files.length && run(folder.files));
  drop.addEventListener("dragover", e => { e.preventDefault(); drop.classList.add("over"); });
  drop.addEventListener("dragleave", () => drop.classList.remove("over"));
  drop.addEventListener("drop", e => { e.preventDefault(); drop.classList.remove("over"); run(e.dataTransfer.files); });
  box.append(drop, input, folder, results);
}
function searchTable(box, { placeholder, url, cols, extra }) {
  const q = el("input", { type: "search", placeholder, "aria-label": placeholder, autocomplete: "off", style: "flex:1;min-width:220px" });
  const out = el("div", { style: "margin-top:16px" });
  let seq = 0, timer;
  const go = async () => {
    const my = ++seq;
    try {
      const data = await api.get(url(q.value.trim()));
      if (my !== seq) return;                                   // a newer keystroke already asked
      const rows = Array.isArray(data) ? data : data.rows;
      put(out, el("p", { class: "muted small", style: "margin:0 0 10px" }, plural(rows.length, "result")), el("div", { class: "card flush" }, table(cols.map(c => c[2] ? "#" + c[1] : c[1]), rows.map(r => el("tr", {}, cols.map(([k, , num], j) => el("td", { class: num ? "num" : null }, num ? fmt(r[k]) : j === 0 ? el("b", {}, r[k] ?? "—") : (r[k] ?? "—"))))))));
    } catch (e) { if (my === seq) put(out, errBox(e)); }
  };
  q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(go, 160); });
  q.addEventListener("keydown", e => { if (e.key === "Enter") { clearTimeout(timer); go(); } });
  box.append(el("div", { class: "row" }, q, extra || null), out);
  go();
}

/* ---------------- Brand Integration: the database and a shortlist ----------------
   Tim, 13 Oct: click a brand and it highlights and is added; pick as many as you like. The shortlist is kept on this
   PC, downloads as a CSV, and a script read on Script intake takes it as that film's brand targets. */
function brandDatabase(box) {
  let picked = [];
  const isOn = id => picked.some(x => x.brand_id === id);
  const bar = el("div", { class: "shortlist" });
  const q = el("input", { type: "search", placeholder: "Brand or parent company", "aria-label": "Brand or parent company", autocomplete: "off", style: "flex:1;min-width:220px" });
  const out = el("div", { style: "margin-top:16px" });
  let rows = [], seq = 0, timer;
  const save = async next => {
    const before = picked; picked = next; drawBar(); mark();
    try { picked = (await api.put("/api/brand/shortlist", { ids: next.map(x => x.brand_id) })).brands; }
    catch (e) { picked = before; toast("bad", "Couldn't save the shortlist", e.message); }
    drawBar(); mark();
  };
  const toggle = r => save(isOn(r.brand_id) ? picked.filter(x => x.brand_id !== r.brand_id) : [...picked, r]);
  const drawBar = () => put(bar,
    el("div", { class: "sl-head" }, el("h2", { style: "margin:0" }, icon("brand"), "Shortlist", el("span", { class: "count" }, picked.length)),
      picked.length ? el("div", { class: "row", style: "gap:8px" },
        el("a", { class: "btn sm", href: "/api/brand/shortlist.csv", download: "" }, icon("download"), "Download CSV"),
        el("button", { type: "button", class: "btn sm quiet", onclick: () => save([]) }, "Clear")) : null),
    picked.length ? el("div", { class: "sl-chips" }, picked.map(x => el("span", { class: "sl-chip" }, x.brand_name,
        el("button", { type: "button", "aria-label": `Remove ${x.brand_name}`, title: "Remove", onclick: () => toggle(x) }, icon("x")))))
      : el("p", { class: "muted small", style: "margin:8px 0 0" }, "Click a brand below to add it. Pick as many as you like: a script read on Script intake takes them as its brand targets."));
  const mark = () => out.querySelectorAll("tr.pick").forEach(tr => { const on = isOn(tr.dataset.id); tr.setAttribute("aria-selected", String(on)); tr.classList.toggle("on", on); });
  const draw = () => put(out, el("p", { class: "muted small", style: "margin:0 0 10px" }, plural(rows.length, "result"), rows.length ? " · click a brand to add or remove it" : ""),
    el("div", { class: "card flush" }, table(["Brand", "Category", "HQ", "Priority", "Film-placement evidence"], rows.map(r => el("tr", {
      class: "pick", "data-id": r.brand_id, tabindex: "0", role: "button", "aria-selected": String(isOn(r.brand_id)), title: "Add to or remove from the shortlist",
      onclick: () => toggle(r), onkeydown: e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(r); } } },
      el("td", {}, el("span", { class: "pick-name" }, el("span", { class: "tick" }, icon("check")), el("b", {}, r.brand_name))),
      el("td", {}, r.category || "—"), el("td", {}, r.hq_country || "—"), el("td", {}, r.priority || "—"), el("td", { class: "evidence" }, r.evidence_statement || "—"))))));
  const go = async () => {
    const my = ++seq;
    try { const data = await api.get(`/api/lookup/brands?q=${encodeURIComponent(q.value.trim())}`); if (my !== seq) return; rows = data; draw(); mark(); }
    catch (e) { if (my === seq) put(out, errBox(e)); }
  };
  q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(go, 160); });
  q.addEventListener("keydown", e => { if (e.key === "Enter") { clearTimeout(timer); go(); } });
  box.append(bar, el("div", { class: "row", style: "margin-top:18px" }, q), out);
  drawBar();
  api.get("/api/brand/shortlist").then(r => { picked = r.brands; drawBar(); mark(); }).catch(() => {});
  go();
}
function brandTargets(r) {
  /* a brand script's targets: the shortlist when it was read, replaceable with today's shortlist */
  const box = el("div", { class: "card", style: "margin-top:24px" });
  const draw = list => put(box,
    el("div", { class: "sl-head" }, el("h2", { style: "margin:0" }, icon("brand"), "Brand targets", el("span", { class: "count" }, list.length)),
      el("div", { class: "row", style: "gap:8px" },
        list.length ? el("a", { class: "btn sm", href: `/api/brand/shortlist.csv?run=${encodeURIComponent(r.id)}`, download: "" }, icon("download"), "Download CSV") : null,
        el("button", { type: "button", class: "btn sm quiet", onclick: async () => {
          try { const s = await api.get("/api/brand/shortlist"); const t = await api.put(`/api/runs/brand/${r.id}/targets`, { ids: s.brands.map(x => x.brand_id) });
            draw(t.brand_targets); toast("ok", "Brand targets updated", `${plural(t.brand_targets.length, "brand")} from your shortlist.`); }
          catch (e) { toast("bad", "Couldn't update the targets", e.message); } } }, "Use my current shortlist"))),
    list.length ? el("div", { class: "sl-chips" }, list.map(x => el("span", { class: "sl-chip static", title: x.evidence_statement || "" }, x.brand_name, el("small", {}, x.category || ""))))
      : el("p", { class: "muted small", style: "margin:8px 0 0" }, "No brands picked for this script. Pick them on the Brand database tab, then press Use my current shortlist."),
    el("p", { class: "muted small", style: "margin:12px 0 0" }, "Scene-by-scene spotting below prefers these brands where they fit. Placement in the cut with F.R.A.T. is coming soon."));
  draw(r.outputs.brand_targets || []);
  return box;
}

/* ---------------- AI jobs on one script: a live line while queued or running (1.0.7) ---------------- */
function jobWatch(kind, tool, runId, onDone) {
  const line = el("div", { style: "margin-top:14px" });
  let timer = null;
  const tick = async () => {
    let r; try { r = await api.get(`/api/jobs?kind=${kind}&limit=40`); } catch (e) { return; }
    const j = r.jobs.find(x => x.tool === tool && x.run_id === runId && ["queued", "running", "error", "done"].includes(x.status));
    if (!j || j.status === "done") { put(line); if (j && line.dataset.seen) onDone(); return; }
    line.dataset.seen = "1";
    if (j.status === "error") return put(line, el("p", { class: "note FAIL" }, "The last attempt failed: ", errorLine(j.error)));
    put(line, el("div", { class: "row", style: "align-items:center;gap:12px" }, el("span", { class: "pill AI" }, j.status === "running" ? "Working" : "Waiting"),
      el("span", { class: "small" }, j.status === "running" ? (j.progress || "Starting") : "In the queue behind other AI work"),
      el("button", { type: "button", class: "btn sm quiet", onclick: async () => { await api.post(`/api/jobs/${j.id}/cancel`, {}); toast("info", "Stopped", j.title); tick(); } }, "Cancel")),
      el("div", { class: "clapper", style: "margin-top:10px" }));
    clearTimeout(timer); timer = setTimeout(() => document.body.contains(line) && tick(), 3000);
  };
  line.start = tick; setTimeout(tick, 0);
  return line;
}
const copyBtn = text => el("button", { type: "button", class: "btn sm quiet", onclick: async () => {
  try { await navigator.clipboard.writeText(text); toast("ok", "Copied"); } catch (e) { toast("bad", "Couldn't copy", "Select the text and copy it instead."); } } }, "Copy");

/* ---------------- Brand: scene-by-scene opportunities and outreach drafts (1.0.7) ---------------- */
let BRAND_OPTS = null;
async function brandSpot(r) {
  const box = el("div", { class: "card", style: "margin-top:24px" });
  BRAND_OPTS = BRAND_OPTS || await api.get("/api/tools/brand/spot/options").catch(() => ({ categories: [], ratings: ["Not decided"] }));
  const res = r.outputs.brand_spotting;
  const prev = (res || {}).options || {};
  const avoid = new Set(prev.avoid || []);
  const chips = el("div", { class: "tabs", role: "group", "aria-label": "Brand categories to avoid", style: "flex-wrap:wrap;height:auto;margin:0" },
    el("span", { class: "lbl" }, "Avoid"), BRAND_OPTS.categories.map(c => { const b = el("button", { type: "button", "aria-pressed": String(avoid.has(c)), onclick: () => { avoid.has(c) ? avoid.delete(c) : avoid.add(c); b.setAttribute("aria-pressed", String(avoid.has(c))); } }, c); return b; }));
  const rating = el("select", { "aria-label": "Intended rating" }, BRAND_OPTS.ratings.map(x => el("option", { value: x, selected: x === (prev.rating || "Not decided") }, x)));
  const withhold = el("input", { type: "checkbox", checked: !!prev.withhold_title });
  const watch = jobWatch("brandspot", "brand", r.id, () => route());
  const go = async ev => {
    const btn = ev.currentTarget; btn.disabled = true;
    try { await api.post("/api/tools/brand/spot", { run_ids: [r.id], mode: MODE, options: { avoid: [...avoid], rating: rating.value, withhold_title: withhold.checked } });
      toast("ai", "Spotting queued", `Gemma reads every scene on ${runsOn()}. You can keep working.`); pollJobs(); watch.start(); }
    catch (e) { toast("bad", "Couldn't start", el("span", {}, e.message, " ", el("a", { href: "#/settings" }, "Settings"))); }
    btn.disabled = false;
  };
  const form = el("div", {}, el("div", { style: "margin-top:14px" }, chips),
    el("div", { class: "row", style: "margin-top:14px;align-items:flex-end;gap:14px" }, el("label", { class: "f" }, "Intended rating", rating),
      el("label", { class: "row small", style: "gap:8px;align-items:center" }, withhold, "Keep the title out of outreach drafts"), modeSwitch(),
      el("button", { type: "button", class: "btn primary", onclick: go }, icon("sparkle"), res ? "Spot again" : "Spot opportunities")));
  if (!res) {
    put(box, el("h2", { style: "margin:0" }, icon("sparkle"), "Scene-by-scene opportunities"),
      el("p", { class: "muted small", style: "margin:8px 0 0" }, "Gemma reads every scene and lists the brand moments it genuinely supports, as the Saracen Bridge brief asks: scene and page, the exact item, placement type, why it fits, what would change, risks and scores, with a primary target and two alternatives from the Saracen Bridge brand database, then ranks the brands and drafts outreach to the top five. Nothing is sent."),
      form, watch);
    return box;
  }
  const brand = id => (res.targets.find(t => t.brand_id === id) || {}).brand_name || id;
  const need = res.opportunities.filter(o => !o.in_script).length;
  const mw = res.made_with || {};
  put(box, el("div", { class: "sl-head" }, el("h2", { style: "margin:0" }, icon("sparkle"), "Scene-by-scene opportunities", el("span", { class: "count" }, res.opportunities.length)),
      el("a", { class: "btn sm", href: `/api/runs/brand/${r.id}/opportunities.xlsx` }, icon("download"), ".xlsx")),
    el("div", { class: "kpis", style: "margin-top:14px" }, kpi("Opportunities", fmt(res.opportunities.length), true), kpi("Scenes with one", `${res.scenes_with_opportunities} of ${res.scenes_read}`),
      kpi("Already in the script", fmt(res.opportunities.length - need)), kpi("Need a script change", fmt(need)), kpi("Brands matched", fmt(res.targets.length))),
    el("p", { class: "muted small", style: "margin:6px 0 0" }, `Read ${res.date} · ${mw.mode || "quick"} reasoning · ${(mw.seconds || 0) < 120 ? fmt(mw.seconds || 0) + " s" : Math.round(mw.seconds / 60) + " min"}. Brands only from the Saracen Bridge database; cash values to price; drafts not sent.${res.options.avoid.length ? " Avoided: " + res.options.avoid.join(", ") + "." : ""}`),
    res.checks.map(c => el("p", { class: "note PRELIMINARY" }, c)),
    el("h3", { style: "margin:22px 0 8px" }, "Opportunity register"),
    table(["ID", "Scene", "Moment and item", "Placement", "Targets", "#F", "#V", "#Priority"], res.opportunities.map(o => el("tr", {},
      el("td", { class: "mono small", style: "white-space:nowrap" }, o.id), el("td", { class: "small" }, `${o.scene} · p${o.page_estimated ? "~" : ""}${o.page}`, el("div", { class: "muted" }, o.scene_heading)),
      el("td", {}, el("b", {}, o.item), o.source === "named in the script" ? el("span", { class: "pill PRELIMINARY", style: "margin-left:8px" }, "clearance") : null,
        el("div", { class: "small" }, o.moment), el("div", { class: "small muted" }, o.narrative_reason),
        o.in_script ? null : el("div", { class: "small warn-text" }, "Needs a script change: ", o.creative_change), o.risks && !/^none/i.test(o.risks) ? el("div", { class: "small muted" }, "Risks: ", o.risks) : null),
      el("td", { class: "small" }, o.placement, el("div", { class: "muted" }, o.category)),
      el("td", { class: "small" }, o.targets.length ? [el("b", {}, brand(o.targets[0])), o.targets.slice(1).map(t => el("div", { class: "muted" }, brand(t)))] : el("span", { class: "muted" }, o.fallback)),
      el("td", { class: "num" }, o.feasibility), el("td", { class: "num" }, o.value), el("td", { class: "num" }, el("b", {}, fmt(o.priority, 1)))))),
    el("h3", { style: "margin:22px 0 8px" }, "Target brands"),
    table(["#", "Brand", "Group", "Primary on", "Angle and next action", "Route"], res.targets.slice(0, 15).map(t => el("tr", {},
      el("td", { class: "num" }, t.rank), el("td", {}, el("b", {}, t.brand_name), el("div", { class: "small muted" }, t.category), t.targeted ? el("span", { class: "pill AI" }, "your target") : null),
      el("td", { class: "small" }, t.group), el("td", { class: "small mono" }, t.opportunity_ids.join(", ") || "—", t.alternative_on.length ? el("div", { class: "muted" }, "alt: " + t.alternative_on.join(", ")) : null),
      el("td", { class: "small" }, t.outreach_angle || "—", t.next_action ? el("div", { class: "muted" }, "Next: ", t.next_action) : null),
      el("td", { class: "small muted" }, t.route)))),
    el("h3", { style: "margin:22px 0 8px" }, "Outreach drafts", el("span", { class: "muted small" }, " · not sent; contacts to be verified")),
    res.outreach.map(d => el("details", { class: "lb-more", style: "margin-top:10px" }, el("summary", {}, el("b", {}, d.brand_name), el("span", { class: "muted small" }, ` · ${d.opportunity_ids.join(", ")} · ${d.subject}`)),
      el("div", { style: "margin-top:12px" }, el("p", { class: "small muted" }, d.route),
        [["Subject", d.subject], ["First email", d.email], ["Follow-up", d.follow_up], ["LinkedIn", d.linkedin], ["Call brief", d.call_brief.map(x => "• " + x).join("\n")]].map(([l, t]) =>
          el("div", { style: "margin-top:12px" }, el("div", { class: "row", style: "justify-content:space-between;align-items:center" }, el("b", { class: "small" }, l), copyBtn(t)),
            el("div", { class: "small", style: "white-space:pre-wrap;margin-top:4px" }, t)))))),
    el("details", { class: "lb-more", style: "margin-top:22px" }, el("summary", {}, "Spot again", el("span", { class: "muted small" }, " with other settings")), form), watch);
  return box;
}

/* ---------------- shared: type-ahead name finder ----------------
   Tim, 13 Oct: type "chris" and the list narrows to the Chrises; click one (or arrow + Enter) and their profile fills in. */
const savedAt = v => { const d = new Date(String(v)); return isNaN(d) ? String(v).replace("T", " ") : d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) + ", " + d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }); };
const dateOnly = v => { if (!v) return "—"; const d = new Date(String(v).slice(0, 10) + "T00:00:00"); return isNaN(d) ? String(v).slice(0, 10) : d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }); };
const usd = v => { if (v === null || v === undefined || v === "") return "—"; const n = Number(v);
  return n >= 1e6 ? "$" + (n / 1e6).toFixed(n >= 1e8 ? 0 : 1).replace(/\.0$/, "") + "m" : n >= 1e3 ? "$" + Math.round(n / 1e3) + "k" : "$" + fmt(n); };
const foldText = t => String(t || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
function markMatch(name, q) {
  /* bold the typed letters inside the name, accents ignored ("timothee" lights up "Timothée") */
  const f = [...String(name)].map(c => foldText(c));
  const flat = f.join(""), hit = new Array(f.length).fill(false);
  foldText(q).split(/\s+/).filter(Boolean).forEach(w => { const at = flat.indexOf(w); if (at < 0) return; let pos = 0;
    f.forEach((c, i) => { if (pos + c.length > at && pos < at + w.length) hit[i] = true; pos += c.length; }); });
  const out = []; [...String(name)].forEach((c, i) => { const last = out[out.length - 1];
    if (last && last.hit === hit[i]) last.text += c; else out.push({ hit: hit[i], text: c }); });
  return out.map(p => p.hit ? el("mark", {}, p.text) : p.text);
}
let FINDER_N = 0;
function finder(box, { label, placeholder, search, name, meta, open, hint }) {
  const id = "finder" + (++FINDER_N);
  const input = el("input", { type: "search", placeholder, "aria-label": label, role: "combobox", "aria-autocomplete": "list", "aria-expanded": "false",
    "aria-controls": id, autocomplete: "off", spellcheck: "false" });
  const list = el("ul", { class: "finder-list", id, role: "listbox", "aria-label": label, hidden: true });
  const out = el("div", { class: "finder-out" }, el("div", { class: "finder-hint" }, icon("search"), el("span", {}, hint)));
  let items = [], act = -1, seq = 0, timer, shown = "";
  const close = () => { list.hidden = true; input.setAttribute("aria-expanded", "false"); input.removeAttribute("aria-activedescendant"); act = -1; };
  const mark = i => {
    act = i;
    [...list.children].forEach((li, j) => li.setAttribute("aria-selected", String(j === i)));
    if (i >= 0 && list.children[i]) { input.setAttribute("aria-activedescendant", `${id}-${i}`); list.children[i].scrollIntoView({ block: "nearest" }); }
  };
  const pick = async i => {
    const it = items[i];
    if (!it) return;
    input.value = shown = name(it); close();
    put(out, el("div", { class: "finder-hint" }, el("span", { class: "clapper sm" }), el("span", {}, `Opening ${name(it)}…`)));
    try { await open(it, out); } catch (e) { put(out, errBox(e)); }
  };
  const draw = q => {
    put(list, items.length ? items.map((it, i) => el("li", { id: `${id}-${i}`, role: "option", "aria-selected": "false",
      onpointerdown: e => { e.preventDefault(); pick(i); }, onpointermove: () => act !== i && mark(i) },
      el("span", { class: "nm" }, markMatch(name(it), q)), el("span", { class: "mt" }, meta(it))))
      : el("li", { class: "none", role: "option", "aria-disabled": "true" }, `No one matching “${q}” in the Saracen Bridge database`));
    list.hidden = false; input.setAttribute("aria-expanded", "true"); mark(items.length ? 0 : -1);
  };
  const run = async () => {
    const q = input.value.trim(), my = ++seq;
    if (!q) { items = []; close(); return; }
    try { const r = await api.get(search(q)); if (my !== seq) return; items = r; draw(q); }
    catch (e) { if (my === seq) { close(); put(out, errBox(e)); } }
  };
  input.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(run, 120); });
  input.addEventListener("keydown", e => {
    if (e.key === "ArrowDown") { e.preventDefault(); if (list.hidden) { clearTimeout(timer); run(); } else mark(Math.min(items.length - 1, act + 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); if (!list.hidden) mark(Math.max(0, act - 1)); }
    else if (e.key === "Enter") { e.preventDefault(); if (!list.hidden && act >= 0) pick(act); else if (input.value.trim() !== shown) { clearTimeout(timer); run(); } }
    else if (e.key === "Escape" && !list.hidden) { e.preventDefault(); e.stopPropagation(); close(); }
  });
  input.addEventListener("focus", () => { if (input.value.trim() && input.value.trim() !== shown) run(); });
  input.addEventListener("blur", () => setTimeout(close, 150));
  box.append(el("div", { class: "finder" }, el("span", { class: "finder-ic" }, icon("search")), input, list), out);
  setTimeout(() => input.focus(), 30);
  return { input, out };
}
const facts = pairs => el("dl", { class: "facts" }, pairs.filter(([, v]) => v !== null && v !== undefined && v !== "").map(([k, v]) => [el("dt", {}, k), el("dd", {}, v)]));
const sourceLinks = text => String(text || "").split(/[;\s]+/).filter(u => /^https?:\/\//.test(u)).map(u => { try { return el("a", { href: u, class: "src-link" }, new URL(u).host.replace(/^www\./, "")); } catch (e) { return null; } });
/* Jon's attachment certainty ladder (Sales Agent instructions; Sales Valuation Engine v4.1, ACTOR_IMPORT / DIRECTOR_IMPORT):
   a name counts toward the sales estimate only as far as the deal has gone. */
const LADDER = [["Wish list", 0], ["Informal interest", .15], ["Availability confirmed", .3], ["Offer submitted", .5], ["Letter of intent", .7], ["Conditional agreement", .85], ["Signed agreement", 1], ["Pay-or-play", 1]];
const ladderWeight = k => (LADDER.find(([n]) => n === k) || [k, 0])[1];
/* The package being put together for a sales estimate (1.0.7). Tim, 15 Oct: "we need to attach multiple actors: when we
   choose signed talent it should attach it and then let me check other actors so we can get a proper estimate".
   Choosing an attachment status on an actor's or director's profile attaches them; the package stays on this computer
   until it goes into a valuation (Territory valuation, where it is saved with the estimate). */
let SALES_PKG = null, SALES_PKG_APPLY = false;
const PKG_WATCH = new Set();
function salesPkg() {
  if (!SALES_PKG) { try { SALES_PKG = JSON.parse(localStorage.getItem("sb-sales-package") || "null"); } catch (e) { SALES_PKG = null; }
    if (!SALES_PKG || !Array.isArray(SALES_PKG.actors) || !Array.isArray(SALES_PKG.directors)) SALES_PKG = { actors: [], directors: [] }; }
  return SALES_PKG;
}
function pkgSave() { try { localStorage.setItem("sb-sales-package", JSON.stringify(SALES_PKG)); } catch (e) { /* private window */ } PKG_WATCH.forEach(f => { try { f(); } catch (e) { PKG_WATCH.delete(f); } }); }
function pkgFind(kind, name) { return salesPkg()[kind].find(x => x.name.toLowerCase() === String(name).toLowerCase()); }
function pkgAttach(kind, name, status, extra = {}) {
  const pk = salesPkg(), had = pkgFind(kind, name);
  if (had) Object.assign(had, { attachment: status }, extra); else pk[kind].push(Object.assign({ name, attachment: status }, extra));
  pkgSave();
  return !had;
}
function pkgRemove(kind, name) { const pk = salesPkg(); pk[kind] = pk[kind].filter(x => x.name.toLowerCase() !== String(name).toLowerCase()); pkgSave(); }
function attachment(who, kind, extra = {}) {
  const cur = pkgFind(kind, who);
  const sel = el("select", { "aria-label": `${who}: attachment status` }, LADDER.map(([k]) => el("option", { selected: cur && cur.attachment === k }, k)));
  const steps = el("div", { class: "ladder", "aria-hidden": "true" }, LADDER.map(([k, v]) => el("i", { title: `${k}: ${Math.round(v * 100)}%` })));
  const said = el("div", { class: "ladder-v" }), act = el("div", { class: "row", style: "gap:10px;margin-top:12px;align-items:center" });
  const draw = () => {
    const i = sel.selectedIndex, v = LADDER[i][1], on = pkgFind(kind, who);
    [...steps.children].forEach((x, j) => x.classList.toggle("on", j <= i && v > 0));
    put(said, el("b", {}, `${Math.round(v * 100)}%`), v === 0 ? " · a wish-list name adds nothing to the sales estimate yet" : v === 1 ? " · counts in full" : ` of ${who}'s value counts toward the sales estimate`);
    put(act, on ? [el("span", { class: "pill PASS" }, icon("check"), `In the package · ${on.attachment}`),
        el("button", { type: "button", class: "btn sm quiet", onclick: () => { pkgRemove(kind, who); draw(); toast("info", `${who} taken out of the package`); } }, "Remove")]
      : el("button", { type: "button", class: "btn sm primary", onclick: () => attach() }, icon("plus"), "Attach to the package"));
  };
  const attach = () => {
    const isNew = pkgAttach(kind, who, LADDER[sel.selectedIndex][0], extra);
    draw();
    toast("ok", isNew ? `${who} attached` : `${who}: ${LADDER[sel.selectedIndex][0]}`, `${LADDER[sel.selectedIndex][0]}. Look up the next ${kind === "actors" ? "actor" : "director"} above, or press Value this package.`);
    const f = document.querySelector(".finder input"); if (f) { f.focus(); f.select(); }
  };
  sel.addEventListener("change", attach);                  /* choosing a status attaches (Tim: "it should attach it") */
  draw();
  return [el("h3", {}, "Attachment"), el("div", { class: "attach" }, sel, el("div", { class: "grow" }, steps, said)), act,
    el("p", { class: "muted small", style: "margin:8px 0 0" }, "The Saracen Bridge certainty ladder: a name is counted only as far as the deal has gone. Choosing a status attaches the name to the package for this estimate.")];
}
/* the package so far, above the actor and director finders */
function pkgBar() {
  const box = el("div", { class: "card pkg-bar", style: "margin-bottom:18px" });
  const draw = () => {
    const pk = salesPkg(), n = pk.actors.length + pk.directors.length;
    const chip = (kind, x) => el("span", { class: "sl-chip" }, x.name, el("small", {}, `${x.attachment} · ${Math.round(ladderWeight(x.attachment) * 100)}%`),
      el("button", { type: "button", "aria-label": `Remove ${x.name}`, title: "Remove from the package", onclick: () => { pkgRemove(kind, x.name); } }, icon("x")));
    put(box, el("div", { class: "sl-head" }, el("h2", { style: "margin:0" }, icon("users"), "Package for this estimate", el("span", { class: "count" }, n)),
        el("div", { class: "row", style: "gap:8px" },
          n ? el("button", { type: "button", class: "btn sm quiet", onclick: () => { SALES_PKG = { actors: [], directors: [] }; pkgSave(); } }, "Clear") : null,
          el("button", { type: "button", class: "btn sm primary", disabled: !n, onclick: () => { SALES_PKG_APPLY = true; SALES_OPEN = true; route(); } }, icon("sales"), "Value this package"))),
      n ? el("div", { class: "sl-chips" }, pk.actors.map(x => chip("actors", x)), pk.directors.map(x => chip("directors", x)))
        : el("p", { class: "muted small", style: "margin:8px 0 0" }, "Look up an actor or director below and choose their attachment status: they're added here. Add as many as the package has, then value it."),
      n ? el("p", { class: "muted small", style: "margin:10px 0 0" }, `${plural(pk.actors.length, "actor")}, ${plural(pk.directors.length, "director")}. Signed and pay-or-play count in full; a wish-list name counts for nothing until the deal moves. The Saracen Bridge engine works out the cast and director factors when you value the package.`) : null);
  };
  const watch = () => { if (!document.body.contains(box)) { PKG_WATCH.delete(watch); return; } draw(); };
  PKG_WATCH.add(watch); draw();
  return box;
}
function actorCard(a) {
  const bars = [["Lead carry", a.lead_carry], ["International presales", a.international_presales], ["Territory breadth", a.territory_breadth], ["Global theatrical", a.global_theatrical],
    ["Streaming / platform", a.streaming_platform], ["Recent momentum", a.recent_momentum], ["Awards & prestige", a.awards_prestige], ["Supporting value", a.supporting_value]];
  const links = sourceLinks(a.primary_source);
  return el("div", { class: "profile" },
    el("div", { class: "profile-head" },
      el("div", {}, el("h2", {}, a.actor), el("div", { class: "muted" }, [a.sales_role, a.sales_influence_class].filter(Boolean).join(" · "))),
      el("span", { class: "tier" }, el("small", {}, "Tier"), a.commercial_tier || "—")),
    el("div", { class: "kpis", style: "margin-top:18px" },
      el("div", { class: "kpi edge" }, el("div", { class: "l" }, "Indicative cash fee"), el("div", { class: "v", title: `USD ${fmt(a.indicative_cash_fee_low_usd)} – ${fmt(a.indicative_cash_fee_high_usd)}` }, `${usd(a.indicative_cash_fee_low_usd)}–${usd(a.indicative_cash_fee_high_usd).slice(1)}`)),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Sensible budget from"), el("div", { class: "v", title: "USD " + fmt(a.minimum_sensible_budget_usd) }, usd(a.minimum_sensible_budget_usd))),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Optimal budget floor"), el("div", { class: "v", title: "USD " + fmt(a.optimal_budget_floor_usd) }, usd(a.optimal_budget_floor_usd))),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Cast value"), el("div", { class: "v" }, fmt(a.composite_cast_value, 1), el("small", {}, " / 100")))),
    el("div", { class: "profile-cols" },
      el("div", {}, el("h3", {}, "Sales strength"), el("div", { class: "bars" }, bars.map(([k, v]) => el("div", { class: "bar" }, el("span", { class: "k" }, k), el("span", { class: "t" }, el("i", { style: `width:${Number(v) || 0}%` })), el("span", { class: "v" }, v ?? "—"))))),
      el("div", {}, el("h3", {}, "Profile"), facts([["Market", a.primary_market], ["Playing age", a.approx_playing_age], ["English-language fit", a.english_language_fit],
        ["Genres", a.primary_genres], ["Benchmark films used", a.benchmark_films]]))),
    attachment(a.actor, "actors", { role: "" }),
    a.package_risk_notes ? [el("h3", {}, "Packaging notes"), el("p", { class: "profile-note" }, a.package_risk_notes)] : null,
    el("div", { class: "profile-foot" }, el("span", {}, "Confidence ", el("b", {}, a.confidence || "—")), el("span", {}, "Reviewed ", el("b", {}, dateOnly(a.last_reviewed))),
      links.length ? el("span", {}, "Sources ", links) : null,
      el("span", { class: "muted" }, "Indicative, from the Saracen Bridge Actor Value Database. Confirm any fee with the agent.")));
}
function directorCard(d) {
  return el("div", { class: "profile" },
    el("div", { class: "profile-head" },
      el("div", {}, el("h2", {}, d.director_name), el("div", { class: "muted" }, [d.primary_classification, d.career_stage, d.current_trajectory].filter(Boolean).join(" · "))),
      el("span", { class: "tier" }, el("small", {}, "Tier"), String(d.commercial_tier || "—").split(/\s+[–-]\s+/)[0])),
    d.commercial_tier ? el("div", { class: "muted small", style: "margin-top:6px" }, d.commercial_tier) : null,
    el("div", { class: "kpis", style: "margin-top:18px" },
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Fee low"), el("div", { class: "v", title: "USD " + fmt(d.fee_low) }, usd(d.fee_low))),
      el("div", { class: "kpi edge" }, el("div", { class: "l" }, "Fee mid"), el("div", { class: "v", title: "USD " + fmt(d.fee_mid) }, usd(d.fee_mid))),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Fee high"), el("div", { class: "v", title: "USD " + fmt(d.fee_high) }, usd(d.fee_high))),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Proven budgets"), el("div", { class: "v", title: `USD ${fmt(d.proven_minimum_budget_usd)} – ${fmt(d.proven_maximum_budget_usd)}` }, `${usd(d.proven_minimum_budget_usd)}–${usd(d.proven_maximum_budget_usd).slice(1)}`))),
    d.fee_status ? el("p", { class: "note " + (/unavailable/i.test(d.fee_status) ? "FAIL" : "PRELIMINARY"), style: "margin-top:14px" }, d.fee_status,
      d.reference_production_budget ? ` · fees set against a ${usd(d.reference_production_budget)} reference budget` : "") : null,
    el("div", { class: "profile-cols" },
      el("div", {}, el("h3", {}, "Profile"), facts([["Genre", d.primary_genre], ["Also", d.secondary_genres], ["Production model", d.preferred_production_model],
        ["Works in", d.primary_working_territories], ["Studios & platforms", d.studio_platform_relationships]])),
      el("div", {}, el("h3", {}, "Deal & delivery"), facts([["Backend deal shape", d.indicative_backend_deal_shape], ["Delivery record", d.completion_bonding_notes]]))),
    attachment(d.director_name, "directors"),
    d.source_limitation_note ? el("p", { class: "muted small", style: "margin-top:14px" }, d.source_limitation_note) : null,
    el("div", { class: "profile-foot" }, el("span", {}, "Data confidence ", el("b", {}, d.overall_data_confidence || "—")), d.fee_confidence ? el("span", {}, "Fee confidence ", el("b", {}, d.fee_confidence)) : null,
      el("span", {}, "Reviewed ", el("b", {}, dateOnly(d.last_reviewed))), d.next_review_due ? el("span", {}, "Next review ", el("b", {}, dateOnly(d.next_review_due))) : null,
      el("span", { class: "muted" }, "Indicative, from the Saracen Bridge Director Value Database. Confirm any fee with the agent.")));
}

/* Term-sheet warnings, grouped by what's wrong, with the fields named (Jon's validator reports one line per field). */
const fieldName = f => String(f).replace(/^S\d+_\d+_/, "").replace(/_/g, " ").toLowerCase().replace(/^./, c => c.toUpperCase());
function warningGroups(warnings) {
  const groups = new Map();
  for (const w of warnings) {
    const msg = typeof w === "string" ? w : (w.message || JSON.stringify(w));
    if (!groups.has(msg)) groups.set(msg, []);
    groups.get(msg).push(...((w && w.fields) || []));
  }
  return el("ul", { class: "plain need", style: "margin-top:14px" }, [...groups].map(([msg, fields]) => el("li", {}, icon("alert"),
    el("span", {}, msg, fields.length ? [" ", el("span", { class: "muted" }, `(${plural(fields.length, "field")})`),
      el("details", { class: "fields" }, el("summary", {}, "Show fields"), el("div", { class: "small muted" }, fields.map(fieldName).join(" · ")))] : null))));
}

/* ---------------- results: one view each, used by the tool page and by the Library (15 Oct audit: the Library showed raw JSON) */
const kpi = (l, v, edge) => el("div", { class: "kpi" + (edge ? " edge" : "") }, el("div", { class: "l" }, l), el("div", { class: "v" }, v));
function incentivesResult(res) {
  return [el("div", { class: "card flush" }, table(["Programme", "Gate", "#Eligible base", "#Gross benefit", "#Tax effect", "#Net"], res.map(r => el("tr", {},
      el("td", {}, el("div", { style: "white-space:nowrap;font-weight:650" }, r.programme_id, el("span", { class: "muted mono", style: "font-weight:400;margin-left:8px" }, r.currency)), el("div", { class: "small muted" }, r.programme_name),
        r.last_verified ? el("div", { class: "small muted" }, "Verified " + String(r.last_verified).slice(0, 10)) : null,
        (r.reasons || []).length ? el("div", { class: "small", style: "margin-top:6px;color:var(--fg-2)" }, r.reasons.join(" ")) : null),
      el("td", {}, el("span", { class: "pill " + r.gate }, r.gate)), el("td", { class: "num" }, fmt(r.eligible_base)),
      el("td", { class: "num" }, fmt(r.gross_benefit)), el("td", { class: "num" }, fmt(r.tax_effect)), el("td", { class: "num" }, el("b", {}, fmt(r.net_after_tax))))))),
    el("p", { class: "muted small" }, "Rules from the Saracen Bridge audited incentive model (26 Aug 2026). Unknown inputs stay unknown and keep a result PRELIMINARY. Confirm with the authority and local advisers before relying on any figure.")];
}
/* 1.0.8: read a Library script for the Cultural Test's Section A (and B), Jon's answer pack */
async function bfiReader(box, apply) {
  const { runs } = await api.get("/api/runs?limit=500").catch(() => ({ runs: [] }));
  const scripts = runs.filter(r => ["coverage", "schedule", "brand"].includes(r.tool));
  const card = el("div", { class: "card" });
  box.append(card);
  if (!scripts.length) return put(card, el("h2", { style: "margin:0" }, icon("sparkle"), "Read a script for Section A"),
    el("p", { class: "muted small" }, "No scripts in the Library yet. Drop one on Script Coverage, Scheduling & Budgeting or Brand Integration, then come back."));
  const pick = el("select", { "aria-label": "Script" }, scripts.map(r => el("option", { value: `${r.tool}/${r.id}` }, `${r.title} · ${(toolById(r.tool) || {}).name || r.tool}`)));
  const body = el("div", {});
  const show = async () => {
    const [tool, id] = pick.value.split("/");
    put(body, el("div", { class: "clapper" }));
    const r = await api.get(`/api/runs/${tool}/${id}`).catch(() => null);
    if (!r) return put(body, el("p", { class: "muted" }, "That script is no longer in the Library."));
    const res = r.outputs.bfi_read, watch = jobWatch("bfiread", tool, id, show);
    const go = async ev => {
      const btn = ev.currentTarget; btn.disabled = true;
      try { await api.post("/api/tools/bfi/read", { tool, run_id: id, mode: MODE }); toast("ai", "Script read queued", `Gemma reads every scene on ${runsOn()}.`); pollJobs(); watch.start(); }
      catch (e) { toast("bad", "Couldn't start", el("span", {}, e.message, " ", el("a", { href: "#/settings" }, "Settings"))); }
      btn.disabled = false;
    };
    const startRow = label => el("div", { class: "row", style: "margin-top:14px;gap:12px;align-items:center" }, modeSwitch(), el("button", { type: "button", class: "btn primary", onclick: go }, icon("sparkle"), label));
    if (!res) return put(body, el("p", { class: "muted small" }, "Gemma reads every scene for where it is set, who the leads are and where they're from, what ties the story to the UK or Europe, and the language of the dialogue. The Studio does the arithmetic: setting by script length, spoken words counted from the script, points from the BFI thresholds."), startRow("Read for Section A"), watch);
    const c = res.criteria, pp = x => `${x.proposed} / ${x.conservative}`;
    put(body,
      el("div", { class: "kpis", style: "margin-top:14px" }, kpi("A1 setting", pp(c.A1), true), kpi("A2 leads", pp(c.A2)), kpi("A3 subject", pp(c.A3)), kpi("A4 dialogue", pp(c.A4)), kpi("B contribution", pp(c.B))),
      el("p", { class: "muted small", style: "margin:6px 0 0" }, `Proposed / conservative points. ${c.A1.reason} ${c.A4.reason}`),
      res.checks.map(x => el("p", { class: "note PRELIMINARY" }, x)),
      el("div", { class: "row", style: "margin:14px 0;gap:10px" }, el("button", { type: "button", class: "btn primary", onclick: () => apply(res, r.title) }, "Use these points in the scorer"),
        el("a", { class: "btn", href: `/api/runs/${tool}/${id}/bfi_pack.xlsx` }, icon("download"), "Answer pack (.xlsx)")),
      el("h3", { style: "margin:18px 0 8px" }, "Leads"),
      table(["#", "Character", "UK or EEA", "Why"], c.A2.leads.map(l => el("tr", {}, el("td", { class: "num" }, l.rank), el("td", {}, el("b", {}, l.name)),
        el("td", {}, el("span", { class: "pill " + (l.qualifies === "Yes" ? "PASS" : l.qualifies === "No" ? "FAIL" : "PRELIMINARY") }, l.qualifies)),
        el("td", { class: "small" }, l.reason, l.evidence.length ? el("div", { class: "muted" }, l.evidence.map(e => `Scene ${e.scene}: ${e.text}`).join(" · ")) : null)))),
      el("h3", { style: "margin:18px 0 8px" }, "Answer pack"),
      table(["Ref", "Proposed answer", "#Points", "Exact reference", "Status"], res.answer_pack.map(x => el("tr", {}, el("td", { class: "mono" }, x.ref),
        el("td", { class: "small" }, x.answer || el("span", { class: "muted" }, "—"), el("div", { class: "muted" }, x.assumptions)),
        el("td", { class: "num" }, `${x.points_proposed} / ${x.points_conservative}`), el("td", { class: "small muted" }, x.reference),
        el("td", {}, el("span", { class: "pill " + (x.status === "DO NOT SUBMIT" ? "FAIL" : "PRELIMINARY") }, x.status))))),
      el("details", { class: "lb-more", style: "margin-top:16px" }, el("summary", {}, "Setting, scene by scene"),
        table(["Scene", "#Eighths", "Country", "Stated", "Evidence", "Languages"], res.scenes.map(x => el("tr", {}, el("td", { class: "small" }, `${x.scene} · ${x.heading}`),
          el("td", { class: "num" }, x.eighths), el("td", { class: "small" }, x.country, el("div", { class: "muted" }, x.zone)), el("td", { class: "small" }, x.explicit ? "Yes" : "Inferred"),
          el("td", { class: "small muted" }, x.evidence), el("td", { class: "small" }, x.languages.map(l => `${l.language} ${l.share}%`).join(", ") || "—"))))),
      el("details", { class: "lb-more", style: "margin-top:12px" }, el("summary", {}, "Read again"), startRow("Read again")), watch);
  };
  pick.addEventListener("change", show);
  put(card, el("h2", { style: "margin:0" }, icon("sparkle"), "Read a script for Section A"),
    el("p", { class: "muted small", style: "margin:6px 0 12px" }, "Saracen Bridge instructions: never award unsupported points; every answer stays with the company to verify, approve and submit."),
    el("label", { class: "f" }, "Script", pick), body);
  show();
}
function bfiResult(r) {
  const sec = s => el("tr", {}, el("td", {}, s), el("td", { class: "num" }, r.proposed.sections[s]), el("td", { class: "num" }, r.conservative.sections[s]));
  return [el("div", { class: "kpis" }, kpi("Verdict", r.verdict, true), kpi("Proposed", `${r.proposed.total} / 35`), kpi("Conservative", `${r.conservative.total} / 35`)),
    el("div", { class: "card flush", style: "margin-top:14px" }, table(["Section", "#Proposed", "#Conservative"], [..."ABCD"].map(sec).concat([el("tr", {}, el("td", {}, el("b", {}, "Total (pass 18)")), el("td", { class: "num" }, r.proposed.total), el("td", { class: "num" }, r.conservative.total))]))),
    [...new Set([...(r.proposed.notes || []), ...(r.conservative.notes || [])])].map(n => el("p", { class: "note PRELIMINARY" }, n))];
}
function termsheetView(t) {
  return [el("p", { class: "muted small" }, [t.parties, t.governing_law ? `Governing law: ${t.governing_law}` : ""].filter(Boolean).join(" · ")),
    t.checks.map(c => el("p", { class: "note PRELIMINARY" }, c)),
    el("div", { class: "card flush", style: "margin-top:12px" }, table(["Instrument", "#Amount", "Status", "Terms"], t.rows.map(r => el("tr", {},
      el("td", {}, el("b", {}, r.name), el("div", { class: "small muted" }, r.terms.status_words || "")),
      el("td", { class: "num" }, r.amount === null ? "Unknown" : fmt(r.amount), el("div", { class: "small muted" }, r.currency)),
      el("td", {}, el("span", { class: "pill PRELIMINARY" }, r.status)),
      el("td", { class: "small" }, ["interest", "fees", "term", "security", "recoupment"].filter(k => r.terms[k] && !/^not stated$/i.test(r.terms[k])).map(k => el("div", {}, el("b", {}, k[0].toUpperCase() + k.slice(1) + ": "), r.terms[k]))))))),
    el("p", { class: "muted small" }, "Open Finance Plan and use Read a term sheet to add these to a plan.")];
}
function financeResult(r) {
  return [el("div", { class: "kpis" }, kpi("Sources", fmt(r.sources_total)), kpi("Confirmed cash", fmt(r.bankable)), kpi("Senior / gap debt to raise", fmt(r.residual_debt_needed), true),
      kpi("Debt share of budget", r.gross_budget ? pct(r.residual_debt_needed / r.gross_budget) : "—")),
    (r.double_count || []).map(d => el("p", { class: "note FAIL" }, "Double count: " + d + ". The package total is ignored and its parts are used.")),
    (r.errors || []).map(d => el("p", { class: "note FAIL" }, d)), (r.preliminary || []).map(d => el("p", { class: "note PRELIMINARY" }, d)),
    r.bankable === 0 ? el("p", { class: "note FAIL" }, "No source is confirmed cash: the plan is not bankable.") : null];
}
function greenlightResult(r) {
  return [el("div", { class: "kpi edge", style: "max-width:420px" }, el("div", { class: "l" }, "Decision"), el("div", { class: "v" }, r.decision)), (r.reasons || []).map(x => el("p", { class: "note" }, x)),
    el("p", { class: "muted small" }, "Rules from the Saracen Bridge Film Finance Analyst. The 243-check closing matrix that produces these scores is awaited from Saracen Bridge.")];
}
function agreementResult(r, withFiles) {
  if (!r.ok) return [el("p", { class: "note FAIL" }, r.error), (r.problems || []).length ? el("ul", { class: "plain need", style: "margin-top:10px" }, r.problems.map(x => el("li", {}, icon("alert"), el("span", {}, x)))) : null];
  const pop = r.population || {};
  return [pop.fields && !pop.populated ? el("p", { class: "note PRELIMINARY" }, "Nothing was filled in: every field still holds the master placeholder. Fill in the project's terms in the input workbook, then build again.")
      : el("p", { class: "note PASS" }, `Built${pop.fields ? `: ${fmt(pop.populated)} of ${fmt(pop.fields)} fields filled` : ""}. Technical validation: ${r.technical_validation_passed ? "passed" : "see warnings"}. Not ready for signature until reviewed.`),
    withFiles ? el("div", { class: "files" }, r.files.map(f => el("a", { class: "file", href: `/api/runs/agreement/${r.run_id}/files/${encodeURIComponent(f)}` }, el("span", { class: "ic" }, icon("doc")), f))) : null,
    (r.warnings || []).length ? warningGroups(r.warnings) : null];
}
/* what was entered, shown above a saved result */
function inputsView(r) {
  const i = r.inputs || {}, box = (title, node) => el("div", { class: "card flush", style: "margin-top:22px" }, el("h2", { style: "padding:20px 20px 0" }, title), node);
  if (r.tool === "incentives") return box("Routes", table(["Programme", "#Spend", "#Project cost", "Eligibility"], (i.routes || []).map(x => el("tr", {}, el("td", {}, el("b", {}, x.programme_id)), el("td", { class: "num" }, fmt(x.qualifying_spend)), el("td", { class: "num" }, fmt(x.project_cost)), el("td", {}, x.eligibility || "Unknown")))));
  if (r.tool === "finance" && !r.outputs.termsheet) return box(`Sources · gross budget ${fmt(i.gross_budget)} ${i.currency || ""}`, table(["Source", "#Amount", "Status", "Cash", "Inside package"], (i.sources || []).map(x => el("tr", {}, el("td", {}, x.name), el("td", { class: "num" }, fmt(x.amount)), el("td", {}, x.status), el("td", {}, x.cash === false ? "No" : "Yes"), el("td", { class: "muted" }, x.parent || "—")))));
  if (r.tool === "greenlight") return box("Scores entered", table(["Check", "Value"], [["Overall", i.overall + "%"], ["Finance", i.finance + "%"], ["Legal", i.legal + "%"], ["Bond & insurance", i.bond_insurance + "%"], ["Production & delivery", i.production_delivery + "%"], ["Critical blockers", i.critical_blockers ?? 0],
    ["Funding gap remains", i.funding_gap ? "Yes" : "No"], ["All sign-offs approved", i.signoffs_approved ? "Yes" : "No"], ["Every condition has an owned, dated cure", i.cures_owned_and_timed ? "Yes" : "No"]].map(([k, v]) => el("tr", {}, el("td", {}, k), el("td", {}, String(v))))));
  if (r.tool === "bfi") { const refs = [...new Set([...Object.keys(i.proposed || {}), ...Object.keys(i.conservative || {})])].sort();
    return refs.length ? box("Points entered", table(["Ref", "#Proposed", "#Conservative"], refs.map(k => el("tr", {}, el("td", { class: "mono" }, k), el("td", { class: "num" }, i.proposed?.[k] ?? "—"), el("td", { class: "num" }, i.conservative?.[k] ?? "—"))))) : null; }
  return null;
}
const RESULT_VIEWS = {
  incentives: r => incentivesResult(r.outputs.results || []), bfi: r => bfiResult(r.outputs),
  finance: r => r.outputs.termsheet ? termsheetView(r.outputs.termsheet) : financeResult(r.outputs),
  greenlight: r => greenlightResult(r.outputs), agreement: r => agreementResult({ ok: true, ...r.outputs }, false),
  sales: r => [el("div", { class: "row", style: "margin-bottom:14px" }, el("a", { class: "btn", href: `/api/runs/sales/${r.id}/engine.xlsx` }, icon("download"), "Download the Saracen Bridge engine, filled (.xlsx)"),
    el("button", { type: "button", class: "btn primary", onclick: () => { SALES_RUN = r.id; SALES_OPEN = true; location.hash = "#/tool/sales"; } }, "Open in Sales Estimates")), salesResult(r.outputs.valuation)],
};

/* ---------------- schedule & budget (1.0.4) ---------------- */
let BUDGET_RUN = null, BUDGET_OPEN = false;   /* a Library item, and whether to open the Schedule & budget tab on it */
let BUDGET_OPTS = null;
const BSTATUS = { benchmark: ["", "Rate card"], input: ["PASS", "Your figure"], unknown: ["PRELIMINARY", "Unknown"], allowance: ["PRELIMINARY", "Allowance"] };
const money = (cur, n) => n === null || n === undefined ? "—" : `${cur} ${fmt(n)}`;
async function budgetPanel(box) {
  BUDGET_OPTS = BUDGET_OPTS || await api.get("/api/tools/schedule/budget/options");
  const { runs } = await api.get("/api/runs?tool=schedule&limit=200");
  if (!runs.length) return box.append(el("div", { class: "drop", style: "border-style:solid" }, el("div", { class: "art" }, icon("schedule")),
    el("div", { class: "big" }, "Read a script first"), el("p", {}, "Drop it on the Script breakdown tab. Its scenes, cast and locations feed the schedule and the budget.")));
  const f = (label, node, grow) => el("label", { class: "f", style: grow ? "flex:1 1 260px" : "flex:0 1 auto" }, label, node);
  const num = (v, label, w = 90, step = "any") => el("input", { type: "number", min: 0, step, value: v ?? "", "aria-label": label, style: `width:${w}px` });
  const pick = el("select", { "aria-label": "Script" }, runs.map(r => el("option", { value: r.id, selected: r.id === BUDGET_RUN },
    `${r.title} · ${plural((r.summary || {}).scene_count || 0, "scene")}${(r.summary || {}).budget_total ? " · budgeted" : ""}`)));
  const jur = el("select", { "aria-label": "Jurisdiction" }, BUDGET_OPTS.jurisdictions.map(j => el("option", { value: j.jurisdiction, selected: j.jurisdiction === "United Kingdom" }, `${j.jurisdiction} (${j.currency})`)));
  const reg = el("select", { "aria-label": "Region" });
  const fillReg = keep => put(reg, ((BUDGET_OPTS.jurisdictions.find(j => j.jurisdiction === jur.value) || {}).regions || []).map(r => el("option", { value: r, selected: r === keep }, r)));
  fillReg(); jur.addEventListener("change", () => fillReg());
  const tier = el("select", { "aria-label": "Crew experience tier" }, [1, 2, 3, 4].map(n => el("option", { value: n, selected: n === 2 }, `Tier ${n}`)));
  const pace = Object.fromEntries(["lean", "base", "conservative"].map(k => [k, num(BUDGET_OPTS.pages_per_day[k], `Pages a day, ${k}`, 70, 0.25)]));
  const fringe = num("", "Payroll load %", 90), bg = num("", "Background artists a day", 90, 1), vfx = num("", "VFX shots", 90, 1);
  let state = { overrides: {}, cast: {}, useOrder: "first" }, RUNREC = null;
  const out = el("div", { style: "margin-top:22px" }), elBox = el("div", {});
  const settings = () => ({ tool: "schedule", run_id: pick.value, jurisdiction: jur.value, region: reg.value, tier: Number(tier.value),
    pages_per_day: Object.fromEntries(Object.entries(pace).map(([k, i]) => [k, Number(i.value) || BUDGET_OPTS.pages_per_day[k]])),
    inputs: { fringe_pct: fringe.value === "" ? null : Number(fringe.value), background_per_day: bg.value === "" ? null : Number(bg.value),
      vfx_shots: vfx.value === "" ? null : Number(vfx.value), overrides: state.overrides, cast: state.cast }, use_order: state.useOrder || "first" });
  const go = async btn => {
    if (btn) btn.disabled = true;
    put(out, el("div", { class: "clapper" }));
    try { const res = await api.post("/api/tools/schedule/budget", settings()); render(res); toast("ok", "Schedule and budget built", `${res.schedule.base.shoot_days} shooting days in the base case. Saved with the script in the Library.`); }
    catch (e) { put(out, errBox(e)); }
    finally { if (btn) btn.disabled = false; }
  };
  const restore = async () => {
    BUDGET_RUN = pick.value;
    const r = await api.get(`/api/runs/schedule/${pick.value}`).catch(() => null);
    RUNREC = r;
    put(elBox, r ? elementsBox(r, () => restore()) : null);
    const res = r && r.outputs && r.outputs.budget;
    if (!res) { state = { overrides: {}, cast: {}, useOrder: "first" }; return put(out, el("p", { class: "muted" }, "No budget yet for this script. Choose the settings and press Build.")); }
    const st = res.settings || {}, inp = st.inputs || {};
    if (st.jurisdiction) { jur.value = st.jurisdiction; fillReg(st.region); }
    if (st.tier) tier.value = st.tier;
    Object.entries(st.pages_per_day || {}).forEach(([k, v]) => pace[k] && (pace[k].value = v));
    fringe.value = inp.fringe_pct ?? ""; bg.value = inp.background_per_day ?? ""; vfx.value = inp.vfx_shots ?? "";
    state = { overrides: inp.overrides || {}, cast: inp.cast || {}, useOrder: st.use_order || (st.use_reasoned ? "reasoned" : "first") };
    render(res);
  };
  pick.addEventListener("change", restore);
  /* 1.1.6 (Tim, 27 Oct: "deep reasoning on schedule"): the AI reasons out a better shooting order; the user chooses
     whether the budget uses it */
  const reasonedBox = res => {
    const outs = (RUNREC && RUNREC.outputs) || {}, opt = outs.schedule_optimised, rs = outs.schedule_reasoned;
    const watch = jobWatch("schedreason", "schedule", pick.value, () => restore());
    const pace0 = () => Number(pace.base.value) || null;
    const optimise = async ev => {
      const btn = ev.currentTarget; btn.disabled = true;
      try { const r = await api.post("/api/tools/schedule/optimise", { run_id: pick.value, pages_per_day: pace0() });
        toast("ok", "Order optimised", `${r.measures.days} days, ${plural(r.measures.moves, "company move")}, ${plural(r.measures.hold_days, "day")} actors are held (first pass ${r.first_pass.hold_days}).`); await restore(); }
      catch (e) { toast("bad", "Couldn't optimise", e.message); btn.disabled = false; }
    };
    const reason = async ev => {
      const btn = ev.currentTarget; btn.disabled = true;
      try { await api.post("/api/tools/schedule/reason", { run_id: pick.value, mode: "deep", pages_per_day: pace0() });
        toast("ai", "Reasoning out the shooting order", `Deep reasoning on ${runsOn()}: the AI thinks before it answers, so this takes a few minutes.`); pollJobs(); watch.start(); }
      catch (e) { toast("bad", "Couldn't start", el("span", {}, e.message, " ", el("a", { href: "#/settings" }, "Settings"))); }
      btn.disabled = false;
    };
    const inUse = res.schedule_source || "first";
    const useBtn = (which, label) => inUse === which ? el("span", { class: "pill PASS" }, icon("check"), `The budget uses ${label}`)
      : el("button", { type: "button", class: "btn sm" + (which === "first" ? " quiet" : " primary"), onclick: ev => { state.useOrder = which; go(ev.currentTarget); } }, `Use ${label}`);
    const intro = el("p", { class: "muted", style: "margin:0 0 12px" }, "The first pass is mechanical. Optimise works the order out by arithmetic: fewest shooting days, then fewest company moves, then fewest days actors are paid to wait between their scenes. Reason it through then has the AI, with Deep reasoning, adjust that order for what arithmetic can't see (weather cover, child, stunt, water and intimacy days) and say why. Every scene is checked back in; nothing changes until you choose an order.");
    const cols = [["First pass", (opt || (rs && rs.optimised) || {}).first_pass || (rs && rs.measures.first_pass)], ["Optimised", (opt || (rs && rs.optimised) || {}).measures], ["AI reasoned", rs && rs.measures.reasoned]].filter(([, m]) => m);
    const row = (l, k, lowerBetter) => el("tr", {}, el("td", {}, l), cols.map(([, m], i) => {
      const v = m[k], f = cols[0][1][k];
      return el("td", { class: "num" }, i ? el("b", {}, fmt(v)) : fmt(v), i && v !== f ? el("span", { class: "small" + (lowerBetter && v < f ? "" : " muted"), style: lowerBetter && v < f ? "color:var(--ok)" : null }, ` (${v > f ? "+" : ""}${fmt(v - f)})`) : null);
    }));
    const board = rs ? rs.board : opt ? opt.board : null;
    return el("div", {}, intro,
      el("div", { class: "row", style: "align-items:center;gap:10px;margin-bottom:12px" },
        el("button", { type: "button", class: "btn sm" + (opt ? " quiet" : " primary"), onclick: optimise }, icon("schedule"), opt ? "Optimise again" : "Optimise the order"),
        el("button", { type: "button", class: "btn sm" + (rs ? " quiet" : opt ? " primary" : ""), onclick: reason }, icon("sparkle"), rs ? "Reason it through again" : "Reason it through (Deep)")), watch,
      cols.length > 1 ? [el("div", { class: "card flush" }, table(["Measure", ...cols.map(([l]) => "#" + l)], [row("Shooting days", "days", true), row("Company moves", "moves", true),
          row("Days actors are held between work days", "hold_days", true), row("…of which the two largest parts", "lead_hold_days", true), row("Days over the pace", "over_pace", true), row("Night days", "night_days", false)])),
        el("div", { class: "row", style: "align-items:center;gap:10px;margin-top:12px" }, useBtn("first", "the first pass"), opt || (rs && rs.optimised) ? useBtn("optimised", "the optimised order") : null, rs ? useBtn("reasoned", "the AI's order") : null)] : null,
      rs ? el("p", { class: "small muted", style: "margin-top:10px" }, `AI order by ${rs.engine}, ${rs.mode} reasoning, ${rs.date}${rs.seconds ? `, in ${Math.round(rs.seconds / 60) || "under a"} min` : ""}, at ${rs.pages_per_day} pages a day, starting from the optimised order.`) : null,
      rs && (rs.repairs || []).length ? el("p", { class: "note PRELIMINARY" }, "The AI's answer needed checking: ", rs.repairs.join(" ")) : null,
      rs && (rs.changes || []).length ? [el("h2", { style: "margin-top:18px" }, "What the AI changed, and why"), el("ul", { class: "plain", style: "line-height:1.6" }, rs.changes.map(c => el("li", {}, el("b", {}, c.change), c.reason ? `: ${c.reason}` : "")))] : null,
      rs && (rs.risks || []).length ? [el("h2", { style: "margin-top:18px" }, "Risks it still carries"), el("ul", { class: "plain", style: "line-height:1.6" }, rs.risks.map(r => el("li", {}, icon("alert"), " ", r)))] : null,
      board ? [el("h2", { style: "margin-top:18px" }, rs ? "The AI's order, base case" : "The optimised order, base case"),
        el("div", { class: "card flush" }, table(["#Day", "D/N", "#Pages", "Scenes", "Locations", "#Moves", "Cast", "Note"],
          board.map(x => el("tr", {}, el("td", { class: "num" }, x.day), el("td", { class: "small" }, x.night ? "Night" : "Day"), el("td", { class: "num" }, x.pages),
            el("td", { class: "small" }, x.scenes.join(", ")), el("td", { class: "small" }, x.locations.join("; ")), el("td", { class: "num" }, x.moves),
            el("td", { class: "small muted" }, x.cast.join(", ")), el("td", { class: "small muted" }, x.note || "")))))] : null,
      el("p", { class: "muted small" }, "Used for the budget, the optimised order is packed at each case's pace; the AI's order keeps its own days in the base case, and lean and conservative take the same order at their pace. Check either with the 1st AD."));
  };
  const render = res => {
    const b = res.budget, base = b.base, cur = res.currency;
    const lineKey = l => `${l.account}|${l.description}`;
    const castNames = new Set(res.dood.map(c => c.name));
    const isAllowance = l => l.status === "allowance";     /* 1.1.6: a planning figure from the card, kept out of the priced total */
    const toPrice = base.lines.filter(l => l.status === "unknown" || isAllowance(l) || state.overrides[lineKey(l)] !== undefined || (l.account === "1401" && state.cast[l.description]));
    const priceRow = l => {
      const isCast = l.account === "1401" && castNames.has(l.description);
      const prev = isCast ? (state.cast[l.description] || {}) : { amount: state.overrides[lineKey(l)] };
      const amt = el("input", { type: "number", min: 0, step: "any", value: prev.amount ?? "", placeholder: isAllowance(l) && l.amount !== null ? `Allowance ${fmt(l.amount)}` : "Amount", "aria-label": `Amount for ${l.description}`, style: "width:150px" });
      const basis = isCast ? el("select", { "aria-label": `Basis for ${l.description}` }, [["flat", "Total fee"], ["day", "Per day"], ["week", "Per week"]].map(([v, t]) => el("option", { value: v, selected: v === (prev.basis || "flat") }, t))) : null;
      const save = () => {
        if (isCast) { if (amt.value === "") delete state.cast[l.description]; else state.cast[l.description] = { amount: Number(amt.value), basis: basis.value }; }
        else if (amt.value === "") delete state.overrides[lineKey(l)]; else state.overrides[lineKey(l)] = Number(amt.value);
      };
      amt.addEventListener("change", save); basis && basis.addEventListener("change", save);
      return el("tr", {}, el("td", { class: "mono small" }, l.account), el("td", {}, el("b", {}, l.description), el("div", { class: "small muted" }, l.category_name)),
        el("td", { class: "small muted" }, isCast ? `${plural(l.qty, "day")} worked` : (l.note || ""), isAllowance(l) ? el("div", {}, l.basis) : null), el("td", {}, el("div", { class: "row", style: "gap:8px;flex-wrap:nowrap" }, amt, basis)));
    };
    const catRows = base.categories.map(c => el("tr", {}, el("td", { class: "mono small" }, c.category), el("td", {}, c.name, el("div", { class: "small muted" }, c.phase)),
      ["lean", "base", "conservative"].map(s => el("td", { class: "num" }, fmt((b[s].categories.find(x => x.category === c.category) || {}).known || 0))),
      el("td", { class: "num" }, c.unknown ? el("span", { class: "pill PRELIMINARY" }, c.unknown) : "")));
    catRows.push(el("tr", {}, el("td", {}), el("td", {}, el("b", {}, "Total of priced lines")), ["lean", "base", "conservative"].map(s => el("td", { class: "num" }, el("b", {}, fmt(b[s].known_total)))),
      el("td", { class: "num" }, el("b", {}, base.unknown_lines))));
    const detail = el("div", {});
    put(out,
      el("div", { class: "kpis" }, kpi("Shooting days", ["lean", "base", "conservative"].map(s => res.schedule[s].shoot_days).join(" / ")),
        kpi("Base case, priced lines", money(cur, base.known_total), true), kpi("Still to price", plural(base.unknown_lines, "line")),
        kpi("Allowances, not in the total", base.allowance_lines ? money(cur, base.allowance_total) : "None"),
        kpi("Company moves", res.schedule.base.moves)),
      el("p", { class: "muted small", style: "margin:6px 0 0" }, `Lean / base / conservative at ${["lean", "base", "conservative"].map(s => res.pages_per_day[s]).join(" / ")} pages a day. ${res.jurisdiction}, ${res.region}, crew tier ${res.tier}. Built ${savedAt(res.built)}.`),
      base.unknown_lines ? el("p", { class: "note PRELIMINARY" }, `PRELIMINARY: ${plural(base.unknown_lines, "line")} can't be priced from a script or the Saracen Bridge rate card (fees, negotiated roles, items the card doesn't list). They are not counted as zero. Price them under Lines to price.${base.allowance_lines ? ` ${plural(base.allowance_lines, "of them has", "of them have")} a planning allowance from the card (${money(cur, base.allowance_total)} in all), shown beside the line but kept out of the priced total until you enter a figure.` : ""}`) : el("p", { class: "note PASS" }, "Every line is priced. Still a script-only estimate: confirm with a line producer and production accountant."),
      (res.warnings || []).map(w => el("p", { class: "note " + (/no scenes/i.test(w) ? "FAIL" : "PRELIMINARY") }, w)),
      el("div", { class: "row", style: "margin:16px 0 4px" }, el("a", { class: "btn", href: `/api/runs/schedule/${pick.value}/budget.xlsx` }, icon("download"), "Download the workbook (.xlsx)")),
      el("div", { class: "card flush", style: "margin-top:16px" }, el("h2", { style: "padding:20px 20px 0" }, `Top sheet (${cur})`),
        table(["Account", "Category", "#Lean", "#Base", "#Conservative", "#To price"], catRows)),
      detail);
    tabs(detail, [
      [`Lines to price (${toPrice.length})`, d => d.append(toPrice.length ? [el("div", { class: "card flush" }, table(["Account", "Line", "Basis", `Amount (${cur})`], toPrice.map(priceRow))),
        el("div", { class: "row", style: "margin-top:14px" }, el("button", { type: "button", class: "btn primary", onclick: ev => go(ev.currentTarget) }, icon("sparkle"), "Update the budget"))]
        : el("p", { class: "muted" }, "Nothing left to price."))],
      ["All lines (base)", d => d.append(el("div", { class: "card flush" }, table(["Account", "Line", "#Qty", "Unit", "#Rate", "#Amount", "Status", "Basis"],
        base.lines.map(l => el("tr", {}, el("td", { class: "mono small" }, l.account), el("td", {}, l.description, el("div", { class: "small muted" }, l.category_name)),
          el("td", { class: "num" }, l.qty === null ? "—" : fmt(l.qty, l.qty % 1 ? 1 : 0)), el("td", { class: "small" }, l.unit || ""), el("td", { class: "num" }, l.rate === null ? "—" : l.rate < 1 ? pct(l.rate) : fmt(l.rate)),
          el("td", { class: "num" }, el("b", {}, fmt(l.amount))), el("td", {}, el("span", { class: "pill " + BSTATUS[l.status][0] }, BSTATUS[l.status][1])),
          el("td", { class: "small muted" }, [l.basis, l.note].filter(Boolean).join(" · "))))))), true],
      [`Stripboard (${res.schedule.base.shoot_days} days)`, d => d.append(el("div", { class: "card flush" }, table(["#Day", "D/N", "#Pages", "Scenes", "Locations", "#Moves", "Cast"],
        res.stripboard.map(x => el("tr", {}, el("td", { class: "num" }, x.day), el("td", { class: "small" }, x.night ? "Night" : "Day"), el("td", { class: "num" }, x.pages),
          el("td", { class: "small" }, x.scenes.join(", ")), el("td", { class: "small" }, x.locations.join("; ")), el("td", { class: "num" }, x.moves), el("td", { class: "small muted" }, x.cast.join(", ")))))),
        el("p", { class: "muted small" }, res.schedule_source === "reasoned" ? "Base case, in the AI's reasoned order (see Shooting order). Check it with the 1st AD before relying on it."
          : res.schedule_source === "optimised" ? "Base case, in the Studio's optimised order (see Shooting order). Check it with the 1st AD before relying on it."
          : "Base case. Day scenes, then night scenes, grouped by site; day and night work never share a day, and a scene that runs over carries on the next day. A first pass for the 1st AD, not a final schedule.")), true],
      [res.schedule_source && res.schedule_source !== "first" ? `Shooting order (${res.schedule_source} in use)` : "Shooting order", d => d.append(reasonedBox(res)), true],
      ["Day out of days", d => d.append(el("div", { class: "card flush" }, table(["Character", "#Work days", "#First", "#Last", "#Holds"],
        res.dood.map(c => el("tr", {}, el("td", {}, el("b", {}, c.name)), el("td", { class: "num" }, c.work_days), el("td", { class: "num" }, c.first), el("td", { class: "num" }, c.last), el("td", { class: "num" }, c.hold_days))))))],
      ["Assumptions", d => d.append(el("ul", { class: "plain", style: "line-height:1.7" }, res.assumptions.map(a => el("li", {}, a))),
        (res.labour_rules || []).length ? [el("h2", { style: "margin-top:20px" }, `Payroll rules on the Saracen Bridge ${res.jurisdiction} card`), el("p", { class: "muted small" }, "For the payroll load % (fringes)."),
          el("ul", { class: "plain small", style: "line-height:1.6" }, res.labour_rules.map(r => el("li", {}, el("b", {}, r.topic), ": ", r.rule || "", r.treatment ? ` (${r.treatment})` : "")))] : null)],
    ]);
  };
  box.append(el("div", { class: "row", style: "align-items:flex-end" }, f("Script", pick, true), f("Jurisdiction", jur), f("Region", reg), f("Crew rates", tier)),
    el("div", { class: "row", style: "margin-top:12px;align-items:flex-end" }, f("Pages a day: lean", pace.lean), f("base", pace.base), f("conservative", pace.conservative),
      f("Payroll load %", fringe), f("Background a day", bg), f("VFX shots", vfx),
      el("button", { type: "button", class: "btn primary", onclick: ev => go(ev.currentTarget) }, icon("schedule"), "Build schedule and budget")),
    el("p", { class: "muted small", style: "margin:10px 0 0" }, "Rates from the Saracen Bridge 2026 rate cards and its chart of accounts. Anything a script can't tell you stays Unknown, never zero."),
    elBox, out);
  await restore();
}
/* 1.0.8: element tagging for the picked script: what Gemma found scene by scene, and the button to (re)tag */
function elementsBox(r, refresh) {
  const e = r.outputs.elements, s = e && e.summary;
  const watch = jobWatch("elements", "schedule", r.id, refresh);
  const tag = async ev => {
    const btn = ev.currentTarget; btn.disabled = true;
    try { await api.post("/api/tools/schedule/elements", { run_ids: [r.id], mode: MODE }); toast("ai", "Element tagging queued", `Gemma reads every scene on ${runsOn()}. Build the budget again when it's done.`); pollJobs(); watch.start(); }
    catch (err) { toast("bad", "Couldn't start", el("span", {}, err.message, " ", el("a", { href: "#/settings" }, "Settings"))); }
    btn.disabled = false;
  };
  const hits = s ? Object.entries(s).filter(([, v]) => v.scenes.length) : [];
  return el("div", { class: "notice", style: "margin-top:18px;align-items:flex-start" }, el("div", { class: "ic" }, icon("sparkle")),
    el("div", { class: "grow" },
      e ? [el("div", {}, `Elements tagged in ${e.scenes.filter(x => x.tagged).length} of ${e.scenes.length} scenes (${e.date || ""})`),
        el("div", { class: "sub" }, hits.length ? hits.map(([, v]) => `${v.label} ${v.scenes.length}`).join(" · ") : "Nothing that adds cost was found."),
        e.checks && e.checks.length ? e.checks.map(c => el("div", { class: "sub warn-text" }, c)) : null,
        el("details", { class: "lb-more", style: "margin-top:10px" }, el("summary", {}, "What was tagged"),
          el("div", { style: "margin-top:10px" }, hits.map(([k, v]) => el("div", { class: "small", style: "margin-top:6px" }, el("b", {}, v.label), ": ",
            v.items ? v.items.slice(0, 12).map(i => `${i.item} (sc ${i.scenes.slice(0, 6).join(", ")})`).join("; ") + (v.items.length > 12 ? ` and ${v.items.length - 12} more` : "")
              : `scenes ${v.scenes.slice(0, 20).join(", ")}${v.total !== undefined ? `, ${fmt(v.total)} in all` : ""}`))))]
        : [el("div", {}, "Elements not tagged yet"), el("div", { class: "sub" }, "Gemma reads every scene for stunts, effects, vehicles, weapons, animals, background, special make-up, child performers and special equipment. Build the budget afterwards and it prices them from the Saracen Bridge rate card, or marks them to quote.")],
      watch),
    modeSwitch(), el("button", { type: "button", class: "btn sm primary", onclick: tag }, icon("sparkle"), e ? "Tag again" : "Tag elements"));
}

/* ---------------- sales valuation: Jon's Sales Valuation Engine v4.1 (1.0.5) ---------------- */
let SALES_OPTS = null, SALES_RUN = null, SALES_OPEN = false;
const usdFull = n => (n === null || n === undefined || n === "") ? "—" : `$${fmt(n)}`;
/* An editable table over an array of records (changed in place). cols: [{key, label, type, options, width, ph}] */
function editTable(cols, data, { addLabel, newRow, empty } = {}) {
  const body = el("tbody", {});
  const opts = c => typeof c.options === "function" ? c.options() : c.options;
  const cell = (rec, c) => {
    const v = rec[c.key] ?? "";
    const fillOpts = (n, cur) => { const list = opts(c), keep = cur !== "" && cur != null && !list.map(String).includes(String(cur));   // a saved value outside the list stays visible
      return put(n, ["", ...list, ...(keep ? [cur] : [])].map(o => el("option", { value: o, selected: String(o) === String(cur) }, o || "—"))); };
    const n = c.type === "select" ? fillOpts(el("select", { "aria-label": c.label }), v)
      : el("input", { type: c.type === "number" ? "number" : c.type === "date" ? "date" : "text", value: v, step: "any", placeholder: c.ph || "", "aria-label": c.label, list: c.list || null, style: `width:${c.width || 120}px` });
    n.addEventListener("change", () => { rec[c.key] = n.value === "" ? null : (c.type === "number" ? Number(n.value) : n.value); });
    if (c.onInput) n.addEventListener("input", () => c.onInput(n));
    if (c.type === "select" && typeof c.options === "function") ["focus", "mousedown"].forEach(e => n.addEventListener(e, () => fillOpts(n, n.value)));   /* options that change, e.g. films */
    return el("td", {}, n);
  };
  const draw = () => put(body, data.length ? data.map((rec, i) => el("tr", {}, cols.map(c => cell(rec, c)),
    el("td", {}, el("button", { type: "button", class: "btn quiet sm", "aria-label": "Remove row", onclick: () => { data.splice(i, 1); draw(); } }, icon("x")))))
    : el("tr", {}, el("td", { colspan: cols.length + 1, class: "muted small" }, empty || "None yet.")));
  draw();
  return el("div", {}, el("div", { class: "card flush" }, table([...cols.map(c => c.label), ""], body)),
    el("div", { class: "row", style: "margin-top:10px" }, el("button", { type: "button", class: "btn sm", onclick: () => { data.push(newRow ? newRow(data) : {}); draw(); } }, addLabel || "Add a row")));
}
const nextId = (rows, prefix) => `${prefix}${rows.reduce((m, r) => Math.max(m, Number(String(r.id || "").replace(/\D/g, "")) || 0), 0) + 1}`;
function namesList(id, url, field) {
  const dl = el("datalist", { id });
  let t;
  return { dl, onInput: inp => { clearTimeout(t); t = setTimeout(async () => {
    if (inp.value.trim().length < 2) return;
    const rows = await api.get(`${url}?q=${encodeURIComponent(inp.value)}&limit=12`).catch(() => []);
    put(dl, rows.map(r => el("option", { value: r[field] })));
  }, 160); } };
}
function salesResult(res) {
  const s = res.summary, f = res.finance;
  const statusPill = t => el("span", { class: "pill " + (t.status === "Complete" ? (t.confidence === "D" ? "PRELIMINARY" : "PASS") : t.status === "NO VALUE" ? "" : "PRELIMINARY") }, t.status === "Complete" ? `Grade ${t.confidence}` : t.status);
  const valued = res.territories.filter(t => t.status === "Complete").length;
  return [el("div", { class: "kpis" }, kpi("Gross Ask", usdFull(s.ask)), kpi("Expected Close", usdFull(s.expected), true), kpi("Gross Take", usdFull(s.take)), kpi("Net producer receipts", usdFull(s.net_producer_receipts))),
    el("p", { class: "muted small", style: "margin:6px 0 0" }, `${valued} of ${res.territories.length} territories valued · valuation date ${s.valuation_date} · USD · ${s.report || "Producer-facing"}. Intake ${pct(s.intake_completeness)} complete; cast factor ${fmt(s.cast_factor, 2)}, director factor ${fmt(s.director_factor, 2)}, package factor ${fmt(s.package_factor, 2)}.`),
    !valued ? el("p", { class: "note PRELIMINARY" }, "No territory has a value yet. The Saracen Bridge engine values a territory only from deal evidence, public buyer-economics proxies, or a documented worldwide anchor. Add evidence below.") : null,
    [["order", "Ask ≥ Expected ≥ Take"], ["fx", "Every deal converted to USD"], ["selection", "Every selected deal valid"]].map(([k, l]) => res.controls[k] === "FAIL" ? el("p", { class: "note FAIL" }, `Control failed: ${l}.`) : null),
    (res.flags || []).map(x => el("p", { class: "note PRELIMINARY" }, x)),
    el("div", { class: "card flush", style: "margin-top:16px" }, el("h2", { style: "padding:20px 20px 0" }, "Territories (USD)"),
      table(["Territory", "Basis", "#Ask", "#Expected Close", "#Take", "#Existing sale", "#Bankable", "Confidence"], res.territories.map(t => el("tr", {},
        el("td", {}, el("b", {}, t.territory), el("div", { class: "small muted" }, [t.package, t.sale_status].filter(Boolean).join(" · "))),
        el("td", { class: "small" }, t.method || t.basis || "—", t.rationale ? el("div", { class: "small muted" }, t.rationale) : null),
        el("td", { class: "num" }, fmt(t.ask)), el("td", { class: "num" }, el("b", {}, fmt(t.expected))), el("td", { class: "num" }, fmt(t.take)),
        el("td", { class: "num" }, fmt(t.existing)), el("td", { class: "num" }, fmt(t.bankable)), el("td", {}, statusPill(t)))))),
    el("div", { class: "card flush", style: "margin-top:16px" }, el("h2", { style: "padding:20px 20px 0" }, "Net receipts and finance (USD)"),
      table(["Case", "#Gross", "#Commission", "#Expenses", "#Collection", "#Net", "#Covers"], f.scenarios.map(x => el("tr", {}, el("td", {}, x.scenario),
        el("td", { class: "num" }, fmt(x.gross)), el("td", { class: "num" }, fmt(x.commission)), el("td", { class: "num" }, fmt(x.expenses)), el("td", { class: "num" }, fmt(x.collection)),
        el("td", { class: "num" }, el("b", {}, fmt(x.net))), el("td", { class: "num" }, x.coverage === "" ? "—" : pct(x.coverage))))),
      el("p", { class: "small", style: "padding:0 20px 16px" }, `Budget ${usdFull(f.budget_usd)}; net finance requirement ${usdFull(f.requirement_usd)}. Lender test: unsold Take ${usdFull(f.unsold_take)}, bankable value ${usdFull(f.bankable)}: `, el("b", {}, f.lender_result || "—"), ".")),
    el("p", { class: "muted small" }, "This is an independent indicative valuation produced by Saracen Bridge Analytics using available market evidence, comparable-title performance, package analysis and proprietary modelling. It is not a formal sales-agent estimate, distributor offer or guarantee of sales performance. Territory values should be validated through direct buyer and recognised sales-agent market testing before being relied upon for binding financing, lending or production decisions.")];
}
/* an existing estimate beside the Saracen Bridge valuation, in USD at the engine's rates (1.1.6) */
function estimateCompare(e, res) {
  if (!e || !(e.rows || []).length || !res) return null;
  const rate = (SALES_OPTS && SALES_OPTS.fx && SALES_OPTS.fx[e.currency]) || 1;
  const ours = Object.fromEntries((res.territories || []).map(t => [t.territory, t]));
  const usdOf = v => v === null || v === undefined ? null : v * rate;
  const rows = e.rows.map(x => { const o = ours[x.territory] || {}, a = usdOf(x.ask), d = a && o.ask ? a / o.ask - 1 : null;
    return el("tr", {}, el("td", {}, x.territory), el("td", { class: "num" }, fmt(a)), el("td", { class: "num" }, fmt(usdOf(x.take))),
      el("td", { class: "num" }, fmt(o.ask)), el("td", { class: "num" }, fmt(o.take)), el("td", { class: "num" }, d === null ? "—" : `${d > 0 ? "+" : ""}${Math.round(d * 100)}%`)); });
  const tot = k => e.rows.reduce((s, x) => s + (usdOf(x[k]) || 0), 0);
  return el("div", { class: "card flush", style: "margin-top:16px" },
    el("h2", { style: "padding:20px 20px 0" }, `Beside ${e.company || "the existing estimate"}${e.date ? ` (${e.date})` : ""}`),
    el("p", { class: "muted small", style: "padding:0 20px" }, `Their figures in USD${e.currency !== "USD" ? ` (from ${e.currency} at the engine's rate)` : ""}. Difference is their ask against the Saracen Bridge ask. Their total: ask ${usdFull(tot("ask"))}, take ${usdFull(tot("take"))}.`),
    table(["Territory", "#Their ask", "#Their take", "#Saracen Bridge ask", "#Saracen Bridge take", "#Difference"], rows));
}
async function valuationPanel(box) {
  const wait = el("div", { class: "clapper" }); box.append(wait);
  SALES_OPTS = SALES_OPTS || await api.get("/api/tools/sales/engine/options");
  SALES_AGENTS = SALES_AGENTS || (await api.get("/api/agents").catch(() => ({ agents: [] }))).agents;
  wait.remove();
  const L = SALES_OPTS.lists, T = SALES_OPTS.territories;
  const [{ runs: saved }, { runs: scripts }] = await Promise.all([api.get("/api/runs?tool=sales&limit=200"), api.get("/api/runs?limit=200").then(r => ({ runs: r.runs.filter(x => ["schedule", "coverage", "brand"].includes(x.tool)) }))]);
  let runId = SALES_RUN && saved.some(r => r.id === SALES_RUN) ? SALES_RUN : null;
  let P = blank();
  function blank() { return { intake: {}, actors: [], directors: [], films: [], deals: [], proxies: [], factors: {}, anchor: {}, rights: {}, finance: {}, package_factors: {}, report: "Producer-facing" }; }
  const pick = el("select", { "aria-label": "Valuation" }, el("option", { value: "" }, "New valuation"), saved.map(r => el("option", { value: r.id, selected: r.id === runId }, r.title)));
  const from = el("select", { "aria-label": "Start from a script" }, el("option", { value: "" }, "Start from a script in the Library…"), scripts.map(r => el("option", { value: `${r.tool}/${r.id}` }, `${r.title} · ${(toolById(r.tool) || {}).name || r.tool}`)));
  const form = el("div", {}), out = el("div", { style: "margin-top:22px" });
  const sel = (key, opts) => ({ key, type: "select", options: opts });
  /* Tim's genre list (20 Oct, 1.1.2): Genre, then the Subgenres of that genre. A value saved before keeps its place
     in the list, so an older valuation shows what it had. The Saracen Bridge engine uses the genre in its narrative only. */
  const GENRES = SALES_OPTS.genres || [], GENRE_NAMES = GENRES.map(g => g.genre);
  const subsOf = g => (GENRES.find(x => x.genre === g) || {}).subgenres || [];
  const withCurrent = (opts, v) => v && !opts.includes(v) ? [...opts, v] : opts;
  const genrePair = () => {
    const sub = el("select", { "aria-label": "Subgenre" });
    const fillSub = () => put(sub, ["", ...withCurrent(subsOf(P.intake.genre), P.intake.subgenre)].map(o =>
      el("option", { value: o, selected: o === (P.intake.subgenre || "") }, o || (P.intake.genre ? "—" : "Choose a genre first"))));
    const genre = el("select", { "aria-label": "Genre" }, ["", ...withCurrent(GENRE_NAMES, P.intake.genre)].map(o =>
      el("option", { value: o, selected: o === (P.intake.genre || "") }, o || "—")));
    genre.addEventListener("change", () => {
      P.intake.genre = genre.value || null;
      if (P.intake.subgenre && !subsOf(P.intake.genre).includes(P.intake.subgenre)) P.intake.subgenre = null;
      fillSub();
    });
    sub.addEventListener("change", () => { P.intake.subgenre = sub.value || null; });
    fillSub();
    /* the secondary genre (22 Oct): optional, never the primary; Sales Agents scores companies on the two */
    const second = el("select", { "aria-label": "Secondary genre" }, ["", ...withCurrent(GENRE_NAMES, P.intake.secondary_genre)].map(o =>
      el("option", { value: o, selected: o === (P.intake.secondary_genre || "") }, o || "None")));
    second.addEventListener("change", () => {
      if (second.value && second.value === P.intake.genre) { toast("bad", "Two different genres", "The secondary genre must differ from the primary."); second.value = P.intake.secondary_genre || ""; return; }
      P.intake.secondary_genre = second.value || null;
    });
    return { genre, subgenre: sub, secondary_genre: second };
  };
  /* Tim's intake changes (22 Oct, 1.1.3): Feature or Episodic first; the release models follow from it; festivals are
     ticked from a list; script status and sales stage are chosen. The Saracen Bridge engine uses these for narrative only. */
  const CH = SALES_OPTS.choices || {};
  const fmt = () => P.intake.format || "Feature";
  const releaseOpts = () => (CH.release_model || {})[fmt()] || L.release_model || [];
  const formatToggle = () => el("div", { class: "tabs", role: "group", "aria-label": "Format", style: "margin:0" }, (CH.format || ["Feature", "Episodic"]).map(f =>
    el("button", { type: "button", "aria-pressed": String(fmt() === f), onclick: () => {
      P.intake.format = f;
      draw();
    } }, f)));
  const festivalPick = () => {
    let v = P.intake.festival;
    if (typeof v === "string" || Array.isArray(v)) v = Array.isArray(v) ? { festivals: v, note: "" } : { festivals: [], note: v };   /* an older free-text strategy */
    v = P.intake.festival = Object.assign({ festivals: [], note: "" }, v || {});
    const label = el("span", {});
    const show = () => label.textContent = v.festivals.length ? v.festivals.join(", ") : "Choose festivals";
    const ticks = (CH.festivals || []).map(f => el("label", { class: "ms-opt" },
      el("input", { type: "checkbox", checked: v.festivals.includes(f) || null, onchange: e => {
        v.festivals = e.target.checked ? [...v.festivals, f] : v.festivals.filter(x => x !== f);
        v.festivals.sort((a, b) => CH.festivals.indexOf(a) - CH.festivals.indexOf(b)); show();
      } }), f));
    const note = el("input", { type: "text", value: v.note || "", placeholder: "Anything else: premiere status, markets, dates" });
    note.addEventListener("change", () => { v.note = note.value; });
    show();
    return el("div", { class: "ms-wrap" }, el("details", { class: "ms" }, el("summary", { "aria-label": "Festival strategy" }, label),
      el("div", { class: "ms-panel" }, el("div", { class: "ms-grid" }, ticks))), note);
  };
  /* Release model (Tim, 27 Oct, 1.1.5): each route numbered in the order it comes, 1 first; a route left without a number
     isn't used. Choosing a number puts the route there and moves the others along. An older single choice keeps its
     place as number 1, under its new name. */
  const releasePick = () => {
    const REN = { "Theatrical-led": "Theatrical", "Direct to streaming": "Straight to streaming", "Direct to TV": "Straight to TV" };
    const opts = releaseOpts();
    let v = P.intake.release_model;
    v = (typeof v === "string" ? (v ? [v] : []) : Array.isArray(v) ? v : []).map(x => REN[x] || x).filter(x => opts.includes(x));
    P.intake.release_model = v;
    const wrap = el("div", { class: "rank", role: "group", "aria-label": "Release order" });
    const drawR = () => put(wrap, opts.map(o => {
      const s = el("select", { "aria-label": `Order for ${o}` }, ["", ...opts.map((_, i) => String(i + 1))].map(n =>
        el("option", { value: n, selected: n === String(v.indexOf(o) + 1) || (n === "" && !v.includes(o)) }, n || "—")));
      s.addEventListener("change", () => {
        const rest = v.filter(x => x !== o);
        if (s.value) rest.splice(Math.min(Number(s.value) - 1, rest.length), 0, o);
        v = P.intake.release_model = rest; drawR();
      });
      return el("label", { class: "rank-opt" + (v.includes(o) ? " on" : "") }, s, o);
    }), el("span", { class: "muted small" }, "1 = first window. Leave a route at — if it isn't used."));
    drawR();
    return wrap;
  };
  /* Known sales feedback (22 Oct): which company it came from, from Jon's register, then the feedback itself */
  const feedbackPick = () => {
    let v = P.intake.sales_feedback;
    if (typeof v === "string") v = { agent: "", note: v };
    v = P.intake.sales_feedback = Object.assign({ agent: "", note: "" }, v || {});
    const who = el("select", { "aria-label": "Sales company", style: "flex:0 1 300px" }, el("option", { value: "" }, "None"),
      (SALES_AGENTS || []).map(a => el("option", { value: a.agentId, selected: a.agentId === v.agent }, a.displayName)));
    who.addEventListener("change", () => { v.agent = who.value; });
    const note = el("input", { type: "text", value: v.note || "", placeholder: "What they said, and when", style: "flex:1 1 300px" });
    note.addEventListener("change", () => { v.note = note.value; });
    return el("div", { class: "row", style: "gap:10px" }, who, note);
  };
  /* Existing sales estimate (Tim, 22 and 27 Oct, 1.1.6): a sales company's estimate by territory, ingested from its file,
     checked here, kept with the valuation and set beside it. It never changes the valuation. */
  const estimateBox = () => {
    const wrap = el("div", { style: "margin-top:4px" });
    const cur = e => (SALES_OPTS.fx && SALES_OPTS.fx[e.currency] ? e.currency : "USD");
    const show = () => {
      const e = P.existing_estimate;
      if (e) return put(wrap, el("div", { class: "row", style: "align-items:center;gap:10px" }, el("span", { class: "pill PASS" }, icon("check"), "Existing estimate kept"),
        el("span", { class: "small" }, `${e.company || "Sales company not named"}${e.date ? `, ${e.date}` : ""}: ${plural(e.rows.length, "territory", "territories")}, ask ${money(cur(e), e.total.ask)}, take ${money(cur(e), e.total.take)}`),
        el("button", { type: "button", class: "btn sm quiet", onclick: () => { P.existing_estimate = null; show(); } }, "Remove")),
        el("p", { class: "muted small", style: "margin:6px 0 0" }, "Set beside the Saracen Bridge valuation, territory by territory, when you value. It doesn't change the valuation: an estimate is a sales company's opinion, not a deal."));
      const file = el("input", { type: "file", accept: ".xlsx,.xlsm,.csv,.tsv,.txt,.docx,.pdf", "aria-label": "Existing sales estimate file" });
      const ingest = el("button", { type: "button", class: "btn sm primary", onclick: async () => {
        if (!file.files[0]) return toast("info", "Choose the estimate file first");
        ingest.disabled = true;
        const fd = new FormData(); fd.append("file", file.files[0], file.files[0].name);
        try { review(await api.form("/api/tools/sales/estimate/read", fd)); } catch (err) { toast("bad", "Couldn't read the estimate", err.message); }
        ingest.disabled = false;
      } }, icon("upload"), "Ingest");
      put(wrap, el("div", { class: "row", style: "gap:10px;align-items:center" }, file, ingest),
        el("p", { class: "muted small", style: "margin:6px 0 0" }, "A sales company's estimate by territory, as a spreadsheet, CSV, Word or PDF. You check what was read before it's kept."));
    };
    const review = r => {
      const fb = P.intake.sales_feedback || {}, agent = (SALES_AGENTS || []).find(a => a.agentId === fb.agent);
      const company = el("input", { type: "text", value: agent ? agent.displayName : "", placeholder: "Sales company", "aria-label": "Sales company" });
      const date = el("input", { type: "date", "aria-label": "Date of the estimate" });
      const currency = el("select", { "aria-label": "Currency" }, Object.keys(SALES_OPTS.fx || { USD: 1 }).map(c => el("option", { selected: c === r.currency }, c)));
      const rows = r.rows.map(x => Object.assign({}, x));
      const body = el("tbody");
      const drawRows = () => put(body, rows.map((x, i) => el("tr", {},
        el("td", {}, (() => { const t = el("select", { "aria-label": `Territory for ${x.as_written}` }, (SALES_OPTS.territories || []).map(o => el("option", { selected: o === x.territory }, o)));
          t.addEventListener("change", () => { x.territory = t.value; }); return t; })()),
        el("td", { class: "small muted" }, x.as_written, el("div", {}, x.how || "")),
        ["ask", "take"].map(k => el("td", {}, (() => { const n = el("input", { type: "number", step: "any", value: x[k] ?? "", style: "width:130px", "aria-label": `${k} for ${x.territory}` });
          n.addEventListener("change", () => { x[k] = n.value === "" ? null : Number(n.value); }); return n; })())),
        el("td", {}, el("button", { type: "button", class: "btn sm quiet", "aria-label": `Leave out ${x.territory}`, onclick: () => { rows.splice(i, 1); drawRows(); } }, icon("x"))))));
      drawRows();
      const keepIt = () => {
        const kept = rows.filter(x => x.territory);
        P.existing_estimate = { file: r.file, company: company.value.trim(), date: date.value, currency: currency.value, rows: kept,
          total: { ask: kept.reduce((a, x) => a + (x.ask || 0), 0), take: kept.reduce((a, x) => a + (x.take || 0), 0) } };
        show(); toast("ok", "Existing estimate kept", "Value the film to see it beside the Saracen Bridge figures.");
      };
      put(wrap, el("div", { class: "card", style: "margin-top:6px" },
        el("h3", { style: "margin-top:0" }, `Read from ${r.file}: ${plural(r.rows.length, "territory", "territories")}`),
        r.note ? el("p", { class: "note PRELIMINARY" }, r.note) : null,
        (r.checks || []).map(c => el("p", { class: "note PRELIMINARY" }, c)),
        el("div", { class: "row", style: "align-items:flex-end;gap:10px" }, el("label", { class: "f", style: "flex:1 1 220px" }, "Sales company", company),
          el("label", { class: "f", style: "flex:0 1 170px" }, "Date", date), el("label", { class: "f", style: "flex:0 1 110px" }, `Currency${r.currency_stated ? "" : " (not stated)"}`, currency)),
        el("div", { class: "card flush", style: "margin-top:12px" }, table(["Territory", "As written", "Ask", "Take", ""], body)),
        (r.unplaced || []).length ? el("details", { class: "lb-more", style: "margin-top:10px" }, el("summary", {}, `${plural(r.unplaced.length, "row")} not placed in a territory`),
          el("ul", { class: "plain small", style: "margin-top:8px" }, r.unplaced.map(u => el("li", {}, u)))) : null,
        el("div", { class: "row", style: "margin-top:12px;gap:10px" }, el("button", { type: "button", class: "btn primary", onclick: keepIt }, icon("check"), "Keep this estimate"),
          el("button", { type: "button", class: "btn quiet", onclick: show }, "Cancel"))));
    };
    show();
    return wrap;
  };
  const special = () => ({ ...genrePair(), festival: festivalPick(),
    sales_feedback: el("div", {}, feedbackPick(), el("div", { class: "small", style: "margin:14px 0 6px;color:var(--fg-2)" }, "Existing sales estimate (optional)"), estimateBox()),
    release_model: releasePick() });
  const fieldKind = { rating: sel("rating", L.rating || []),
    script_status: sel("script_status", CH.script_status || []), sales_stage: sel("sales_stage", CH.sales_stage || []),
    production_status: sel("production_status", L.production_status || []), budget_currency: sel("budget_currency", L.currencies || []),
    director_attachment: sel("director_attachment", SALES_OPTS.attachment), cast_attachment: sel("cast_attachment", SALES_OPTS.attachment), delivery_date: { type: "date" } };
  const input = (obj, key, kind = {}, w) => {
    const v = obj[key] ?? "";
    const n = kind.type === "select" ? el("select", {}, ["", ...kind.options].map(o => el("option", { value: o, selected: String(o) === String(v) }, o || "—")))
      : el("input", { type: kind.type === "date" ? "date" : kind.numeric ? "number" : "text", value: v, step: "any", style: w ? `width:${w}px` : "" });
    n.addEventListener("change", () => { obj[key] = n.value === "" ? null : (kind.numeric ? Number(n.value) : n.value); });
    return n;
  };
  const textArea = (obj, key) => {
    const n = el("textarea", { rows: 4, style: "height:auto;padding:10px 12px;line-height:1.45;resize:vertical" }, obj[key] ?? "");
    n.addEventListener("change", () => { obj[key] = n.value === "" ? null : n.value; });
    return n;
  };
  const section = (title, sub, body, open) => el("details", { class: "lb-more", open: open || null, style: "margin-top:16px" }, el("summary", {}, title, sub ? el("span", { class: "muted small" }, ` ${sub}`) : null), el("div", { style: "margin-top:14px" }, body));
  /* the package attached on the Actors and Directors tabs (1.0.7): new names are added, statuses brought up to date */
  const pkgMissing = () => { const pk = salesPkg(), has = (list, n) => list.some(x => String(x.name || "").toLowerCase() === n.toLowerCase());
    return pk.actors.filter(x => !has(P.actors, x.name)).length + pk.directors.filter(x => !has(P.directors, x.name)).length; };
  const takePackage = () => {
    const pk = salesPkg();
    const merge = (list, items, row) => items.forEach(x => { const had = list.find(y => String(y.name || "").toLowerCase() === x.name.toLowerCase());
      if (had) had.attachment = x.attachment; else list.push(row(x, list)); });
    merge(P.actors, pk.actors, (x, list) => ({ name: x.name, role: x.role || "", billing: list.length + 1, attachment: x.attachment }));
    merge(P.directors, pk.directors, x => ({ name: x.name, attachment: x.attachment }));
  };
  const draw = () => {
    const actorsDL = namesList("sb-actor-names", "/api/lookup/actors", "actor"), dirDL = namesList("sb-director-names", "/api/lookup/directors", "director_name");
    const films = () => P.films.map(f => f.id).filter(Boolean);
    P.rights = Object.fromEntries(T.map(t => [t, P.rights[t] || {}]));
    const rightsRows = T.map(t => Object.assign(P.rights[t], { territory: t }));
    const sp = special(), episodic = fmt() === "Episodic";
    const labelOf = f => f.key === "runtime" && episodic ? "Episode runtime (minutes)" : f.key === "logline" && P.intake.logline_from ? "Logline / synopsis (from the script's coverage)" : f.label;
    put(form,
      section("Project", "the more you give, the better the package factors", [
        el("div", { class: "row", style: "align-items:flex-end;margin-bottom:6px" }, el("label", { class: "f" }, "Format", formatToggle()),
          episodic ? el("label", { class: "f", style: "flex:0 1 160px" }, "Episodes", input(P.intake, "episodes", { numeric: true }, 140)) : null),
        el("div", { class: "row", style: "align-items:flex-end" },
        SALES_OPTS.intake.flatMap(f => [el("label", { class: "f", style: ["logline", "hook", "cast_summary", "rights_summary", "audience", "festival", "sales_feedback", "release_model"].includes(f.key) ? "flex:1 1 100%" : "flex:1 1 200px" },
          labelOf(f) + (f.required ? "" : " (optional)"), sp[f.key] || (f.key === "logline" ? textArea(P.intake, "logline") : input(P.intake, f.key, Object.assign({ numeric: f.numeric }, fieldKind[f.key] || {})))),
          f.key === "genre" ? el("label", { class: "f", style: "flex:1 1 200px" }, "Secondary genre (optional)", sp.secondary_genre) : null]))], true),
      section("Package", "cast and director from the Saracen Bridge databases, with attachment status", [actorsDL.dl, dirDL.dl,
        pkgMissing() ? el("div", { class: "notice", style: "margin-bottom:14px" }, el("div", { class: "ic" }, icon("users")),
          el("div", { class: "grow" }, el("div", {}, `${plural(pkgMissing(), "name")} attached on the Actors and Directors tabs ${pkgMissing() === 1 ? "isn't" : "aren't"} in this valuation yet`)),
          el("button", { type: "button", class: "btn sm primary", onclick: () => { takePackage(); draw(); toast("ok", "Package added", "Value with the Saracen Bridge engine to see the estimate."); } }, "Add them")) : null,
        /* Tim, 27 Oct (1.1.5): the casting director comes before the actors */
        el("div", { class: "row", style: "align-items:flex-end;margin-bottom:6px" }, el("label", { class: "f", style: "flex:0 1 380px" }, "Casting director (optional)",
          input(P.intake, "casting_director"))),
        el("h2", {}, "Cast"), editTable([{ key: "name", label: "Actor", width: 190, list: "sb-actor-names", onInput: actorsDL.onInput }, { key: "role", label: "Role", width: 130 },
          { key: "billing", label: "Billing", type: "number", width: 70 }, { key: "attachment", label: "Attachment", type: "select", options: SALES_OPTS.attachment },
          { key: "genre_fit", label: "Genre fit 0–5", type: "number", width: 80 }], P.actors, { addLabel: "Add an actor", newRow: d => ({ billing: d.length + 1, attachment: "Wish list" }) }),
        el("h2", { style: "margin-top:18px" }, "Director"), editTable([{ key: "name", label: "Director", width: 200, list: "sb-director-names", onInput: dirDL.onInput },
          { key: "attachment", label: "Attachment", type: "select", options: SALES_OPTS.attachment }, { key: "budget_fit", label: "Budget fit 0–5", type: "number", width: 80 }], P.directors,
          { addLabel: "Add a director", newRow: () => ({ attachment: "Wish list" }) })]),
      section("Evidence", "what the engine values from: deals, public proxies, or a worldwide anchor", [
        el("div", { class: "row", style: "align-items:flex-end" }, el("label", { class: "f" }, "Analyst worldwide anchor (USD)", input(P.anchor, "usd", { numeric: true }, 160)),
          el("label", { class: "f", style: "flex:1 1 320px" }, "Basis for the anchor", input(P.anchor, "note"))),
        el("p", { class: "muted small" }, "Expected Close before package and market adjustments, from documented public comparables. The Saracen Bridge engine allocates it by its territory weights at grade D, and only where no deal or proxy evidence exists."),
        el("h2", { style: "margin-top:18px" }, "Comparable films"), editTable([{ key: "id", label: "ID", width: 60 }, { key: "title", label: "Title", width: 200 }, { key: "year", label: "Year", type: "number", width: 80 },
          { key: "genre", label: "Genre", type: "select", options: GENRE_NAMES.length ? GENRE_NAMES : L.genre_profile || [] }, { key: "source", label: "Source", width: 160 }], P.films, { addLabel: "Add a film", newRow: d => ({ id: nextId(d, "F") }) }),
        el("h2", { style: "margin-top:18px" }, "Deals (verified transactions)"), editTable([{ key: "id", label: "ID", width: 60 }, { key: "film_id", label: "Film", type: "select", options: films },
          { key: "territory", label: "Territory", type: "select", options: T }, { key: "date", label: "Date", type: "date" }, { key: "stage", label: "Stage", type: "select", options: L.deal_stage || [] },
          { key: "buyer", label: "Buyer", width: 120 }, { key: "package", label: "Rights", type: "select", options: L.rights_package || [] }, { key: "term", label: "Term (yrs)", type: "number", width: 70 },
          { key: "exclusivity", label: "Exclusivity", type: "select", options: L.exclusivity || [] }, { key: "currency", label: "Currency", type: "select", options: L.currencies || [] },
          { key: "amount", label: "MG / fee", type: "number", width: 110 }, { key: "evidence_type", label: "Evidence", type: "select", options: L.evidence_type || [] },
          { key: "grade", label: "Grade", type: "select", options: ["A", "B", "C", "D"] }, { key: "source", label: "Source", width: 140 }], P.deals,
          { addLabel: "Add a deal", newRow: d => ({ id: nextId(d, "D"), term: 15, package: "All rights", exclusivity: "Exclusive", currency: "USD" }) }),
        el("h2", { style: "margin-top:18px" }, "Public proxies (buyer economics)"), editTable([{ key: "id", label: "ID", width: 60 }, { key: "film_id", label: "Film", type: "select", options: films },
          { key: "territory", label: "Territory", type: "select", options: ["Global", ...T] }, { key: "date", label: "Date", type: "date" }, { key: "category", label: "Category", type: "select", options: L.proxy_category || [] },
          { key: "box_office_usd", label: "Box office $", type: "number", width: 110 }, { key: "rental_rate", label: "Rental rate", type: "number", width: 80 }, { key: "ancillary_usd", label: "Ancillary $", type: "number", width: 100 },
          { key: "pa_usd", label: "P&A $", type: "number", width: 100 }, { key: "overhead_usd", label: "Overhead $", type: "number", width: 100 }, { key: "margin", label: "Margin", type: "number", width: 70 },
          { key: "rights_factor", label: "Rights match", type: "number", width: 70 }, { key: "relevance", label: "Relevance", type: "number", width: 70 }, { key: "source_weight", label: "Source weight", type: "number", width: 70 },
          { key: "include", label: "Use", type: "select", options: ["Y", "N"] }, { key: "source", label: "Source", width: 140 }], P.proxies,
          { addLabel: "Add a proxy", newRow: d => ({ id: nextId(d, "P"), include: "Y", rights_factor: 1 }) }),
        el("p", { class: "muted small" }, "Each deal and proxy goes into its territory's selection (up to 10 each) with adjustment factors of 1, as the Saracen Bridge workbook ships. Change factors in the workbook download for now.")]),
      section("Rights", "availability, sales and offers by territory", editTable([{ key: "territory", label: "Territory", width: 200 }, { key: "available", label: "Available", type: "select", options: ["Y", "N"] },
        { key: "status", label: "Sale status", type: "select", options: L.sale_status || [] }, { key: "offer_currency", label: "Currency", type: "select", options: L.currencies || [] },
        { key: "offer_amount", label: "Sale / offer", type: "number", width: 110 }, { key: "buyer", label: "Buyer", width: 140 }], rightsRows, { empty: "" })),
      section("Finance", "confirmed sources, in USD", el("div", { class: "row", style: "align-items:flex-end" },
        el("label", { class: "f" }, "Confirmed soft money", input(P.finance, "soft", { numeric: true }, 150)), el("label", { class: "f" }, "Confirmed equity", input(P.finance, "equity", { numeric: true }, 150)),
        el("label", { class: "f" }, "Other confirmed finance", input(P.finance, "other", { numeric: true }, 150)),
        el("label", { class: "f" }, "Report", input(P, "report", { type: "select", options: ["Producer-facing", "Lender-facing"] })))));
  };
  const value = async btn => {
    btn.disabled = true;
    put(out, el("div", { class: "muted small", style: "margin-bottom:8px" }, "Running the Saracen Bridge Sales Valuation Engine… the first run after starting the Studio takes up to a minute."), el("div", { class: "clapper" }));
    try {
      const rights = Object.fromEntries(Object.entries(P.rights).map(([t, r]) => { const x = Object.assign({}, r); delete x.territory; return [t, x]; }).filter(([, r]) => Object.values(r).some(v => v !== null && v !== "" && v !== undefined)));
      const res = await api.post("/api/tools/sales/value", { run_id: runId, project: Object.assign({}, P, { rights }) });
      runId = SALES_RUN = res.run_id;
      if (![...pick.options].some(o => o.value === runId)) pick.append(el("option", { value: runId, selected: true }, res.title));
      pick.value = runId;
      put(out, el("div", { class: "row", style: "margin-bottom:14px" }, el("a", { class: "btn", href: `/api/runs/sales/${runId}/engine.xlsx` }, icon("download"), "Download the Saracen Bridge engine, filled (.xlsx)")), salesResult(res), estimateCompare(P.existing_estimate, res));
      toast("ok", "Valued with the Saracen Bridge engine", `${res.territories.filter(t => t.status === "Complete").length} territories valued. Saved in the Library.`);
    } catch (e) { put(out, errBox(e)); }
    finally { btn.disabled = false; }
  };
  const load = async id => {
    runId = id || null; SALES_RUN = runId;
    if (!id) { P = blank(); draw(); return put(out); }
    const r = await api.get(`/api/runs/sales/${id}`);
    P = Object.assign(blank(), r.inputs || {});
    draw();
    put(out, r.outputs && r.outputs.valuation ? [el("div", { class: "row", style: "margin-bottom:14px" }, el("a", { class: "btn", href: `/api/runs/sales/${id}/engine.xlsx` }, icon("download"), "Download the Saracen Bridge engine, filled (.xlsx)")), salesResult(r.outputs.valuation), estimateCompare(P.existing_estimate, r.outputs.valuation)] : null);
  };
  pick.addEventListener("change", () => load(pick.value));
  from.addEventListener("change", async () => {
    if (!from.value) return;
    const [tool, id] = from.value.split("/");
    const pre = await api.get(`/api/tools/sales/engine/prefill?tool=${tool}&run_id=${encodeURIComponent(id)}`).catch(() => ({}));
    Object.entries(pre).forEach(([k, v]) => { if (v !== "" && v !== null && (P.intake[k] === undefined || P.intake[k] === null || P.intake[k] === "")) P.intake[k] = v; });
    draw();
    const got = [pre.title && "title", pre.budget && "budget", pre.logline && "logline and synopsis from its coverage"].filter(Boolean);
    toast("info", "Filled from the Library", (got.length ? `Took the ${got.join(", ")}.` : "") +
      (pre.logline ? "" : " No coverage for this script yet: write its coverage in Script Coverage and the logline and synopsis come with it."));
  });
  box.append(el("p", { class: "muted", style: "margin:0 0 14px" }, "The Saracen Bridge Sales Valuation Engine v4.1, run exactly as his workbook calculates. It values each territory from verified deals, public buyer-economics proxies, or a documented worldwide anchor, and never from the budget alone."),
    el("div", { class: "row", style: "align-items:flex-end" }, el("label", { class: "f", style: "flex:1 1 260px" }, "Valuation", pick), el("label", { class: "f", style: "flex:1 1 260px" }, "Prefill", from)),
    form, el("div", { class: "row", style: "margin-top:18px" }, el("button", { type: "button", class: "btn primary", onclick: ev => value(ev.currentTarget) }, icon("sparkle"), "Value with the Saracen Bridge engine")), out);
  if (runId) await load(runId); else draw();
  if (SALES_PKG_APPLY) {                                   /* arrived from "Value this package" */
    SALES_PKG_APPLY = false; takePackage(); draw();
    const pk = salesPkg();
    toast("ok", "Package added to the valuation", `${plural(pk.actors.length, "actor")} and ${plural(pk.directors.length, "director")} are in the Package section. Add the evidence, then Value with the Saracen Bridge engine.`);
    form.querySelector("details:nth-of-type(2)")?.setAttribute("open", "");
  }
}

/* ---------------- tool panels ---------------- */
/* ---------------- Casting Director (1.1.6) ----------------
   Tim, 27 Oct: casting suggestions for a broken-down script. Roles from the breakdown, each read by the AI (gender,
   playing age, a breakdown line) and shortlisted from the Saracen Bridge Actor Value Database only. */
let CASTING_RUN = null;
async function castingPanel(box) {
  const wait = el("div", { class: "clapper" }); box.append(wait);
  const { runs } = await api.get("/api/runs?limit=200");
  wait.remove();
  const scripts = runs.filter(r => ["coverage", "schedule", "brand"].includes(r.tool) && (r.summary || {}).scene_count);
  if (!scripts.length) return box.append(el("div", { class: "drop", style: "border-style:solid" }, el("div", { class: "art" }, icon("casting")),
    el("div", { class: "big" }, "Read a script first"), el("p", {}, "Drop it on Script Coverage or Scheduling & Budgeting. Its breakdown gives the roles to cast."),
    el("div", { class: "row" }, el("a", { class: "btn", href: "#/tool/coverage" }, "Open Script Coverage"))));
  /* Tim's genres from the Sales Agents register (quick); the sales engine's options load the whole workbook */
  const GN = SALES_OPTS ? (SALES_OPTS.genres || []).map(g => g.genre) : ((await api.get("/api/agents").catch(() => ({ genres: [] }))).genres || []).map(g => g.name);
  const key = r => `${r.tool}/${r.id}`;
  if (!scripts.some(r => key(r) === CASTING_RUN)) CASTING_RUN = key(scripts[0]);
  const pick = el("select", { "aria-label": "Script" }, scripts.map(r => el("option", { value: key(r), selected: key(r) === CASTING_RUN },
    `${r.title} · ${(toolById(r.tool) || {}).name || r.tool} · ${plural(r.summary.scene_count, "scene")}`)));
  const genre = el("select", { "aria-label": "Genre" }, ["", ...GN].map(g => el("option", { value: g }, g || "Any genre")));
  const budget = el("input", { type: "number", min: 0, step: "any", placeholder: "e.g. 5000000", "aria-label": "Budget in US dollars", style: "width:170px" });
  const out = el("div", { style: "margin-top:18px" });
  let data = null;
  const load = async () => {
    CASTING_RUN = pick.value;
    put(out, el("div", { class: "clapper" }));
    try { data = await api.get(`/api/casting/${pick.value}`); } catch (e) { return put(out, errBox(e)); }
    render();
  };
  const save = async body => { try { data = await api.put(`/api/casting/${pick.value}`, body); render(); } catch (e) { toast("bad", "Couldn't save", e.message); } };
  pick.addEventListener("change", load);
  genre.addEventListener("change", () => save({ genre: genre.value || null }));
  budget.addEventListener("change", () => save({ budget_usd: budget.value === "" ? null : Number(budget.value) }));
  const sizeSel = r => { const n = el("select", { "aria-label": `Size of part for ${r.name}` }, ["Lead", "Supporting", "Featured"].map(x => el("option", { selected: x === r.size }, x)));
    n.addEventListener("change", () => save({ edits: { [r.name]: { size: n.value } } })); return n; };
  const ageText = r => (r.age_low || r.age_high) && r.age_low !== null && r.age_low !== undefined ? (r.age_low === r.age_high ? `${r.age_low}` : `${r.age_low}–${r.age_high}`) : "age not known";
  const addBtn = (a, r) => pkgFind("actors", a.actor) ? el("span", { class: "pill PASS" }, icon("check"), "In the package")
    : el("button", { type: "button", class: "btn sm", onclick: () => { pkgAttach("actors", a.actor, "Wish list", { role: r.name }); toast("ok", `${a.actor} added as Wish list`, `For ${r.name}. Value the package in Sales Estimates when it's ready.`); render(); } }, icon("plus"), "Add to package");
  const roleCard = r => {
    const rd = r.read || {};
    const said = rd.edited ? " (corrected)" : rd.source === "model" ? (rd.stated ? " (as the script says)" : " (the AI's reading)") : rd.source === "script" ? " (age printed in the script)" : "";
    const g = el("select", { "aria-label": "Gender" }, [["Female", "Female"], ["Male", "Male"], ["Non-binary", "Non-binary"], ["Any", "Open to any gender"]].map(([v, l]) => el("option", { value: v, selected: v === r.gender }, l)));
    const lo = el("input", { type: "number", min: 0, max: 100, value: r.age_low ?? "", "aria-label": "Youngest playing age", style: "width:80px" });
    const hi = el("input", { type: "number", min: 0, max: 100, value: r.age_high ?? "", "aria-label": "Oldest playing age", style: "width:80px" });
    const desc = el("input", { type: "text", value: rd.description || "", placeholder: "One line for the breakdown", "aria-label": "Description" });
    const editor = el("div", { class: "row", style: "gap:10px;align-items:flex-end;margin-top:12px;display:none" },
      el("label", { class: "f", style: "flex:0 1 200px" }, "Gender", g), el("label", { class: "f", style: "flex:0 1 auto" }, "Playing age", el("div", { class: "row", style: "gap:6px;flex-wrap:nowrap" }, lo, hi)),
      el("label", { class: "f", style: "flex:1 1 260px" }, "Description", desc), el("label", { class: "f", style: "flex:0 1 150px" }, "Size of part", sizeSel(r)),
      el("button", { type: "button", class: "btn sm primary", onclick: () => save({ edits: { [r.name]: { gender: g.value, age_low: lo.value, age_high: hi.value, description: desc.value } } }) }, "Save"),
      rd.edited ? el("button", { type: "button", class: "btn sm quiet", onclick: () => save({ edits: { [r.name]: { reset: true } } }) }, "Undo my changes") : null);
    const rows = r.shortlist.map(a => el("tr", {}, el("td", {}, el("b", {}, a.actor), el("div", { class: "small muted" }, a.sales_role || "")),
      el("td", {}, a.tier || "—"), el("td", { class: "num", title: a.value_basis }, fmt(a.value, 1)), el("td", { class: "small" }, `${usd(a.fee_low)}–${usd(a.fee_high)}`),
      el("td", { class: "small" }, `from ${usd(a.min_budget)}`, el("div", { class: "muted" }, `optimal ${usd(a.optimal_floor)}+`)),
      el("td", { class: "small" }, a.genres || "—", a.genre_match ? el("div", {}, el("span", { class: "pill PASS" }, "genre match")) : null),
      el("td", { class: "small muted" }, a.why.join("; "), el("div", {}, `Confidence ${a.confidence}, reviewed ${a.reviewed || "—"}`)), el("td", {}, addBtn(a, r))));
    return el("div", { class: "card", style: "margin-top:16px" },
      el("div", { class: "row", style: "justify-content:space-between;align-items:baseline;gap:10px" },
        el("h2", { style: "margin:0" }, r.name, " ", el("span", { class: "pill " + (r.size === "Lead" ? "AI" : "") }, r.size)),
        el("span", { class: "small muted" }, `${plural(r.scenes, "scene")} (${Math.round(r.share * 100)}%) · ${plural(r.dialogue, "speech", "speeches")} · ${plural(r.days, "shooting day")} · first in scene ${r.first_scene}`)),
      el("p", { style: "margin:10px 0 0" }, el("b", {}, `${r.gender === "Any" ? "Open to any gender" : r.gender}, ${ageText(r)}`), rd.description ? `: ${rd.description}` : "",
        el("span", { class: "muted small" }, said), " ", el("button", { type: "button", class: "btn sm quiet", onclick: () => { editor.style.display = editor.style.display === "none" ? "flex" : "none"; } }, "Correct")),
      editor,
      (r.flags || []).map(f => el("p", { class: "note PRELIMINARY", style: "margin-top:10px" }, f)),
      r.shortlist.length ? el("div", { class: "card flush", style: "margin-top:14px" }, table(["Actor", "Tier", "#Value", "Fee range", "Budget", "Genres", "Why", ""], rows))
        : el("p", { class: "note PRELIMINARY" }, r.over_budget ? `${plural(r.over_budget, "actor")} in the database fit${r.over_budget === 1 ? "s" : ""} the part but need a bigger budget.` : "No one in the database fits this reading. Check the gender and age, or widen the age."),
      el("p", { class: "small muted", style: "margin:10px 0 0" }, `${plural(r.considered, "actor")} in the database fit ${[r.filters.gender, r.filters.bands.length < 5 ? `playing age ${r.filters.bands.join(" or ")}` : null].filter(Boolean).join(", ") || "any gender and age"}`,
        r.over_budget ? `; ${fmt(r.over_budget)} of them need a bigger budget.` : ".", r.size === "Lead" ? " Ranked by composite cast value." : " Ranked by supporting value.", data.genre ? ` ${data.genre} matches first.` : ""));
  };
  const render = () => {
    genre.value = data.genre || ""; budget.value = data.budget_usd ?? "";
    const [tool, id] = pick.value.split("/");
    const watch = jobWatch("casting", tool, id, () => load());
    const read = async ev => {
      const btn = ev.currentTarget; btn.disabled = true;
      try { await api.post(`/api/casting/${pick.value}/read`, { mode: MODE }); toast("ai", "Reading the roles", `Gemma reads each principal role where the script brings it in. On ${runsOn()}.`); pollJobs(); watch.start(); }
      catch (e) { toast("bad", "Couldn't start", el("span", {}, e.message, " ", el("a", { href: "#/settings" }, "Settings"))); }
      btn.disabled = false;
    };
    put(out,
      el("div", { class: "notice", style: "align-items:flex-start" }, el("div", { class: "ic" }, icon("sparkle")),
        el("div", { class: "grow" }, el("div", {}, data.read ? `Roles read by ${data.read.engine}, ${data.read.mode} reasoning (${data.read.date || ""})` : "The AI hasn't read the roles yet: gender and age come only from what the script prints beside a name."),
          el("div", { class: "small muted" }, "It reads each principal role where the script brings it in. Check each reading and correct any you disagree with: the shortlist follows."), watch),
        el("button", { type: "button", class: "btn sm primary", onclick: read }, icon("sparkle"), data.read ? "Read again" : "Read the roles")),
      el("div", { class: "kpis", style: "margin-top:16px" }, kpi("Principal roles", data.roles.length), kpi("Featured parts", data.featured.length),
        kpi("Budget", data.budget_usd ? usd(data.budget_usd) : "Not set"), kpi("Actors in the database", fmt(data.actors))),
      data.prefill_from ? el("p", { class: "muted small", style: "margin:8px 0 0" }, `Genre and budget from the Sales Estimates valuation “${data.prefill_from}”.`) : null,
      data.budget_usd ? null : el("p", { class: "muted small", style: "margin:8px 0 0" }, "Add the budget to leave out actors whose minimum sensible budget is above it."),
      data.roles.map(roleCard),
      data.featured.length ? el("details", { class: "lb-more", style: "margin-top:16px" }, el("summary", {}, `Featured parts (${data.featured.length})`, el("span", { class: "muted small" }, " make one supporting or lead to shortlist it")),
        el("div", { class: "card flush", style: "margin-top:12px" }, table(["Role", "#Scenes", "#Speeches", "#Days", "Size"], data.featured.map(f => el("tr", {},
          el("td", {}, el("b", {}, f.name)), el("td", { class: "num" }, f.scenes), el("td", { class: "num" }, f.dialogue), el("td", { class: "num" }, f.days), el("td", {}, sizeSel(f))))))) : null,
      el("p", { class: "muted small", style: "margin-top:18px" }, "Suggestions come only from the Saracen Bridge Actor Value Database, matched on gender and playing-age band, with the film's genre first. Fees, values and budget floors are the database's indicative figures; availability and interest are not known. Nobody is attached: a suggestion goes to the package as Wish list, which counts for nothing in the estimate until the deal moves. Size of part is read from the script (lead: one of the two largest parts in a quarter or more of the scenes; supporting: 8% or more, or 15 speeches)."));
  };
  box.append(el("div", { class: "row", style: "align-items:flex-end" },
    el("label", { class: "f", style: "flex:1 1 320px" }, "Script", pick), el("label", { class: "f", style: "flex:0 1 220px" }, "Genre", genre),
    el("label", { class: "f", style: "flex:0 1 auto" }, "Budget (USD)", budget)), out);
  await load();
}

const PANELS = {
  casting(box) { return castingPanel(box); },
  ai_only(box, t) {
    box.append(el("div", { class: "drop", style: "border-style:solid" }, el("div", { class: "art" }, icon("sparkle")), el("div", { class: "big" }, "Coming to the Studio"),
      el("p", {}, `${t.name} reads and judges material: ${t.needs_ai.join("; ").toLowerCase()}. It runs on the AI engine once it's built.`),
      el("div", { class: "row" }, el("a", { class: "btn", href: "#/settings" }, "AI engine settings"))));
  },
  coverage(box) {
    const q = queuePanel("coverage");
    box.append(q.box);
    tabs(box, [["Scripts", b => scriptIntake(b, "coverage", rows => {
      const ids = rows.filter(r => r.run_id && !r.error).map(r => r.run_id);
      if (!ids.length) return null;
      return el("button", { type: "button", class: "btn primary", style: "margin-top:16px", onclick: async ev => {
        ev.currentTarget.disabled = true;
        try { const r = await api.post("/api/tools/coverage/write", { run_ids: ids, mode: MODE }); toast("ai", `${plural(r.queued, "script")} queued for coverage`, `On ${runsOn()}, ${r.mode} reasoning. You can keep working; the queue runs in the background.`); }
        catch (e) { toast("bad", "Couldn't queue coverage", e.message); ev.currentTarget && (ev.currentTarget.disabled = false); }
        q.draw();
      } }, icon("sparkle"), ids.length === 1 ? "Write coverage for this script" : `Write coverage for these ${ids.length} scripts`);
    })], ["Scoring matrix", async b => {
      const w = await api.get("/api/tools/coverage/weights");
      const inputs = Object.keys(w).map(k => [k, el("input", { type: "number", min: 1, max: 10, step: 0.5, "aria-label": k })]);
      const out = el("div", { style: "margin-top:16px" });
      b.append(el("div", { class: "card flush" }, table(["Category", "#Weight", "Score 1–10"], inputs.map(([k, i]) => el("tr", {}, el("td", {}, k), el("td", { class: "num" }, pct(w[k])), el("td", {}, i))))),
        el("div", { class: "row", style: "margin-top:16px" }, el("button", { type: "button", class: "btn primary", onclick: async () => {
          const r = await api.post("/api/tools/coverage/score", Object.fromEntries(inputs.map(([k, i]) => [k, i.value === "" ? null : Number(i.value)])));
          put(out, r.composite === null ? el("p", { class: "note PRELIMINARY" }, "Score every category: " + r.missing.join(", ")) :
            [el("div", { class: "kpi edge", style: "max-width:280px" }, el("div", { class: "l" }, "Composite score"), el("div", { class: "v" }, `${r.composite} / 10`)), el("p", { class: "muted small" }, r.note)]);
        } }, "Calculate")), out);
    }]]);
  },
  lookbook(box) {
    if (aiWrites() && !AI.vision) box.append(el("div", { class: "notice", style: "margin:0 0 20px" }, el("div", { class: "ic" }, icon("sparkle")),
      el("div", { class: "grow" }, el("div", {}, "Gemma can't see pages yet"), el("div", { class: "sub" }, AI.vision_reason || "Connect an AI engine that reads images.")),
      el("a", { class: "btn sm", href: "#/settings" }, "Settings")));
    const q = queuePanel("lookbook");
    box.append(q.box);
    const f = (label, node, wide) => el("label", { class: "f", style: wide ? "flex:1 1 100%" : "flex:1 1 220px" }, label, node);
    const inp = ph => el("input", { type: "text", placeholder: ph });
    const area = ph => el("textarea", { rows: 2, placeholder: ph, style: "height:auto;min-height:64px;padding:10px 12px;resize:vertical" });
    const fields = {
      title: inp("Taken from the file name if blank"), format: el("select", {}, ["Feature film", "TV series", "Limited series", "Short", "Documentary"].map(x => el("option", {}, x))),
      logline: area("If the deck has one, leave blank: the analysis judges the deck's own"), cast: inp("Confirmed attachments only"), director: inp("Confirmed attachment only"),
      budget: inp("e.g. £3–4m"), comparables: inp("Titles you compare it to"), opinion: area("Your honest view of the deck. The analysis uses it to guide its tone and focus."),
    };
    const out = el("div", {});
    const input = el("input", { type: "file", multiple: true, accept: ".pdf,.png,.jpg,.jpeg,.webp", style: "display:none" });
    const run = async files => {
      const list = [...files];
      if (!list.length) return;
      const fd = new FormData();
      list.forEach(x => fd.append("files", x, x.name));
      Object.entries(fields).forEach(([k, n]) => fd.append(k, n.value || ""));
      put(out, el("div", { style: "margin-top:18px" }, el("div", { class: "muted small", style: "margin-bottom:8px" }, `Reading ${list.length > 1 ? list.length + " images" : list[0].name}…`), el("div", { class: "clapper" })));
      try {
        const r = await api.form("/api/tools/lookbook/intake", fd);
        toast(r.duplicate ? "info" : "ok", r.duplicate ? "This deck is already in the Library" : `${plural(r.pages, "page")} read`, r.title);
        put(out, el("div", { class: "card", style: "margin-top:18px;background:var(--ink-1)" },
          el("div", { class: "row", style: "justify-content:space-between;align-items:center" }, el("h2", { style: "margin:0" }, r.title, el("span", { class: "count" }, plural(r.pages, "page"))),
            el("a", { class: "btn sm quiet", href: `#/run/lookbook/${r.run_id}` }, "Open", icon("arrow"))),
          pageStrip(r.run_id, r.pages),
          el("div", { class: "row", style: "margin-top:16px;align-items:center" }, modeSwitch(),
            el("button", { type: "button", class: "btn primary", onclick: async ev => {
              const b = ev.currentTarget; b.disabled = true;
              try { const a = await api.post("/api/tools/lookbook/analyse", { run_ids: [r.run_id], mode: MODE }); toast("ai", "Look book queued", `Gemma looks at every page, then writes the Saracen Bridge 16-section analysis. On ${runsOn()}.`); q.draw(); pollJobs(); }
              catch (e) { toast("bad", "Couldn't start the analysis", e.message); b.disabled = false; }
            } }, icon("sparkle"), "Analyse this look book"))));
      } catch (e) { put(out); toast("bad", "Couldn't read the deck", e.message); }
    };
    input.addEventListener("change", () => input.files.length && run(input.files));
    const drop = el("div", { class: "drop" }, el("div", { class: "art" }, icon("lookbook")), el("div", { class: "big" }, "Drop the look book here"),
      el("p", {}, "A PDF of the deck, or its pages as images. PowerPoint or Keynote: export to PDF first."),
      el("div", { class: "row" }, el("button", { type: "button", class: "btn primary", onclick: () => input.click() }, "Choose the deck")));
    drop.addEventListener("dragover", e => { e.preventDefault(); drop.classList.add("over"); });
    drop.addEventListener("dragleave", () => drop.classList.remove("over"));
    drop.addEventListener("drop", e => { e.preventDefault(); drop.classList.remove("over"); run(e.dataTransfer.files); });
    box.append(drop, input,
      el("details", { class: "lb-more" }, el("summary", {}, "Add what the deck doesn't say", el("span", { class: "muted small" }, " (optional: attachments, budget, your view)")),
        el("div", { class: "row", style: "margin-top:14px" }, f("Title", fields.title), f("Format", fields.format), f("Logline", fields.logline, true),
          f("Attached cast", fields.cast), f("Attached director", fields.director), f("Budget", fields.budget), f("Comparables", fields.comparables), f("Your view of the deck", fields.opinion, true))),
      out);
  },
  schedule(box) {
    const toBudget = id => { BUDGET_RUN = id; BUDGET_OPEN = true; route(); };
    tabs(box, [["Script breakdown", b => scriptIntake(b, "schedule", rows => {
      const ok = rows.filter(r => r.run_id && !r.error);
      return ok.length ? el("button", { type: "button", class: "btn primary", style: "margin-top:16px", onclick: () => toBudget(ok[0].run_id) }, icon("schedule"),
        ok.length === 1 ? "Schedule and budget this script" : `Schedule and budget ${ok[0].title}`) : null;
    })], ["Schedule & budget", b => budgetPanel(b), true], ["Crew rates", async b => {
      const first = await api.get("/api/lookup/rates?jurisdiction=United%20Kingdom");
      const sel = el("select", { "aria-label": "Jurisdiction" }, first.jurisdictions.map(j => el("option", { value: j, selected: j === "United Kingdom" }, j)));
      const q = el("input", { type: "search", placeholder: "Role or department, e.g. Gaffer", "aria-label": "Role or department", style: "flex:1;min-width:220px" });
      const typ = el("select", { "aria-label": "Production type" });
      const out = el("div", { style: "margin-top:16px" });
      const go = async (resetType) => {
        try {
          if (resetType) typ.value = "";
          const r = await api.get(`/api/lookup/rates?jurisdiction=${encodeURIComponent(sel.value)}&q=${encodeURIComponent(q.value)}&production_type=${encodeURIComponent(typ.value)}`);
          const keepType = typ.value;
          put(typ, el("option", { value: "" }, "All production types"), r.types.map(t => el("option", { value: t, selected: t === keepType }, t)));
          const cur = (r.rows[0] || {}).currency || "";
          const check = v => /quote/i.test(v || "") ? el("span", { class: "pill PRELIMINARY" }, "Quote") : /published/i.test(v || "") ? el("span", { class: "pill PASS" }, "Published") : el("span", { class: "muted" }, v || "—");
          put(out, el("p", { class: "muted small", style: "margin:0 0 10px" }, `${plural(r.rows.length, "role")} · ${r.basis === "four_tier" ? "four experience tiers" : "official minimum plus market bands"}${cur ? ` · all figures in ${cur}` : ""}`),
            el("div", { class: "card flush" }, table(["Role", ...r.labels.map(l => "#" + l.replace(" / ", " /\u00a0")), "Check"], r.rows.map(x => el("tr", { title: [x.rate_status, x.notes].filter(Boolean).join(" · ") || null },
              el("td", { class: "role" }, el("b", {}, x.role), el("div", { class: "small muted" }, [x.department, x.production_type].filter(Boolean).join(" · ")), x.local_role ? el("div", { class: "small muted" }, x.local_role) : null),
              x.negotiated ? el("td", { colspan: 5, class: "small muted" }, "Negotiated: ", x.notes || "no card rate") : ["d1", "d2", "d3", "d4", "week"].map(k => el("td", { class: "num" }, fmt(x[k]))),
              el("td", { title: x.rate_status || null }, check(x.validation_status)))))),
            el("p", { class: "muted small" }, "From the Saracen Bridge 2026 rate cards. Quote means a market or negotiated figure: confirm with the union card or a quote before budgeting. Hover a row for its basis and notes."));
        } catch (e) { put(out, errBox(e)); }
      };
      let timer;
      sel.addEventListener("change", () => go(true)); typ.addEventListener("change", () => go(false));
      q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(() => go(false), 180); });
      q.addEventListener("keydown", e => { if (e.key === "Enter") { clearTimeout(timer); go(false); } });
      b.append(el("div", { class: "row" }, q, sel, typ), out); go(false);
    }, true]], BUDGET_OPEN ? 1 : 0);
    BUDGET_OPEN = false;
  },
  brand(box) {
    tabs(box, [["Brand database", b => brandDatabase(b), true],
      ["Script intake", b => scriptIntake(b, "brand")]]);
  },
  sales(box) {
    tabs(box, [["Actors", b => b.append(pkgBar()) || finder(b, { label: "Find an actor", placeholder: "Start typing a name, e.g. Chris", hint: "Type a few letters: the list narrows as you go. Pick a name to see their sales value, fee range and budget floor.",
        search: q => `/api/lookup/actors?q=${encodeURIComponent(q)}&limit=12`, name: a => a.actor,
        meta: a => [a.commercial_tier && `Tier ${a.commercial_tier}`, a.sales_role].filter(Boolean).join(" · "),
        open: async (a, out) => put(out, actorCard(await api.get(`/api/lookup/actor?name=${encodeURIComponent(a.actor)}`))) })],
      ["Directors", b => b.append(pkgBar()) || finder(b, { label: "Find a director", placeholder: "Start typing a name, e.g. Nolan", hint: "Type a few letters: the list narrows as you go. Pick a name to see their fee bands and proven budget range.",
        search: q => `/api/lookup/directors?q=${encodeURIComponent(q)}&limit=12`, name: d => d.director_name,
        meta: d => [String(d.commercial_tier || "").split(/\s+[–-]\s+/)[0] && `Tier ${String(d.commercial_tier).split(/\s+[–-]\s+/)[0]}`, d.career_stage, d.primary_genre].filter(Boolean).join(" · "),
        open: async (d, out) => put(out, directorCard(await api.get(`/api/lookup/director?id=${encodeURIComponent(d.director_id)}`))) })],
      ["Territory valuation", b => valuationPanel(b), true],
      /* Tim, 27 Oct (1.1.5): Sales Agents lives here, off the main menu */
      ["Sales Agents", b => PANELS.agents(b), true]], SALES_OPEN === "agents" ? 3 : SALES_OPEN ? 2 : 0);
    SALES_OPEN = false;
  },
  /* Sales Agents (22 Oct): Jon's Sales Agent scoring specification v1.0. Each company's base score, reduced where it
     fits the film's genre less well, worked out on the server by his formula and shown with its explanation. */
  async agents(box) {
    const R = await api.get("/api/agents");
    const FL = R.fit_labels, FITS = R.fits, GN = Object.fromEntries(R.genres.map(g => [g.id, g.name]));
    const me = () => { try { return localStorage.getItem("sb-assessor") || ""; } catch (_) { return ""; } };
    const rememberMe = n => { try { localStorage.setItem("sb-assessor", n); } catch (_) {} };
    const scoreCell = r => r.result && r.result.status === "SCORED"
      ? el("b", { style: "font-size:18px" }, `${r.result.adjustedScore}`, el("span", { class: "muted small" }, "/100")) : el("span", { class: "muted small" },
        { NEEDS_REVIEW: "Genre fit unverified", SCOPE_MISMATCH: "Score unavailable for this mandate", INVALID_INPUT: "Unrated" }[(r.result || {}).status] || "—");
    const links = a => (a.sourceUrls || []).map(u => el("a", { href: u, target: "_blank", rel: "noopener", class: "small", style: "margin-left:8px" }, "profile"));
    box.append(el("p", { class: "muted", style: "margin:0 0 14px" }, "The Saracen Bridge register of sales companies, scored for a film by his specification: the base score, reduced where the company fits the film's genre less well. Base scores and fits are provisional internal assessments, not measured sales success, estimate accuracy or payment reliability, and they never change the valuation's figures."));
    tabs(box, [["Compare for a film", async b => {
      const { runs } = await api.get("/api/runs?tool=sales&limit=200");
      let project = AGENTS_PROJECT && runs.some(r => r.id === AGENTS_PROJECT) ? AGENTS_PROJECT : (runs[0] || {}).id || "", scope = "INTERNATIONAL_SALES";
      const pick = el("select", { "aria-label": "Valuation" }, el("option", { value: "" }, runs.length ? "No film: base scores only" : "No valuations yet"),
        runs.map(r => el("option", { value: r.id, selected: r.id === project }, r.title)));
      const who = el("input", { type: "text", value: me(), placeholder: "Your name", "aria-label": "Assessor" });
      who.addEventListener("change", () => rememberMe(who.value.trim()));
      const scopeBar = el("div", { class: "tabs", role: "group", "aria-label": "Mandate", style: "margin:0" });
      const genresBox = el("div", {}), out = el("div", { style: "margin-top:16px" });
      const fitAsk = async (row, gid, fit) => {
        if (!who.value.trim()) { toast("bad", "Your name first", "Each fit is recorded with who assessed it."); who.focus(); return false; }
        const rationale = el("textarea", { rows: 3, style: "height:auto;padding:10px 12px;width:100%", placeholder: fit === "OUTSIDE" ? "Why its focus sits substantially elsewhere" : "Why this fit, in a sentence" });
        const evidence = el("input", { type: "text", style: "width:100%", value: "Company register speciality text (" + R.dataVersion + ")", "aria-label": "Evidence" });
        const verified = el("input", { type: "checkbox" }), keep = el("input", { type: "checkbox" });
        const ok = fit === "UNVERIFIED" ? true : await modal({ icon: "users", title: `${row.displayName}: ${FL[fit]} for ${GN[gid]}`, body: [
          el("label", { class: "f" }, "Rationale", rationale), el("label", { class: "f", style: "margin-top:10px" }, "Source or internal evidence reference", evidence),
          el("label", { class: "small", style: "display:flex;align-items:center;margin-top:12px" }, verified, "Verified evidence (otherwise provisional)"),
          el("label", { class: "small", style: "display:flex;align-items:center;margin-top:8px" }, keep, `Approve as ${row.displayName}'s fit for ${GN[gid]} on later films`)],
          actions: [["Cancel", false], ["Save", true, true]] });
        if (!ok) return false;
        try {
          await api.post("/api/agents/fit", { project, agent: row.agentId, genre: gid, fit, rationale: rationale.value, evidence: evidence.value,
            assessor: who.value.trim(), evidence_status: verified.checked ? "VERIFIED" : "PROVISIONAL", mandate: scope, save_mapping: keep.checked });
          return true;
        } catch (e) { toast("bad", "Fit not saved", e.message); return false; }
      };
      const fitSel = (row, side) => {
        const gid = side === "primary" ? C.project.primaryGenreId : C.project.secondaryGenreId, f = row[side] || {};
        if (!gid) return el("span", { class: "muted small" }, "—");
        const s = el("select", { "aria-label": `${side} fit for ${row.displayName}`, style: "min-width:150px" }, FITS.map(x => el("option", { value: x, selected: x === f.fit }, FL[x])));
        s.addEventListener("change", async () => { if (await fitAsk(row, gid, s.value)) draw(); else s.value = f.fit; });
        const by = f.assessedBy ? `${f.from === "approved mapping" ? "Approved mapping" : "Assessed"} by ${f.assessedBy}, ${String(f.assessedAt || "").slice(0, 10)}${f.evidenceStatus === "VERIFIED" ? " · verified" : ""}${f.rationale ? ": " + f.rationale : ""}` : "";
        return el("div", { title: by }, s, by ? el("div", { class: "small muted", style: "margin-top:4px;max-width:220px" }, f.from === "approved mapping" ? "Approved mapping" : (f.assessedBy || "")) : null);
      };
      const rowEl = (r, i) => el("tr", {},
        el("td", { class: "num" }, i == null ? "" : i + 1),
        el("td", { style: "min-width:280px" }, el("b", {}, r.displayName), links(r), el("div", { class: "small muted", style: "margin-top:4px;max-width:360px" }, r.explanation || ""),
          r.provisional ? el("span", { class: "pill PRELIMINARY", style: "margin-top:6px" }, "Provisional") : null),
        el("td", { class: "small", style: "max-width:240px" }, r.specialityText),
        el("td", { class: "num" }, r.baseScore == null ? "Unrated" : `${r.baseScore}/100`),
        el("td", {}, C.project ? fitSel(r, "primary") : "—"), el("td", {}, C.project && C.project.secondaryGenreId ? fitSel(r, "secondary") : el("span", { class: "muted small" }, "—")),
        el("td", { class: "num" }, r.result && r.result.status === "SCORED" ? `${+r.result.discountPercent.toFixed(2)}%` : "—"),
        el("td", { class: "num" }, scoreCell(r)),
        el("td", { class: "small muted" }, r.estimateAccuracyScore == null ? "Unrated" : r.estimateAccuracyScore),
        el("td", { class: "small muted" }, r.trustworthinessScore == null ? "Unrated" : r.trustworthinessScore));
      const heads = ["#", "Company", "Genre speciality", "#Base score", "Primary fit", "Secondary fit", "#Genre discount", "#Adjusted score", "Estimate accuracy", "Trustworthiness"];
      let C = null;
      const draw = async () => {
        AGENTS_PROJECT = project;
        put(scopeBar, Object.entries(R.scopes).map(([k, label]) => el("button", { type: "button", "aria-pressed": String(scope === k), onclick: () => { scope = k; draw(); } }, label)));
        C = await api.get(`/api/agents/compare?scope=${scope}` + (project ? `&project=${encodeURIComponent(project)}` : ""));
        if (C.project) {
          const g1 = el("select", { "aria-label": "Primary genre" }, el("option", { value: "" }, "—"), R.genres.map(g => el("option", { value: g.id, selected: g.id === C.project.primaryGenreId }, g.name)));
          const g2 = el("select", { "aria-label": "Secondary genre" }, el("option", { value: "" }, "None"), R.genres.map(g => el("option", { value: g.id, selected: g.id === C.project.secondaryGenreId }, g.name)));
          const save = async () => {
            if (g1.value && g1.value === g2.value) { toast("bad", "Two different genres", "The secondary genre must differ from the primary."); g2.value = C.project.secondaryGenreId || ""; return; }
            try { await api.put(`/api/agents/project/${encodeURIComponent(project)}`, { primary: g1.value, secondary: g2.value || null }); toast("ok", "Genres saved to the valuation", "Every company is scored again for them."); draw(); }
            catch (e) { toast("bad", "Genres not saved", e.message); }
          };
          g1.addEventListener("change", save); g2.addEventListener("change", save);
          const suggest = el("button", { type: "button", class: "btn sm", onclick: async ev => {
            const btn = ev.currentTarget; btn.disabled = true; const w = toast("ai", "Jonny is assessing the fits", "From each company's speciality; a minute or so on this computer.", 120000);
            try { const r = await api.post("/api/agents/suggest", { project, mode: MODE }); toast("ok", `${plural(r.assessed, "fit")} suggested`, "Marked provisional, with Jonny as the assessor. Change any you disagree with."); draw(); }
            catch (e) { toast("bad", "No suggestions", e.message); } finally { btn.disabled = false; typeof w === "function" && w(); }
          } }, icon("sparkle"), "Suggest unassessed fits");
          put(genresBox, el("div", { class: "row", style: "align-items:flex-end;margin-top:14px" },
            el("label", { class: "f", style: "flex:0 1 220px" }, "Primary genre", g1), el("label", { class: "f", style: "flex:0 1 220px" }, "Secondary genre (if material)", g2),
            el("div", { class: "row", style: "gap:8px" }, suggest, el("a", { class: "btn sm", href: `/api/agents/compare.csv?scope=${scope}&project=${encodeURIComponent(project)}` }, icon("download"), "Export (.csv)"))),
            el("p", { class: "muted small", style: "margin:8px 0 0" }, "The valuation's own genres, one classification for every company. With two genres the score weighs the primary 70% and the secondary 30%."));
        } else put(genresBox, el("p", { class: "muted small", style: "margin:12px 0 0" }, runs.length ? "Choose a valuation to score the companies for its film." : "Save a valuation in Sales Estimates first: its genres decide each company's fit."));
        put(out,
          C.scored.length ? [el("h2", {}, `Ranked for ${R.scopes[scope].toLowerCase()}`), el("div", { class: "card flush" }, table(heads, C.scored.map(rowEl)))] : null,
          C.unscored.length ? [el("h2", { style: "margin-top:20px" }, C.project ? "Not scored yet" : "Base scores"),
            C.project ? el("p", { class: "muted small", style: "margin:0 0 10px" }, "Set each company's fit for the film's genres to score it. A company scored for another mandate isn't ranked here.") : null,
            el("div", { class: "card flush" }, table(heads, C.unscored.map(r => rowEl(r, C.project ? null : C.unscored.indexOf(r)))))] : null,
          el("p", { class: "muted small", style: "margin-top:12px" }, `Register data version ${C.dataVersion} · formula ${C.formulaVersion}. Estimate accuracy and trustworthiness stay unrated until there is an evidence-based method for them.`));
      };
      pick.addEventListener("change", () => { project = pick.value; draw(); });
      b.append(el("div", { class: "row", style: "align-items:flex-end" }, el("label", { class: "f", style: "flex:1 1 260px" }, "Film (a Sales Estimates valuation)", pick),
        el("label", { class: "f" }, "Mandate", scopeBar), el("label", { class: "f", style: "flex:0 1 200px" }, "Assessor", who)), genresBox, out);
      await draw();
    }, true], ["Register", async b => {
      const draw = async () => {
        const reg = await api.get("/api/agents");
        put(b, el("div", { class: "card flush" }, table(["ID", "Company", "Genre speciality", "#Base score", "Mandate", "Status", ""], reg.agents.map(a => el("tr", {},
          el("td", { class: "small muted" }, a.agentId), el("td", {}, el("b", {}, a.displayName), links(a), a.aliases && a.aliases.length ? el("div", { class: "small muted" }, "Also: " + a.aliases.join(", ")) : null),
          el("td", { class: "small" }, a.specialityText), el("td", { class: "num" }, a.baseScore == null ? "Unrated" : `${a.baseScore}/100`), el("td", { class: "small" }, R.scopes[a.scoreScope]),
          el("td", {}, el("span", { class: "pill PRELIMINARY" }, a.baseScoreStatus === "PROVISIONAL" ? "Provisional" : a.baseScoreStatus)),
          el("td", {}, el("button", { type: "button", class: "btn sm quiet", onclick: async () => {
            const base = el("input", { type: "number", min: 0, max: 100, step: 1, value: a.baseScore ?? "" }), spec = el("input", { type: "text", value: a.specialityText, style: "width:100%" });
            const sc = el("select", {}, Object.entries(R.scopes).map(([k, v]) => el("option", { value: k, selected: k === a.scoreScope }, v)));
            const ed = el("input", { type: "text", value: me(), placeholder: "Your name" }), why = el("input", { type: "text", placeholder: "Why the change", style: "width:100%" });
            const ok = await modal({ icon: "users", title: `Edit ${a.displayName}`, body: [el("label", { class: "f" }, "Base score (0–100, whole number; empty for unrated)", base),
              el("label", { class: "f", style: "margin-top:10px" }, "Genre speciality", spec), el("label", { class: "f", style: "margin-top:10px" }, "Mandate this score is for", sc),
              el("label", { class: "f", style: "margin-top:10px" }, "Your name", ed), el("label", { class: "f", style: "margin-top:10px" }, "Reason", why),
              el("p", { class: "muted small" }, "Kept in the history with the old value. A base-score change makes a new data version.")], actions: [["Cancel", false], ["Save", true, true]] });
            if (!ok) return;
            const v = base.value.trim() === "" ? null : Number(base.value);
            try { await api.put(`/api/agents/${a.agentId}`, { baseScore: v, specialityText: spec.value, scoreScope: sc.value, editor: ed.value, reason: why.value }); rememberMe(ed.value.trim()); toast("ok", "Saved", a.displayName); draw(); }
            catch (e) { toast("bad", "Not saved", e.message); }
          } }, "Edit")))))),
          el("p", { class: "muted small", style: "margin-top:12px" }, `Data version ${reg.dataVersion} (seeded ${reg.seedVersion}) · ${plural(reg.edits, "recorded edit")}.`));
      };
      await draw();
    }, true], ["History", async b => {
      const h = await api.get("/api/agents/history");
      put(b, h.length ? el("div", { class: "card flush" }, table(["When", "Company", "Field", "Was", "Now", "By", "Reason", "Data version"], h.map(e => el("tr", {},
        el("td", { class: "small" }, e.at), el("td", {}, e.agent_id), el("td", {}, e.field), el("td", {}, String(e.old ?? "Unrated")), el("td", {}, String(e.new ?? "Unrated")),
        el("td", {}, e.editor), el("td", { class: "small" }, e.reason), el("td", { class: "small muted" }, e.data_version))))) : el("p", { class: "muted" }, "No edits yet: the register is as Saracen Bridge seeded it on 21 October 2026."));
    }]]);
  },
  async incentives(box) {
    const country = el("input", { type: "search", placeholder: "Filter by country or region", "aria-label": "Filter programmes" });
    const prog = el("select", { "aria-label": "Programme", style: "min-width:min(320px, 100%)" });
    const spend = el("input", { type: "number", placeholder: "Qualifying spend", "aria-label": "Qualifying spend" });
    const cost = el("input", { type: "number", placeholder: "Total production cost", "aria-label": "Total production cost" });
    const all = el("input", { type: "checkbox", "aria-label": "Include limited and closed programmes" });
    const elig = el("select", { "aria-label": "Eligibility" }, ["Eligible", "Unknown", "Manual Review", "Excluded"].map(v => el("option", {}, v)));
    const routes = [], list = el("tbody", {}), out = el("div", { style: "margin-top:20px" });
    const load = async () => { const ps = await api.get(`/api/tools/incentives/programmes?country=${encodeURIComponent(country.value)}&all=${all.checked}`);
      put(prog, ps.map(p => el("option", { value: p.programme_id }, `${p.programme_id} · ${p.programme_name} (${p.programme_currency})${p.availability_status === "Active" ? "" : " · " + p.availability_status}`))); };
    country.addEventListener("input", load); all.addEventListener("change", load); await load();
    const redraw = () => put(list, routes.length ? routes.map((r, i) => el("tr", {}, el("td", {}, el("b", {}, r.programme_id)), el("td", { class: "num" }, fmt(r.qualifying_spend)), el("td", { class: "num" }, fmt(r.project_cost)), el("td", {}, r.eligibility),
      el("td", { style: "text-align:right" }, el("button", { type: "button", class: "btn quiet sm", onclick: () => { routes.splice(i, 1); redraw(); } }, "Remove"))))
      : el("tr", {}, el("td", { colspan: 5, class: "muted small" }, "No routes yet. Pick a programme, enter the spend and add it.")));
    redraw();
    box.append(el("h2", {}, "Routes to compare"), el("div", { class: "row" }, el("label", { class: "f" }, "Country", country), el("label", { class: "f" }, "Programme", prog), el("label", { class: "small muted", style: "padding-bottom:11px" }, all, " Include limited and closed")),
      el("div", { class: "row", style: "margin-top:12px" }, el("label", { class: "f" }, "Qualifying spend (programme currency)", spend), el("label", { class: "f" }, "Total production cost", cost), el("label", { class: "f" }, "Eligibility", elig),
        el("button", { type: "button", class: "btn", onclick: () => { routes.push({ programme_id: prog.value, qualifying_spend: spend.value === "" ? null : Number(spend.value), project_cost: cost.value === "" ? null : Number(cost.value), eligibility: elig.value }); redraw(); toast("info", "Route added", `${prog.value}: ${spend.value ? fmt(spend.value) : "spend unknown"}`); } }, "Add route")),
      el("div", { class: "card flush", style: "margin-top:16px" }, table(["Programme", "#Spend", "#Project cost", "Eligibility", ""], list)),
      el("button", { type: "button", class: "btn primary", style: "margin-top:16px", onclick: async () => {
        if (!routes.length) return toast("info", "Add a route first", "Pick a programme, enter the qualifying spend, then Add route.");
        try { put(out, incentivesResult(await api.post("/api/tools/incentives/calc", { routes }))); }
        catch (e) { put(out, errBox(e)); }
      } }, "Calculate"), out);
  },
  async bfi(box) {
    const crit = await api.get("/api/tools/bfi/criteria");
    const title = el("input", { type: "text", placeholder: "Project title", "aria-label": "Project title" });
    const rows = crit.map(c => ({ c, p: el("input", { type: "number", min: 0, max: c.max_points, step: 1, "aria-label": `${c.ref} proposed` }), k: el("input", { type: "number", min: 0, max: c.max_points, step: 1, "aria-label": `${c.ref} conservative` }) }));
    const out = el("div", { style: "margin-top:20px" }), reader = el("div", { style: "margin-bottom:26px" });
    const apply = (res, name) => {                       /* the script read's points into the scorer (1.0.8) */
      title.value = title.value || name;
      rows.forEach(({ c, p, k }) => { const x = res.criteria[c.ref]; if (x) { p.value = x.proposed; k.value = x.conservative; } });
      toast("ok", "Section A and B filled in", "Add Sections C and D from the production's records, then Score.");
    };
    bfiReader(reader, apply);
    box.append(reader, el("div", { class: "row" }, el("label", { class: "f", style: "flex:1" }, "Project", title)),
      el("div", { class: "card flush", style: "margin-top:16px" }, table(["Ref", "Criterion", "#Max", "Proposed", "Conservative"], rows.map(({ c, p, k }) => el("tr", {}, el("td", { class: "mono" }, c.ref), el("td", { class: "small" }, c.criterion), el("td", { class: "num" }, c.max_points), el("td", {}, p), el("td", {}, k))))),
      el("button", { type: "button", class: "btn primary", style: "margin-top:16px", onclick: async () => {
        const pick = key => Object.fromEntries(rows.filter(r => r[key].value !== "").map(r => [r.c.ref, Number(r[key].value)]));
        try { put(out, bfiResult(await api.post("/api/tools/bfi/assess", { title: title.value, proposed: pick("p"), conservative: pick("k") }))); }
        catch (e) { put(out, errBox(e)); }
      } }, "Score"), out);
  },
  async finance(box) {
    const gross = el("input", { type: "number", "aria-label": "Gross budget" }), cur = el("input", { type: "text", value: "EUR", "aria-label": "Currency", style: "width:90px" });
    const title = el("input", { type: "text", placeholder: "Project title", "aria-label": "Project title" });
    const statuses = ["Confirmed cash", "Signed but conditional", "Draft / conditional", "LOI / non-binding", "User instruction / to document", "Assumption only", "Missing"];
    const body = el("tbody", {}), out = el("div", { style: "margin-top:20px" });
    const addRow = (s = {}) => {
      const st = el("select", { "aria-label": "Status" }, statuses.map(v => el("option", { selected: v === s.status }, v)));
      const tr = el("tr", {}, el("td", {}, el("input", { type: "text", value: s.name || "", "aria-label": "Source" })), el("td", {}, el("input", { type: "number", value: s.amount ?? "", "aria-label": "Amount" })), el("td", {}, st),
        el("td", {}, el("input", { type: "checkbox", checked: s.cash !== false, "aria-label": "Cash" })), el("td", {}, el("input", { type: "text", value: s.parent || "", placeholder: "package id", "aria-label": "Inside package" })),
        el("td", {}, el("button", { type: "button", class: "btn quiet sm", "aria-label": "Remove source", onclick: () => tr.remove() }, icon("x"))));
      tr.querySelectorAll("input[type=text]").forEach(i => { i.title = i.value; i.addEventListener("input", () => { i.title = i.value; }); });   // full name on hover when the cell cuts it
      tr.dataset.id = s.id || ""; if (s.is_debt) tr.dataset.debt = "1"; body.append(tr);
    };
    /* 1.0.8: read a term sheet; every instrument is reviewed before it goes into the sources */
    const tsBox = el("div", {}), tsFile = el("input", { type: "file", accept: ".pdf,.docx,.txt", style: "display:none" });
    const tsRow = r => {
      const t = r.terms, add = el("button", { type: "button", class: "btn sm", onclick: () => {
        addRow(r); add.disabled = true; add.textContent = "Added";
        if (r.currency && cur.value && r.currency !== cur.value.toUpperCase()) toast("info", `Added in ${r.currency}`, `The plan is in ${cur.value}: convert at a dated rate.`);
      } }, "Add to sources");
      return el("tr", {}, el("td", {}, el("b", {}, r.name), el("div", { class: "small muted" }, t.status_words || ""), t.status_note ? el("div", { class: "small warn-text" }, t.status_note) : null),
        el("td", { class: "num" }, r.amount === null ? "Unknown" : fmt(r.amount), el("div", { class: "small muted" }, r.currency), r.amount !== null && !r.amount_in_document ? el("div", { class: "small warn-text" }, "not found in the document") : null),
        el("td", {}, el("span", { class: "pill " + (r.status === "Confirmed cash" ? "PASS" : "PRELIMINARY") }, r.status), r.is_debt ? el("div", { class: "small muted" }, "debt") : null),
        el("td", { class: "small" }, [["Interest", t.interest], ["Fees", t.fees], ["Term", t.term], ["Security", t.security], ["Recoupment", t.recoupment]].filter(([, v]) => v && !/^not stated$/i.test(v)).map(([k, v]) => el("div", {}, el("b", {}, k + ": "), v)),
          (t.conditions || []).length ? el("div", { class: "muted" }, "Conditions: " + t.conditions.join("; ")) : null),
        el("td", {}, add));
    };
    tsFile.addEventListener("change", async () => {
      const f = tsFile.files[0]; if (!f) return;
      const fd = new FormData(); fd.append("file", f, f.name); if (MODE) fd.append("mode", MODE);
      put(tsBox, el("div", { class: "card", style: "margin-top:16px" }, el("div", { class: "small" }, `Reading ${f.name} on ${runsOn()}…`), el("div", { class: "clapper", style: "margin-top:10px" })));
      try {
        const r = await api.form("/api/tools/finance/termsheet", fd);
        put(tsBox, el("div", { class: "card flush", style: "margin-top:16px" }, el("h2", { style: "padding:20px 20px 0" }, icon("doc"), `Term sheet: ${r.file}`),
          el("p", { class: "muted small", style: "padding:0 20px" }, [r.parties, r.governing_law ? `Governing law: ${r.governing_law}` : ""].filter(Boolean).join(" · "), " Saved in the Library."),
          r.checks.map(c => el("p", { class: "note PRELIMINARY", style: "margin:8px 20px" }, c)),
          r.rows.length ? table(["Instrument", "#Amount", "Status", "Terms", ""], r.rows.map(tsRow)) : null,
          r.rows.length > 1 ? el("div", { class: "row", style: "padding:14px 20px" }, el("button", { type: "button", class: "btn", onclick: ev => { tsBox.querySelectorAll("td button.btn.sm:not([disabled])").forEach(b => b.click()); ev.currentTarget.disabled = true; } }, "Add all to sources")) : null));
      } catch (e) { put(tsBox, errBox(e)); }
      tsFile.value = "";
    });
    const load = async () => { const ex = await api.get("/api/tools/finance/example"); gross.value = ex.gross_budget; cur.value = ex.currency; title.value = ex.title; put(body); ex.sources.forEach(addRow); toast("info", "SHADE example loaded", "The Saracen Bridge sample plan. Change any figure and Calculate."); };
    addRow();
    box.append(el("div", { class: "row" }, el("label", { class: "f", style: "flex:1" }, "Project", title), el("label", { class: "f" }, "Gross budget", gross), el("label", { class: "f" }, "Currency", cur),
      el("button", { type: "button", class: "btn", onclick: load }, "Load SHADE example"),
      el("button", { type: "button", class: "btn", title: "PDF, Word or text. Gemma lists each instrument and its terms; you choose what goes into the plan.", onclick: () => tsFile.click() }, icon("sparkle"), "Read a term sheet"), tsFile),
      tsBox,
      el("h2", { style: "margin-top:24px" }, "Sources ", el("span", { class: "muted small", style: "font-weight:400" }, "leave debt out; the tool sizes it")),
      el("div", { class: "card flush" }, table(["Source", "Amount", "Status", "Cash", "Inside package", ""], body)),
      el("div", { class: "row", style: "margin-top:14px" }, el("button", { type: "button", class: "btn", onclick: () => addRow() }, "Add source"),
        el("button", { type: "button", class: "btn primary", onclick: async () => {
          const sources = [...body.children].map((tr, i) => { const q = tr.querySelectorAll("input,select"); return { id: tr.dataset.id || `s${i}`, name: q[0].value, amount: q[1].value === "" ? null : Number(q[1].value), status: q[2].value, cash: q[3].checked, parent: q[4].value || null, is_debt: tr.dataset.debt === "1" }; });
          try {
            if (!(Number(gross.value) > 0)) return toast("info", "Enter the gross budget first", "The plan sizes the debt against it.");
            put(out, financeResult(await api.post("/api/tools/finance/plan", { title: title.value, currency: cur.value, gross_budget: Number(gross.value), sources })));
          } catch (e) { put(out, errBox(e)); }
        } }, "Calculate")), out);
  },
  greenlight(box) {
    const n = (label, v) => [label, el("input", { type: "number", min: 0, max: 100, value: v, "aria-label": label })];
    const scores = [n("Overall %", 0), n("Finance %", 0), n("Legal %", 0), n("Bond & insurance %", 0), n("Production & delivery %", 0)];
    const blockers = el("input", { type: "number", min: 0, value: 0, "aria-label": "Critical blockers" });
    const gap = el("input", { type: "checkbox", "aria-label": "Funding gap" }), signed = el("input", { type: "checkbox", "aria-label": "Sign-offs approved" }), cures = el("input", { type: "checkbox", "aria-label": "Cures owned and timed" });
    const out = el("div", { style: "margin-top:20px" });
    box.append(el("div", { class: "row" }, scores.map(([l, i]) => el("label", { class: "f" }, l, i)), el("label", { class: "f" }, "Critical blockers", blockers)),
      el("div", { class: "row", style: "margin-top:16px;gap:22px;color:var(--fg-2)" }, el("label", {}, gap, " Funding gap remains"), el("label", {}, signed, " All professional sign-offs approved"), el("label", {}, cures, " Every outstanding condition has an owned, dated cure")),
      el("button", { type: "button", class: "btn primary", style: "margin-top:18px", onclick: async () => {
        const v = scores.map(([, i]) => Number(i.value));
        try { put(out, greenlightResult(await api.post("/api/tools/greenlight/decide", { overall: v[0], finance: v[1], legal: v[2], bond_insurance: v[3], production_delivery: v[4], critical_blockers: Number(blockers.value), funding_gap: gap.checked, signoffs_approved: signed.checked, cures_owned_and_timed: cures.checked }))); }
        catch (e) { put(out, errBox(e)); }
      } }, "Decide"), out);
  },
  agreement(box) {
    const file = el("input", { type: "file", accept: ".xlsx", "aria-label": "Completed input workbook", style: "display:none" });
    const fname = el("span", { class: "name" }, "No workbook chosen");
    file.addEventListener("change", () => { const f = file.files[0]; fname.textContent = f ? f.name : "No workbook chosen"; fname.classList.toggle("set", !!f); });
    const pick = el("div", { class: "filepick" }, el("button", { type: "button", class: "btn", onclick: () => file.click() }, icon("upload"), "Choose workbook"), fname, file);
    const name = el("input", { type: "text", value: "Term_Sheet_DRAFT_01", "aria-label": "Draft name" });
    const prop = el("input", { type: "checkbox", "aria-label": "Include proposed terms" });
    const out = el("div", { style: "margin-top:20px" });
    box.append(el("ol", { class: "muted", style: "margin:0 0 18px;padding-left:18px;line-height:1.8" }, el("li", {}, "Download the input workbook and fill in the project's terms, with sources."), el("li", {}, "Upload it here. The fixed master is never edited; only its named fields are filled.")),
      el("a", { class: "btn", href: "/api/tools/agreement/blank" }, icon("file"), "Download input workbook"),
      el("div", { class: "row", style: "margin-top:20px;align-items:flex-end" }, el("label", { class: "f" }, "Completed workbook", pick), el("label", { class: "f" }, "Draft name", name), el("label", { class: "small muted", style: "padding-bottom:11px" }, prop, " Include proposed terms (discussion draft)")),
      el("button", { type: "button", class: "btn primary", style: "margin-top:16px", onclick: async () => {
        if (!file.files.length) return toast("info", "Choose the completed workbook first");
        const fd = new FormData(); fd.append("file", file.files[0]); fd.append("draft_name", name.value); fd.append("include_proposed", prop.checked ? "true" : "false");
        try {
          const r = await api.form("/api/tools/agreement/build", fd);
          if (r.ok && r.population && r.population.fields && !r.population.populated) toast("info", "Nothing was filled in", "The workbook is still blank. Fill in the project's terms, then build again.");
          else if (r.ok) toast("ok", "Term sheet built", r.technical_validation_passed ? "Technical validation passed. Review before signature." : "Built with warnings. Review before signature.");
          put(out, agreementResult(r, true));
        } catch (e) { put(out, errBox(e)); }
      } }, "Build term sheet"), out);
  },
  aiden(box, t) { external(box, t, "aiden"); },
  frat(box, t) { external(box, t, "frat"); },
};
function external(box, t, id) {
  if (t.coming_soon) return box.append(el("div", { class: "drop", style: "border-style:solid" }, el("div", { class: "art" }, toolIcon(t)),
    el("div", { class: "big" }, "Coming soon"),
    el("p", {}, t.coming_soon_text || `${t.name} is being built into Saracen Bridge Studio.`)));
  box.append(el("div", { class: "drop", style: "border-style:solid" }, el("div", { class: "art" }, toolIcon(t)), el("div", { class: "big" }, t.tagline),
    el("p", {}, `${t.name} runs as its own program. Saracen Bridge Studio opens it for you.`),
    el("div", { class: "row" }, el("button", { type: "button", class: "btn primary", onclick: async () => {
      try { const r = await api.post(`/api/external/${id}/launch`, {}); toast("ok", `Opening ${t.name}`, r.launched); }
      catch (e) { const go = await modal({ icon: "external", title: `${t.name} isn't linked yet`, body: [`Tell the Studio where ${t.name} lives on this computer: its web address or program path.`], actions: [["Not now", false], ["Open Settings", true, true]] }); if (go) location.hash = "#/settings"; }
    } }, icon("external"), `Open ${t.name}`))));
}

/* ---------------- coverage queue ---------------- */
let MODE = null;                              // reasoning for new jobs: "quick" (thinking off) or "deep" (thinking on)
function modeSwitch() {
  const wrap = el("div", { class: "tabs", role: "group", "aria-label": "Reasoning", style: "margin:0" });
  const draw = () => put(wrap, el("span", { class: "lbl" }, "Reasoning"),
    [["quick", "Quick", "Thinking off: fastest"], ["deep", "Deep", "Thinking on: slower, more considered"]].map(([v, l, tip]) =>
      el("button", { type: "button", title: tip, "aria-pressed": String(MODE === v), onclick: () => { MODE = v; draw(); engineChip(); } }, l)));
  draw();
  return wrap;
}
async function writeMissing() {
  try { const q = await api.post("/api/tools/coverage/write", { missing: true, mode: MODE }); toast(q.queued ? "ai" : "info", q.queued ? `${plural(q.queued, "script")} queued for coverage` : "Every script already has coverage", q.queued ? `On ${runsOn()}, ${q.mode} reasoning.` : null); pollJobs(); }
  catch (e) { toast("bad", "Couldn't start coverage", el("span", {}, e.message, " ", el("a", { href: "#/settings" }, "Settings"))); }
}
async function testEngine() {
  const close = toast("ai", "Asking the AI engine a question…", "The first answer loads the model, so it takes longest.", 120000);
  try { const r = await api.post("/api/ai/test", { mode: MODE }); close(); toast("ok", `Answered in ${r.seconds} s`, `${r.engine}: “${r.reply}”`, 8000); return r; }
  catch (e) { close(); toast("bad", "The engine didn't answer", e.message); }
}
/* A failed job says what happened in plain words; the engine's own message stays one click away (Tim, 13 Oct:
   the queue showed "EngineError: 500 from http://127.0.0.1:61185/v1/chat/completions: {"error":..."). */
/* a job's options arrive as the JSON text stored with it (Tim, 13 Oct: a Deep job was labelled "quick reasoning") */
const jobOpts = j => { try { return typeof j.options === "string" ? JSON.parse(j.options || "{}") : (j.options || {}); } catch (e) { return {}; } };
function plainError(raw) {
  const t = String(raw || "");
  const say = [
    [/context size|exceeds the available context|context length/i, "The AI engine ran out of working memory part-way through (another request was running at the same time). Press Retry."],
    [/no text before reaching its length limit/i, "Gemma spent its whole allowance thinking and wrote nothing. Press Retry, or set Reasoning to Quick."],
    [/not valid JSON|returned no text/i, "Gemma's answer came back incomplete. Press Retry; a second attempt usually works."],
    [/stopped part-way|stopped while loading|exit code/i, "The AI engine stopped, usually because the computer ran out of memory. Close other programs and press Retry."],
    [/not reachable|RemoteDisconnected|Connection (refused|reset)|timed out/i, "The AI engine didn't respond. Press Retry; if it happens again, restart the Studio."],
    [/^Cancelled|InterruptedError/i, "Cancelled."],
  ].find(([re]) => re.test(t));
  return { text: say ? say[1] : t.replace(/^[A-Za-z]+Error:\s*/, "").replace(/\s*https?:\/\/\S+/g, "").slice(0, 200), detail: say ? t : "" };
}
function errorLine(raw) {
  const e = plainError(raw);
  if (!e.detail) return el("span", { class: "meta" }, e.text);
  const more = el("span", { class: "err-detail", hidden: true }, e.detail);
  return el("span", { class: "meta" }, e.text, " ", el("button", { type: "button", class: "linkish", onclick: ev => {
    ev.preventDefault(); ev.stopPropagation(); more.hidden = !more.hidden; ev.currentTarget.textContent = more.hidden ? "Details" : "Hide details";
  } }, "Details"), more);
}
function queuePanel(kind) {
  const LB = kind === "lookbook";
  const word = LB ? { title: "Look book queue", doing: "Reading", stop: "Stop this analysis?", stopped: "Analysis stopped" }
                  : { title: "Coverage queue", doing: "Writing", stop: "Stop this coverage?", stopped: "Coverage stopped" };
  const box = el("div", { class: "card", style: "margin-bottom:22px;background:var(--ink-1)" });
  const sw = modeSwitch();
  let timer = null;
  const say = node => toast("info", node.textContent || "Done");
  const draw = async () => {
    let r;
    try { r = await api.get(`/api/jobs?kind=${kind}&limit=60`); } catch (e) { return; }
    const c = r.counts, active = (c.queued || 0) + (c.running || 0);
    const running = r.jobs.find(j => j.status === "running");
    const finished = r.jobs.filter(j => ["done", "error", "cancelled"].includes(j.status)).slice(0, 6);
    if (JOBS_ACTIVE !== active) { JOBS_ACTIVE = active; pollJobs(); }
    put(box, el("h2", {}, icon("reel"), word.title, active ? el("span", { class: "pill AI" }, `${active} in progress`) : null),
      el("div", { class: "kpis" }, [["Waiting", c.queued], [word.doing, c.running], ["Done", c.done], ["Failed", c.error]]
        .map(([l, v]) => el("div", { class: "kpi" + (l === word.doing && v ? " edge" : "") }, el("div", { class: "l" }, l), el("div", { class: "v" }, fmt(v || 0))))),
      running ? el("div", { style: "margin-top:16px" }, el("div", { class: "row", style: "align-items:center;justify-content:space-between;margin-bottom:10px" },
          el("div", {}, el("b", {}, running.title), el("span", { class: "muted small" }, ` · ${jobOpts(running).mode || "quick"} reasoning · ${running.progress || "starting"}`)),
          el("button", { type: "button", class: "btn sm", onclick: async () => {
            const ok = await modal({ icon: "alert", title: word.stop, body: [`“${running.title}” stops now. What's done so far is discarded; you can queue it again later.`], actions: [["Keep going", false], ["Stop", true, true]] });
            if (ok) { await api.post(`/api/jobs/${running.id}/cancel`, {}); toast("info", word.stopped, running.title); draw(); }
          } }, "Cancel")), el("div", { class: "clapper" })) : null,
      el("div", { class: "row", style: "margin-top:18px;align-items:center" },
        sw,
        LB ? null : el("button", { type: "button", class: "btn", onclick: async () => { await writeMissing(); draw(); } }, icon("sparkle"), "Write coverage for every script without it"),
        c.error ? el("button", { type: "button", class: "btn quiet", onclick: async () => { await api.post("/api/jobs/retry", { kind }); toast("info", `Retrying ${c.error} failed`); draw(); } }, `Retry ${c.error} failed`) : null,
        c.error ? el("button", { type: "button", class: "btn quiet", title: "Takes them off this list. The scripts stay in the Library and can be queued again.", onclick: async () => {
          const r = await api.post("/api/jobs/clear", { kind }); toast("ok", `Cleared ${plural(r.cleared, "failed job")}`, "The scripts stay in the Library."); draw(); } }, icon("x"), `Clear ${c.error} failed`) : null),
      finished.length ? el("div", { class: "list", style: "margin-top:16px;border-top:1px solid var(--line)" }, finished.map(j => el("a", { href: `#/run/${j.tool}/${j.run_id}`, style: "padding:12px 4px" },
        el("span", {}, el("span", { class: "ttl" }, j.title), " ", el("span", { class: "pill st " + ({ done: "PASS", error: "FAIL", cancelled: "PRELIMINARY" })[j.status], style: "margin-left:8px" }, j.status),
          j.error ? errorLine(j.error) : null),
        el("span", { class: "row-end" }, el("span", { class: "when" }, (j.finished || "").slice(5, 16)),
          j.status !== "done" ? el("button", { type: "button", class: "row-x", title: "Clear from this list", "aria-label": `Clear ${j.title} from this list`, onclick: async e => {
            e.preventDefault(); e.stopPropagation(); await api.post("/api/jobs/clear", { kind, id: j.id }); draw(); } }, icon("x")) : null)))) : null);
    clearTimeout(timer);
    if (active) timer = setTimeout(() => document.body.contains(box) && draw(), 3000);
  };
  setTimeout(draw, 0);
  return { box, draw, say };
}

function pageStrip(runId, n, notes) {
  return el("div", { class: "pages" }, Array.from({ length: n }, (_, i) => {
    const src = `/api/runs/lookbook/${runId}/files/pages/p${String(i + 1).padStart(2, "0")}.jpg?inline=1`, note = notes && notes[i];
    return el("a", { class: "pg", href: src, target: "_self", title: note ? note.shows : `Page ${i + 1}`, onclick: e => { e.preventDefault(); pageModal(src, i + 1, note); } },
      el("img", { src, alt: `Page ${i + 1}`, loading: "lazy" }), el("span", { class: "n" }, i + 1), note ? el("span", { class: "vs" }, `${note.visual_score}/10`) : null);
  }));
}
function pageModal(src, n, note) {
  modal({ icon: "lookbook", title: `Page ${n}`, body: [el("img", { src, alt: `Page ${n}`, style: "width:100%;border-radius:10px;margin:6px 0 10px" }),
    ...(note ? [el("p", {}, el("b", {}, "Shows: "), note.shows), el("p", {}, el("b", {}, "Sells: "), note.sells),
      note.issues.length ? el("p", {}, el("b", {}, "Issues: "), note.issues.join("; ")) : null, el("p", { class: "muted small" }, `Visual quality ${note.visual_score} / 10`)] : [])],
    actions: [["Close", true, true]] });
}
function lookbookRun(r) {
  const lb = r.outputs.lookbook, n = (r.outputs.deck || { pages: [] }).pages.length;
  if (!lb) return el("div", {},
    el("div", { class: "notice", style: "margin-top:24px" }, el("div", { class: "ic" }, icon("sparkle")),
      el("div", { class: "grow" }, el("div", {}, "Not analysed yet"), el("div", { class: "sub" }, AI.vision ? "Gemma looks at every page, then writes the Saracen Bridge 16-section analysis." : (AI.vision_reason || "Needs an AI engine that reads images."))),
      modeSwitch(), el("button", { type: "button", class: "btn primary", onclick: async ev => {
        const b = ev.currentTarget; b.disabled = true;
        try { const q = await api.post("/api/tools/lookbook/analyse", { run_ids: [r.id], mode: MODE }); toast("ai", "Look book queued", el("span", {}, `On ${runsOn()}. `, el("a", { href: "#/tool/lookbook" }, "Watch the queue"))); pollJobs(); }
        catch (e) { toast("bad", "Couldn't start the analysis", e.message); b.disabled = false; }
      } }, icon("sparkle"), "Analyse")),
    el("div", { class: "section-title" }, "The deck", el("small", {}, plural(n, "page"))), pageStrip(r.id, n));
  return el("div", {}, lookbookView(lb), el("div", { class: "section-title" }, "Page by page", el("small", {}, `${plural(n, "page")} · click a page for its notes`)), pageStrip(r.id, n, lb.page_notes));
}
function lookbookView(lb) {
  const s = lb.sections, sn = s.snapshot, st = s.story, vi = s.visual, mk = s.market, rb = s.rebuild;
  let no = 0;
  const H = t => el("h2", { class: "sec" }, el("span", { class: "no" }, String(++no).padStart(2, "0")), t), P = t => t ? el("p", {}, t) : null;
  const UL = a => (a || []).length ? el("ul", { class: "plain need", style: "margin:6px 0 4px" }, a.map(x => el("li", {}, icon("arrow"), el("span", { style: "color:var(--fg)" }, x)))) : null;
  const KV = rows => el("div", { class: "card flush", style: "margin-top:10px;background:var(--ink-1)" }, table(["", ""], rows.filter(([, v]) => v).map(([k, v]) => el("tr", {}, el("td", { class: "muted", style: "width:32%" }, k), el("td", {}, v)))));
  const B = t => el("div", { class: "lbl" }, t);
  return el("div", { class: "card report" },
    el("div", { class: "kpis" },
      el("div", { class: "kpi edge" }, el("div", { class: "l" }, "Look book sales score"), el("div", { class: "v" }, `${lb.final_score}`, el("small", { style: "font-size:18px;color:var(--fg-3)" }, " / 100"))),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Verdict (proposed)"), el("div", { class: "v", style: "font-size:24px" }, lb.verdict)),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Sales tool usefulness"), el("div", { class: "v" }, `${mk.sales_tool_usefulness_score}`)),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Average of 13 scores"), el("div", { class: "v" }, lb.average.toFixed(1)))),
    lb.checks.map(c => el("p", { class: "note PRELIMINARY" }, c)),
    H("Executive Snapshot"), P(sn.immediate_impression),
    KV([["Format", sn.format], ["Genre", sn.genre], ["Tone", sn.tone], ["Core proposition", sn.core_proposition], ["Primary audience", sn.primary_audience], ["Market lane", sn.market_lane], ["Main strength", sn.main_strength], ["Main weakness", sn.main_weakness]]),
    H("One-Sentence Sales Proposition"), KV([["As presented", sn.current_proposition || "Not stated"], ["Improved", sn.improved_proposition], ["Commercial hook", sn.commercial_hook]]),
    H("Logline Review and Rewrite"), KV([["As presented", sn.current_logline || "No logline in the deck"]]), P(sn.logline_review), el("p", { class: "logline" }, sn.revised_logline),
    H("Story Sell"), P(st.story_sell), st.clear.length ? [B("Clear"), UL(st.clear)] : null, st.unclear.length ? [B("Unclear or underdeveloped"), UL(st.unclear)] : null, st.move_earlier.length ? [B("Should appear earlier"), UL(st.move_earlier)] : null,
    H("Character Sell"), el("div", { class: "card flush", style: "margin-top:10px;background:var(--ink-1)" }, table(["Character", "Function and hook", "Actor type", "Status", "Names"],
      st.characters.map(c => el("tr", {}, el("td", {}, el("b", {}, c.character)), el("td", {}, `${c.function} ${c.emotional_hook}`), el("td", { class: "small" }, c.actor_type),
        el("td", {}, el("span", { class: "pill " + (c.status === "Attached" ? "PASS" : "") }, c.status)), el("td", { class: "small" }, c.names.join(", ") || "None"))))),
    H("Director Positioning"), st.director_named ? KV([["Director", st.director_named]]) : null, P(st.director_assessment),
    st.director_suggestions.length ? [B("Suggested directors (not attached)"), UL(st.director_suggestions.map(d => `${d.name}: ${d.why}`))] : null,
    H("Visual Tone Analysis"), P(vi.visual_tone), KV([["Does it visually sell the project?", vi.sells_visually], ["Does the tone match the story?", vi.tone_matches_story], ["Cinematic or generic?", vi.cinematic_or_generic], ["Does it show the finished film?", vi.shows_finished_film], ["Castable and directable?", vi.castable_and_directable]]),
    H("Design and Presentation"), P(vi.design_presentation),
    vi.strongest_pages.length ? [B("Strongest pages"), UL(vi.strongest_pages.map(p => `Page ${p.page}: ${p.why}`))] : null,
    vi.weakest_pages.length ? [B("Weakest pages"), UL(vi.weakest_pages.map(p => `Page ${p.page}: ${p.why}`))] : null, B("Cut, simplify or redesign"), UL(vi.cut_simplify_redesign),
    H("Genre and Audience Positioning"), KV([["Primary genre", mk.primary_genre], ["Secondary genre", mk.secondary_genre], ["Audience", mk.audience], ["Likely buyers", mk.buyers], ["Theatrical", mk.theatrical_potential], ["Streamer / broadcaster", mk.streamer_broadcaster_potential], ["International", mk.international_appeal], ["Is positioning clear?", mk.positioning_verdict]]),
    H("Film / TV Comparables"), P(mk.comparables_assessment), UL(mk.better_comparables.map(c => `${c.title} (${c.year}): ${c.why}`)),
    H("Budget Signals and Production Scale"), KV([["Budget", mk.budget_summary], ["Budget feel", mk.budget_feel]]), UL(mk.scale_signals),
    H("Sales Agent / Distributor Usefulness"), P(mk.sales_usefulness),
    H("Recommended Look Book Structure"), el("div", { class: "card flush", style: "margin-top:10px;background:var(--ink-1)" }, table(["#", "Slide", "Purpose", "Content", "Visual direction"],
      rb.slides.map(x => el("tr", {}, el("td", { class: "num" }, x.slide), el("td", {}, el("b", {}, x.title)), el("td", { class: "small" }, x.purpose), el("td", { class: "small" }, x.content), el("td", { class: "small muted" }, x.visual_direction))))),
    H("Priority Improvements"), B("Must fix"), UL(rb.must_fix), B("Should improve"), UL(rb.should_improve), rb.optional_enhancement.length ? [B("Optional enhancement"), UL(rb.optional_enhancement)] : null,
    H("Scored Assessment"), el("div", { class: "bars" }, Object.entries(lb.scores).map(([k, v]) => el("div", { class: "bar" }, el("span", { class: "k" }, k), el("span", { class: "t" }, el("i", { style: `width:${v}%` })), el("span", { class: "v" }, v)))),
    H("Final Verdict"), el("div", { class: "kpi edge", style: "margin-top:10px" }, el("div", { class: "l" }, "Final verdict (proposed)"), el("div", { class: "v", style: "font-size:26px" }, lb.verdict_text)), P(s.scores.verdict_reason),
    el("div", { class: "colophon" }, `Written ${lb.date} by ${lb.made_with.model} (${lb.made_with.engine}), ${lb.made_with.mode || "quick"} reasoning, ${plural(lb.made_with.pages_read, "page")} looked at in ${Math.round(lb.made_with.seconds)} s. The verdict and scores are proposals: the Saracen Bridge rule for mapping scores to verdicts is open (G-01).`));
}
function coverageView(cov) {
  const s = cov.sections, st = s.story, cr = s.creative, mk = s.market, dv = s.develop, vd = s.verdict;
  let no = 0;
  const H = t => el("h2", { class: "sec" }, el("span", { class: "no" }, String(++no).padStart(2, "0")), t), P = t => el("p", {}, t);
  const B = t => el("div", { class: "lbl" }, t);
  const UL = a => el("ul", { class: "plain need", style: "margin:6px 0 4px" }, (a || []).map(x => el("li", {}, icon("arrow"), el("span", { style: "color:var(--fg)" }, x))));
  const KV = rows => el("div", { class: "card flush", style: "margin-top:10px;background:var(--ink-1)" }, table(["", ""], rows.map(([k, v]) => el("tr", {}, el("td", { class: "muted", style: "width:32%" }, k), el("td", {}, v)))));
  return el("div", { class: "card report" },
    el("div", { class: "kpis" },
      el("div", { class: "kpi edge" }, el("div", { class: "l" }, "Verdict (proposed)"), el("div", { class: "v" }, cov.verdict)),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Composite"), el("div", { class: "v" }, cov.composite.toFixed(2), el("span", { style: "font-size:18px;color:var(--fg-3)" }, " / 10"))),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Commercial readiness"), el("div", { class: "v" }, cov.commercial_readiness, el("span", { style: "font-size:18px;color:var(--fg-3)" }, " / 100"))),
      el("div", { class: "kpi" }, el("div", { class: "l" }, "Budget band"), el("div", { class: "v", style: "font-size:24px" }, dv.budget_band))),
    cov.checks.map(c => el("p", { class: "note PRELIMINARY" }, c)),
    H("Executive summary"), P(st.concept_sentence), P(vd.overall_assessment), B("Commercial potential"), P(vd.commercial_potential),
    B("Major strengths"), UL(vd.major_strengths), B("Primary issues"), UL(vd.primary_issues),
    H("Logline and five-sentence pitch"), el("p", { class: "logline" }, st.logline), P(st.pitch.join(" ")),
    H("Synopsis"), st.synopsis.map(P),
    H("Creative analysis"),
    [["A. Concept and premise", cr.concept_and_premise], ["B. Story and structure", cr.story_and_structure], ["C. Characters", cr.characters]].map(([t, x]) => [B(t), P(x)]),
    cr.casting && cr.casting.length ? el("div", { class: "card flush", style: "margin-top:10px;background:var(--ink-1)" }, table(["Role", "Casting suggestions"], cr.casting.map(c => el("tr", {}, el("td", {}, el("b", {}, c.role)), el("td", {}, c.names.join(", ")))))) : null,
    [["D. Dialogue", cr.dialogue], ["E. Themes and tone", cr.themes_and_tone], ["F. Worldbuilding", cr.worldbuilding], ["G. Production feasibility", cr.production_feasibility]].map(([t, x]) => [B(t), P(x)]),
    H("Market positioning"), KV([["Target demographic", mk.target_demographic], ["Audience profile", mk.audience_profile], ["Release pathway", mk.release_pathway],
      ["Sales agent tier", mk.sales_agent_tier], ["Distributor / platform", mk.distributor_suitability], ["Awards / festival", mk.awards_festival_potential], ["Current market fit", mk.current_market_fit]]),
    B("Comparables"), UL((mk.comparables || []).map(c => typeof c === "string" ? c : `${c.title} (${c.year}): ${c.relevance}`)),
    H("Risk assessment"), UL(mk.risks),
    H("Development notes"), B("Top 3 rewrite priorities"), UL(dv.rewrite_priorities), B("Notes"), UL(dv.development_notes),
    [["Character", dv.character_notes], ["Dialogue", dv.dialogue_notes], ["Structure and pacing", dv.structure_notes], ["Commercial sharpening", dv.commercial_notes]].map(([t, x]) => [B(t), P(x)]),
    H("Strengths and weaknesses"), B("Strengths"), UL(dv.strengths), B("Weaknesses"), UL(dv.weaknesses),
    H("Budget band guidance"), KV([["Estimated band", dv.budget_band], ["If too low", dv.risk_if_budget_too_low], ["If too high", dv.risk_if_budget_too_high], ["To justify more", dv.to_justify_higher_budget]]),
    B("Pressure points"), UL(dv.budget_pressure_points), B("Cost control"), UL(dv.cost_control_opportunities), el("p", { class: "muted small" }, "Indicative only, subject to full budget, schedule and production review."),
    H("Weighted scoring matrix"),
    el("div", { class: "card flush", style: "background:var(--ink-1)" }, table(["Category", "#Score", "#Weight", "#Weighted", "Why"], Object.entries(cov.weights).map(([k, w]) => el("tr", {}, el("td", {}, el("b", {}, k)), el("td", { class: "num" }, cov.scores[k]),
      el("td", { class: "num" }, Math.round(w * 100) + "%"), el("td", { class: "num" }, (cov.scores[k] * w).toFixed(2)), el("td", { class: "small" }, (vd.score_reasons || {})[k] || ""))))),
    H("Final recommendation"), el("div", { class: "kpi edge", style: "max-width:360px;margin:6px 0 14px" }, el("div", { class: "l" }, "Verdict"), el("div", { class: "v" }, vd.verdict)), P(vd.reason_for_verdict),
    KV([["Development priority", vd.development_priority], ["Best next step", vd.best_next_step]]),
    el("div", { class: "colophon" }, `Written ${cov.date} by ${cov.made_with.model} (${cov.made_with.engine}, ${cov.made_with.mode || "quick"} reasoning), ${plural(cov.made_with.parts_read, "part")} read, ${Math.round(cov.made_with.seconds)} s. The verdict and readiness score are the model's proposals: the Saracen Bridge rules for both are open questions (G-01, G-02).`));
}

/* ---------------- runs ---------------- */
async function runView(toolId, id) {
  const r = await api.get(`/api/runs/${toolId}/${id}`);
  const t = toolById(r.tool) || { name: r.tool, group: "Library" };
  topbar(["Library", t.name, r.title]);
  const fileIcon = f => /\.docx$/i.test(f) ? "doc" : "file";
  const head = [el("h1", {}, r.title), el("div", { class: "run-meta" }, "Saved " + savedAt(r.created)),
    r.files.length ? el("div", { class: "files" }, r.files.map(f => el("a", { class: "file", href: `/api/runs/${toolId}/${id}/files/${encodeURIComponent(f)}` }, el("span", { class: "ic" }, icon(fileIcon(f))), f))) : null];
  if (r.tool === "lookbook") return put(app(), ...head, lookbookRun(r));
  const b = r.outputs.breakdown;
  if (!b) {
    const view = RESULT_VIEWS[r.tool];
    if (!view) return put(app(), ...head, el("p", { class: "muted" }, "This record has no viewer in this version of the Studio. Its files are above."));
    let body; try { body = view(r); } catch (e) { body = el("p", { class: "muted" }, "This record was saved by an older version and can't be shown in full. Its files are above."); }
    return put(app(), ...head, el("div", { style: "margin-top:22px" }, body), inputsView(r),
      el("p", { style: "margin-top:20px" }, el("a", { class: "btn quiet sm", href: `#/tool/${r.tool}` }, "Open ", t.name, icon("arrow"))));
  }
  const covBox = el("div", {});
  const writeBtn = label => el("button", { type: "button", class: "btn primary", onclick: async ev => {
    const btn = ev.currentTarget; btn.disabled = true;
    try { await api.post("/api/tools/coverage/write", { tool: toolId, run_ids: [id], mode: MODE }); toast("ai", "Coverage queued", el("span", {}, `On ${runsOn()}. `, el("a", { href: "#/tool/coverage" }, "Watch the queue"))); pollJobs(); }
    catch (e) { toast("bad", "Couldn't queue coverage", el("span", {}, e.message, " ", el("a", { href: "#/settings" }, "Settings"))); btn.disabled = false; }
  } }, icon("sparkle"), label);
  if (r.outputs.coverage) put(covBox, (r.summary || {}).coverage_stale ? el("div", { class: "notice", style: "margin-top:24px" }, el("div", { class: "ic" }, icon("alert")),
      el("div", { class: "grow" }, el("div", {}, `The script has been read again since this coverage was written (now ${plural(b.scene_count, "scene")})`),
        el("div", { class: "sub" }, "The coverage below was written from the earlier reading. Write it again to base it on the full script.")),
      modeSwitch(), writeBtn("Write again")) : null, coverageView(r.outputs.coverage));
  else put(covBox, el("div", { class: "notice", style: "margin-top:24px" }, el("div", { class: "ic" }, icon("sparkle")),
    el("div", { class: "grow" }, el("div", {}, "No coverage yet"), el("div", { class: "sub" }, "Gemma reads the whole script and writes the Saracen Bridge 11-section report.")),
    modeSwitch(), el("button", { type: "button", class: "btn primary", onclick: async ev => {
      const btn = ev.currentTarget; btn.disabled = true;
      try { const q = await api.post("/api/tools/coverage/write", { tool: toolId, run_ids: [id], mode: MODE }); toast("ai", "Coverage queued", el("span", {}, `On ${runsOn()}. `, el("a", { href: "#/tool/coverage" }, "Watch the queue"))); pollJobs(); }
      catch (e) { toast("bad", "Couldn't queue coverage", el("span", {}, e.message, " ", el("a", { href: "#/settings" }, "Settings"))); btn.disabled = false; }
    } }, icon("sparkle"), "Write coverage")));
  const bud = r.outputs.budget, budBox = r.tool === "schedule" ? el("div", { class: "notice", style: "margin-top:24px" }, el("div", { class: "ic" }, icon("schedule")),
    el("div", { class: "grow" }, bud ? [el("div", {}, `Budget: ${money(bud.currency, bud.budget.base.known_total)} priced in the base case, ${plural(bud.schedule.base.shoot_days, "shooting day")}`),
      el("div", { class: "sub" }, bud.budget.base.unknown_lines ? `PRELIMINARY: ${plural(bud.budget.base.unknown_lines, "line")} still to price. ${bud.jurisdiction}, built ${savedAt(bud.built)}.` : `Every line priced. ${bud.jurisdiction}, built ${savedAt(bud.built)}.`)]
      : [el("div", {}, "No schedule or budget yet"), el("div", { class: "sub" }, "Shooting days, a stripboard, day-out-of-days and a budget from the Saracen Bridge rate cards.")]),
    bud ? el("a", { class: "btn sm", href: `/api/runs/schedule/${id}/budget.xlsx` }, icon("download"), ".xlsx") : null,
    el("button", { type: "button", class: "btn sm primary", onclick: () => { BUDGET_RUN = id; BUDGET_OPEN = true; location.hash = "#/tool/schedule"; } }, icon("schedule"), bud ? "Open" : "Build")) : null;
  put(app(), ...head, r.tool === "brand" ? brandTargets(r) : null, r.tool === "brand" ? await brandSpot(r) : null, budBox, covBox, el("div", { class: "section-title" }, "Breakdown", el("small", {}, `${b.format || ""}`)),
    el("div", { class: "kpis" }, [["Pages", b.pages_estimated ? `~${fmt(b.pages)}` : fmt(b.pages)], ["Scenes", b.scene_count], ["Speaking roles", b.speaking_roles], ["Locations", b.locations.length], ["INT / EXT", `${b.int} / ${b.ext}`], ["Day / Night", `${b.day} / ${b.night}`]]
      .map(([l, v]) => el("div", { class: "kpi" }, el("div", { class: "l" }, l), el("div", { class: "v" }, v)))),
    b.warnings.map(w => el("p", { class: "note PRELIMINARY" }, w)),
    el("div", { class: "cols", style: "grid-template-columns:minmax(0,340px) minmax(0,1fr)" },
      el("div", { class: "card flush" }, el("h2", { style: "padding:20px 20px 0" }, "Cast by dialogue"), table(["Character", "#Lines", "#Scenes", "#1st"], b.cast.map(c => el("tr", {}, el("td", {}, el("b", {}, c.name)), el("td", { class: "num" }, c.dialogue_blocks), el("td", { class: "num" }, c.scene_count), el("td", { class: "num" }, c.first_scene))))),
      el("div", { class: "card flush" }, el("h2", { style: "padding:20px 20px 0" }, "Scenes"), table(["#", "Location", "I/E", "Time", "Characters"], b.scenes.map(s => el("tr", {}, el("td", { class: "num" }, s.number), el("td", {}, s.location || s.heading), el("td", { class: "mono small" }, s.int_ext), el("td", { class: "mono small" }, s.time_of_day), el("td", { class: "small muted" }, s.characters.join(", "))))))));
}
async function library(only) {
  topbar(["Studio", "Library"]);
  const q = el("input", { type: "search", placeholder: "Search titles", "aria-label": "Search titles", style: "flex:1;min-width:220px" });
  const tsel = el("select", { "aria-label": "Tool" }, el("option", { value: "" }, "All tools"), CAT.tools.filter(t => !t.external).map(t => el("option", { value: t.id, selected: t.id === only }, t.name)));
  const head = el("p", { class: "lede" }), list = el("div", {}), more = el("div", { style: "margin-top:14px" });
  let offset = 0;
  const load = async (reset) => {
    if (reset) { offset = 0; put(list); }
    const r = await api.get(`/api/runs?tool=${tsel.value}&q=${encodeURIComponent(q.value)}&limit=100&offset=${offset}`);
    offset += r.runs.length;
    head.textContent = r.total ? `${fmt(r.total)} saved ${r.total === 1 ? "item" : "items"}, all stored on this computer.` : (q.value || tsel.value ? "Nothing matches." : "Nothing saved yet. Everything stays on this computer.");
    if (r.runs.length) list.append(runList(r.runs));
    else if (reset) put(list, el("div", { class: "drop", style: "border-style:solid" }, el("div", { class: "art" }, icon("library")), el("div", { class: "big" }, "Nothing here yet"), el("p", {}, "Everything you run in any tool is saved here. Open a tool from Home to start.")));
    put(more, offset < r.total ? el("button", { type: "button", class: "btn", onclick: () => load(false) }, `Show more (${fmt(r.total - offset)} left)`) : null);
  };
  let timer;
  q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(() => load(true), 180); });
  q.addEventListener("keydown", e => { if (e.key === "Enter") { clearTimeout(timer); load(true); } }); tsel.addEventListener("change", () => load(true));
  put(app(), el("h1", {}, "Everything you've ", el("em", {}, "run")), head,
    el("div", { class: "row", style: "margin:22px 0 18px" }, q, tsel), list, more);
  await load(true);
}

/* ---------------- settings ---------------- */
async function settings() {
  topbar(["Studio", "Settings"]);
  const s = await api.get("/api/settings");
  const e = s.ai_engine;
  const prov = el("select", { "aria-label": "AI engine" }, [
    ["auto", "Automatic: Gemma on this computer, else the built-in model"],
    ["ollama", "Ollama (address below)"],
    ["openai", "Local model server, OpenAI-compatible (address below)"],
    ["bundled", "Built-in model only"],
    ["none", "None (calculation tools only)"]].map(([v, l]) => el("option", { value: v, selected: e.provider === v }, l)));
  const url = el("input", { type: "text", value: e.url || "", placeholder: "http://127.0.0.1:11434  or  http://127.0.0.1:8080/v1", "aria-label": "Engine address", style: "min-width:min(320px, 100%)" });
  const model = el("input", { type: "text", value: e.model || "", placeholder: "blank = largest Gemma found", "aria-label": "Model" });
  const key = el("input", { type: "password", value: e.api_key || "", placeholder: "only if the server needs one", "aria-label": "Access key" });
  const modes = Object.assign({ quick: { model: "", think: false }, deep: { model: "", think: true } }, e.modes || {});
  const defMode = el("select", { "aria-label": "Default reasoning" }, [["quick", "Quick: thinking off"], ["deep", "Deep: thinking on"]].map(([v, l]) => el("option", { value: v, selected: (e.default_mode || "quick") === v }, l)));
  const quickModel = el("input", { type: "text", value: modes.quick.model || "", placeholder: "blank = engine's model", "aria-label": "Quick model" });
  const deepModel = el("input", { type: "text", value: modes.deep.model || "", placeholder: "blank = engine's model", "aria-label": "Deep model" });
  const keyBox = el("label", { class: "f" }, "Access key", key);
  const showFields = () => { url.parentElement.style.display = ["ollama", "openai"].includes(prov.value) ? "" : "none"; model.parentElement.style.display = ["auto", "ollama", "openai"].includes(prov.value) ? "" : "none"; keyBox.style.display = prov.value === "openai" ? "" : "none"; };
  prov.addEventListener("change", showFields);
  const apps = Object.entries(s.external_apps).map(([id, a]) => [id, el("input", { type: "text", value: a.target, placeholder: "Web address or program path", "aria-label": a.name, style: "min-width:min(380px, 100%)" }), a.name]);
  const now = el("div", { style: "margin:4px 0 20px" });
  const showStatus = a => put(now, el("div", { class: "engine-chip", style: "background:var(--ink-1)" }, el("span", { class: "dot " + (a.connected ? "ok live" : "warn") }),
    el("span", {}, el("b", {}, a.connected ? "In use: " + a.description : "Not connected"), a.connected ? (a.note || "Running on this computer.") : a.reason)));
  const save = async () => { Object.assign(s.ai_engine, { provider: prov.value, url: url.value.trim(), model: model.value.trim(), api_key: key.value,
      default_mode: defMode.value, modes: { quick: { model: quickModel.value.trim(), think: false }, deep: { model: deepModel.value.trim(), think: true } } }); MODE = defMode.value; apps.forEach(([id, i]) => s.external_apps[id].target = i.value); await api.put("/api/settings", s); AI = await api.get("/api/ai/status"); showStatus(AI); engineChip(); return AI; };
  put(app(), el("h1", {}, "Settings"), el("p", { class: "lede" }, "The AI engine, cloud AI and the apps the Studio opens. These settings, and any cloud key, are kept on this computer."),
    el("div", { class: "cols" },
      el("div", { class: "stack" }, el("div", { class: "card ai-card" }, el("h2", {}, icon("sparkle"), "AI engine"),
        el("p", { class: "muted small", style: "margin-top:-4px" }, "Calculation tools never need this. Writing tools do. Every engine in this card runs on this computer or your own network, so scripts never leave the building."),
        now,
        el("div", { class: "row" }, el("label", { class: "f", style: "flex:1 1 320px" }, "Engine", prov), el("label", { class: "f" }, "Address", url), el("label", { class: "f" }, "Model", model), keyBox),
        el("div", { class: "hr" }),
        el("h2", {}, "Reasoning"),
        el("p", { class: "muted small", style: "margin-top:-4px" }, "Quick switches the model's thinking off for speed. Deep switches it on for considered answers. Each can use its own model."),
        el("div", { class: "row" }, el("label", { class: "f" }, "Default", defMode), el("label", { class: "f" }, "Quick model", quickModel), el("label", { class: "f" }, "Deep model", deepModel)),
        el("div", { class: "row", style: "margin-top:22px" },
          el("button", { type: "button", class: "btn", onclick: async () => { const a = await save(); toast(a.connected ? "ok" : "info", a.connected ? "Saved and connected" : "Saved", a.connected ? a.description : a.reason); } }, "Save"),
          el("button", { type: "button", class: "btn primary", onclick: async ev => {
            const btn = ev.currentTarget; const a = await save();
            if (!a.connected) return toast("bad", "No engine to test", a.reason);
            btn.disabled = true; await testEngine(); btn.disabled = false;
          } }, icon("sparkle"), "Test the engine")))),
      el("div", { class: "stack" }, el("div", { class: "card side-card" }, el("h2", {}, icon("external"), "Linked apps"),
        el("p", { class: "muted small", style: "margin-top:-4px" }, "Storyboard and Visual Feedback are coming soon; when they arrive, the Studio opens them from here. Use a web address or a program path."),
        apps.map(([, i, name]) => el("label", { class: "f", style: "margin-bottom:14px" }, name, i)),
        el("button", { type: "button", class: "btn primary", onclick: async () => { await save(); toast("ok", "Linked apps saved"); } }, "Save")))));
  showFields(); showStatus(AI);
  const gc = gemmaCard(); app().querySelector(".ai-card").after(gc); gc.after(await cloudCard());
  const jc = jonCard(); app().querySelector(".cols .side-card")?.after(jc); jc.after(displayCard());
}
function jonCard() {
  const sw = el("button", { type: "button", class: "switch", role: "switch", "aria-label": "Jonny offers tips", "aria-checked": String(tipsOn()) }, el("i"));
  sw.addEventListener("click", () => { const on = !tipsOn(); setTips(on); sw.setAttribute("aria-checked", String(on)); COACH.ignored = 0; COACH.snoozed.clear();
    toast(on ? "ok" : "info", on ? "Jonny will offer tips again" : "Jonny will keep quiet", on ? "Only when you look stuck, never while you type." : "Click him any time to ask a question."); });
  const reveal = el("select", { "aria-label": "Show Jonny's answers" }, [["stream", "As they're written"], ["finished", "When finished"]].map(([v, l]) => el("option", { value: v, selected: askReveal() === v }, l)));
  reveal.addEventListener("change", () => { try { localStorage.setItem("jonny-reveal", reveal.value); } catch (e) { /* private window */ }
    toast("ok", reveal.value === "finished" ? "Answers appear when finished" : "Answers appear as they're written", reveal.value === "finished" ? "Jonny shows a steady note while he writes." : "Line by line, steady, nothing blinks."); });
  return el("div", { class: "card side-card jon-card", style: "margin-top:20px" },
    el("div", { class: "row", style: "align-items:center;gap:14px;flex-wrap:nowrap" }, el("span", { class: "jon jon-avatar", html: jonSvg(true) }),
      el("div", { style: "flex:1" }, el("h2", { style: "margin:0" }, "Jonny"), el("div", { class: "muted small" }, "Your guide to the Studio and Saracen Bridge's methods."))),
    el("div", { class: "row", style: "justify-content:space-between;align-items:center;margin-top:16px;flex-wrap:nowrap" },
      el("span", { class: "small" }, "Offer tips when I look stuck"), sw),
    el("div", { class: "row", style: "justify-content:space-between;align-items:center;margin-top:12px;flex-wrap:nowrap" },
      el("span", { class: "small" }, "Show answers"), reveal),
    el("button", { type: "button", class: "btn sm quiet", style: "margin-top:12px;padding:0", onclick: () => {
      try { Object.keys(localStorage).filter(k => k.startsWith("jon-seen-")).forEach(k => localStorage.removeItem(k)); } catch (e) { /* private window */ }
      toast("ok", "First-visit tips reset", "Jonny will offer a walkthrough the next time you open each tool.");
    } }, "Show first-visit walkthroughs again"));
}
/* ---------------- Gemma on this computer: downloaded by the Studio itself (Tim, 13 Oct) ----------------
   On Jon's PC the installer's download of the 6.1 GB model timed out and could only start again from zero. The Studio
   now fetches it in the background, carrying on from the last byte after a dropped connection, a closed Studio or a
   restart, and checks every file before it is used. */
const gb = n => `${(n / 1e9).toFixed(n >= 1e10 ? 0 : 1)} GB`;
const etaText = s => s == null ? "" : s < 90 ? "under 2 min left" : s < 5400 ? `about ${Math.round(s / 60)} min left` : `about ${(s / 3600).toFixed(1)} hours left`;
function gemmaCard() {
  const box = el("div", { class: "card gemma-card", style: "margin-top:20px" });
  let timer = null, was = null;
  const go = async model => { try { await api.post("/api/ai/download", { model }); } catch (e) { toast("bad", "Couldn't start the download", e.message); } draw(); };
  const draw = async () => {
    clearTimeout(timer);
    if (!document.body.contains(box) && was !== null) return;
    let d; try { d = await api.get("/api/ai/download"); } catch (e) { return; }
    const pct = d.total_bytes ? Math.floor(100 * (d.done_bytes || 0) / d.total_bytes) : 0;
    const name = d.model_name || "Gemma";
    const rec = d.memory_gb >= 15 ? "12b" : "e4b";
    const opt = m => d.options[m];
    const head = el("h2", {}, icon("download"), "Gemma on this computer");
    const note = el("p", { class: "muted small", style: "margin-top:-4px" }, "Downloads in the background while you work, from Google's official source, and is checked before it is used. If the connection drops or the Studio closes, it carries on from where it stopped.");
    const bar = () => el("div", { class: "dl-track" + (d.active ? " live" : "") }, el("i", { style: `width:${pct}%` }));
    const nums = () => el("div", { class: "dl-nums" }, el("span", {}, `${gb(d.done_bytes || 0)} of ${gb(d.total_bytes || 0)}`),
      d.active && d.speed ? el("span", {}, `${(d.speed / 1e6).toFixed(1)} MB/s · ${etaText(d.eta_s)}`) : el("span", {}, `${pct}%`));
    let bodyEls;
    if (d.active) bodyEls = [el("div", { class: "dl-title" }, el("b", {}, `Downloading ${name}`), d.item && d.item !== name ? el("span", { class: "muted small" }, ` · ${d.item}`) : null),
      bar(), nums(), d.message ? el("p", { class: "small", style: "margin:8px 0 0;color:var(--fg-2)" }, d.message) : null,
      el("div", { class: "row", style: "margin-top:14px" }, el("button", { type: "button", class: "btn sm", onclick: async () => { await api.post("/api/ai/download/pause", {}); draw(); } }, icon("stop"), "Pause"))];
    else if (d.state === "paused" || d.state === "waiting") bodyEls = [el("div", { class: "dl-title" }, el("b", {}, `${name}: paused at ${pct}%`)), bar(), nums(),
      el("div", { class: "row", style: "margin-top:14px" }, el("button", { type: "button", class: "btn primary sm", onclick: () => go(d.model) }, icon("download"), "Resume"))];
    else if (d.state === "error") bodyEls = [el("p", { class: "note FAIL", style: "margin:0" }, d.error), d.total_bytes ? bar() : null, d.total_bytes ? nums() : null,
      el("div", { class: "row", style: "margin-top:14px" }, el("button", { type: "button", class: "btn primary sm", onclick: () => go(d.model) }, icon("download"), "Try again"))];
    else {
      const have = Object.keys(d.options).filter(m => opt(m).installed);
      bodyEls = [have.length ? el("p", { class: "small", style: "margin:0 0 12px" }, icon("check"), ` ${have.map(m => opt(m).name).join(" and ")} installed and ready.`) : null,
        el("div", { class: "row", style: "gap:10px" }, ["12b", "e4b"].filter(m => !opt(m).installed).map(m => el("button", { type: "button", class: "btn sm" + (m === rec && !have.length ? " primary" : ""), onclick: () => go(m) },
          icon("download"), `${have.length ? "Also download" : "Download"} ${opt(m).name} · ${gb(opt(m).to_download)}`))),
        !have.length ? el("p", { class: "muted small", style: "margin:10px 0 0" }, d.memory_gb ? `This computer has about ${d.memory_gb} GB of memory: ${rec === "12b" ? "Gemma 4 12B (best writing) suits it." : "Gemma 4 E4B (lighter) suits it; 12B wants about 16 GB."}` : "Gemma 4 12B writes best and wants about 16 GB of memory; E4B is lighter.") : null];
    }
    put(box, head, note, ...bodyEls);
    if (AI.download ? (AI.download.state !== d.state || AI.download.done_bytes !== d.done_bytes) : true) { AI.download = d; engineChip(); }
    if (was && was !== "done" && d.state === "done") { toast("ok", `${name} is ready`, "Writing tools are switched on."); AI = await api.get("/api/ai/status").catch(() => AI); engineChip(); }
    was = d.state;
    if (d.active || d.state === "starting") timer = setTimeout(draw, 1500);
  };
  draw();
  return box;
}
async function dlWatch() {
  /* the sidebar follows a running download; when it finishes the AI switches on without a restart */
  const d = AI.download || {};
  if (!(d.active || d.state === "starting")) return;
  const before = d.state;
  try { AI = await api.get("/api/ai/status"); } catch (e) { return; }
  engineChip();
  const now = AI.download || {};
  if (before !== "done" && now.state === "done" && !location.hash.startsWith("#/settings")) toast("ok", `${now.model_name || "Gemma"} is ready`, "Writing tools are switched on.");
}

async function cloudCard() {
  let c = await api.get("/api/cloud");
  const card = el("div", { class: "card cloud-card", style: "margin-top:20px" });
  const keyIn = el("input", { type: "password", autocomplete: "off", spellcheck: "false", "aria-label": "API key" });
  const model = el("input", { type: "text", "aria-label": "Model", list: "cloud-models" });
  const models = el("datalist", { id: "cloud-models" });
  const chat = el("input", { type: "checkbox" }), writing = el("input", { type: "checkbox" });
  let prov = c.provider;
  const sw = el("button", { type: "button", class: "switch", role: "switch", "aria-label": "Use my cloud AI" }, el("i"));
  const draw = () => {
    const P = c.providers[prov];
    sw.setAttribute("aria-checked", String(c.enabled));
    keyIn.value = ""; keyIn.placeholder = c.keys[prov] ? `Saved (${c.keys[prov]}). Paste a new key to replace it.` : `Paste your ${P.name} API key`;
    model.placeholder = P.model; model.value = c.provider === prov ? (c.model === P.model ? "" : c.model) : "";
    chat.checked = !!c.use_for.chat; writing.checked = !!c.use_for.writing;
    put(segs, Object.entries(c.providers).map(([id, x]) => el("button", { type: "button", "aria-pressed": String(id === prov), onclick: () => { prov = id; put(models); draw(); } },
      el("b", {}, x.name), el("small", {}, x.maker))));
    put(keyLink, el("a", { href: P.keys_at, target: "_blank", rel: "noopener" }, `Get a ${P.name} key`, icon("external")));
    put(state, c.enabled ? el("span", { class: "pill AI" }, `On · ${c.providers[c.provider].name}`) : el("span", { class: "pill" }, "Off"));
    put(warnName, c.providers[prov].maker);
  };
  const segs = el("div", { class: "tabs provs", role: "group", "aria-label": "Provider" });
  const keyLink = el("span", { class: "small" }), state = el("span", {}), warnName = el("b", {});
  const body = () => ({ provider: prov, model: model.value.trim(), use_for: { chat: chat.checked, writing: writing.checked }, ...(keyIn.value.trim() ? { key: keyIn.value.trim() } : {}) });
  const save = async extra => {
    try { c = await api.put("/api/cloud", { ...body(), ...extra }); AI = await api.get("/api/ai/status"); engineChip(); if (ASK.node) ASK.node.draw(); draw(); return true; }
    catch (e) { toast("bad", "Not saved", e.message); c = await api.get("/api/cloud"); draw(); return false; }
  };
  sw.addEventListener("click", async () => {
    const on = !c.enabled;
    if (on && !(await modal({ icon: "cloud", title: "Send questions to the cloud?", body: [`With this on, what you ask Jonny${writing.checked ? ", and scripts sent for coverage," : ""} goes to ${c.providers[prov].maker} under your own account and is billed to it. The page you're on goes too, unless you switch off "Reads this page" in the chat.`, "Gemma on this computer stays available: switch this off at any time."], actions: [["Keep it local", false], ["Turn on", true, true]] }))) return;
    if (await save({ enabled: on })) toast(on ? "ai" : "ok", on ? `Cloud AI on: ${c.providers[c.provider].name}` : "Cloud AI off", on ? `Model ${c.model}. Answers are marked Cloud.` : "Everything runs on this computer again.");
  });
  card.append(
    el("div", { class: "row", style: "justify-content:space-between;align-items:center;margin-bottom:6px" },
      el("h2", { style: "margin:0" }, icon("cloud"), "Cloud AI", el("small", {}, "optional · your own account")), el("div", { class: "row", style: "gap:12px;align-items:center" }, state, sw)),
    el("p", { class: "muted small" }, "Gemma on this computer is the default. For sharper answers, connect your own Claude, ChatGPT or Gemini account; the provider bills you for what you use."),
    segs,
    el("div", { class: "row", style: "margin-top:16px" },
      el("label", { class: "f", style: "flex:2 1 300px" }, el("span", { class: "row", style: "justify-content:space-between;gap:10px" }, "API key", keyLink), keyIn),
      el("label", { class: "f", style: "flex:1 1 200px" }, "Model", model, models),
      el("button", { type: "button", class: "btn", onclick: async () => {
        if (keyIn.value.trim() && !(await save())) return;
        try { const r = await api.get(`/api/cloud/models?provider=${prov}`); put(models, r.models.map(m => el("option", { value: m }))); toast("ok", `${r.models.length} models on your account`, "Pick one in the Model box, or leave it blank for the default."); }
        catch (e) { toast("bad", "Couldn't list models", e.message); }
      } }, "List models")),
    el("div", { class: "uses" },
      el("label", {}, chat, el("span", {}, el("b", {}, "Ask Jonny chat"), el("small", {}, "Questions and the page you're on"))),
      el("label", {}, writing, el("span", {}, el("b", {}, "Writing tools"), el("small", {}, "Coverage. The whole script is sent")))),
    el("div", { class: "note PRELIMINARY" }, icon("lock"), " When this is on, what you send goes to ", warnName, " under your account. Leave writing tools off for confidential scripts. Your key stays on this computer, encrypted for your Windows account, and is never shown again."),
    el("div", { class: "row", style: "margin-top:18px" },
      el("button", { type: "button", class: "btn", onclick: async () => { if (await save()) toast("ok", "Cloud settings saved", c.keys[prov] ? `${c.providers[prov].name} key ${c.keys[prov]}` : "No key saved yet."); } }, "Save"),
      el("button", { type: "button", class: "btn primary", onclick: async ev => {
        const b = ev.currentTarget; if (!(await save())) return; b.disabled = true;
        const close = toast("ai", `Asking ${c.providers[prov].name}…`, null, 60000);
        try { const r = await api.post("/api/cloud/test", {}); close(); toast("ok", `Answered in ${r.seconds} s`, `${r.engine}: “${r.reply}”`, 8000); }
        catch (e) { close(); toast("bad", "No answer", e.message); }
        b.disabled = false;
      } }, icon("cloud"), "Test the connection"),
      c.keys[prov] ? el("button", { type: "button", class: "btn quiet", onclick: async () => { if (await modal({ icon: "trash", title: "Remove the saved key?", body: [`The ${c.providers[prov].name} key is deleted from this computer and cloud AI switches off.`], actions: [["Keep it", false], ["Remove", true, true]] })) { await save({ clear_key: true, enabled: false }); toast("ok", "Key removed"); } } }, "Remove key") : null));
  draw();
  return card;
}

/* web links open in the default browser (the Studio window only shows the Studio) */
document.addEventListener("click", e => {
  const a = e.target.closest && e.target.closest("a[href^='http']");
  if (!a || e.defaultPrevented || location.host === a.host) return;
  e.preventDefault();
  api.post("/api/open-url", { url: a.href }).then(() => toast("info", "Opened in your browser", a.host)).catch(err => toast("bad", "Couldn't open the link", err.message));
});

/* ---------------- interface scale (Tim, 13 Oct) ----------------
   Text and layout scale as one: a single uniform zoom on the page, never a per-axis stretch, so letters keep their
   shape on any screen. Auto follows the window's shorter side against the 1440 x 900 the Studio is drawn at, damped
   and held between 90% and 120%; Settings can pin it. Viewport units in the CSS divide by --uiz, so nothing overflows. */
function uiSizePref() { try { return localStorage.getItem("ui-size") || "auto"; } catch (e) { return "auto"; } }
function uiScale() {
  let z = parseFloat(uiSizePref());
  if (!(z > 0)) { const r = Math.min(innerWidth / 1440, innerHeight / 900); z = Math.min(1.2, Math.max(.9, 1 + (r - 1) * .5)); }
  z = Math.round(z * 100) / 100;
  if (document.documentElement.style.getPropertyValue("--uiz") !== String(z)) document.documentElement.style.setProperty("--uiz", String(z));
  return z;
}
uiScale();
{ let raf = 0; addEventListener("resize", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(uiScale); }); }
function displayCard() {
  const sizes = [["auto", "Auto"], ["0.9", "90%"], ["1", "100%"], ["1.1", "110%"], ["1.25", "125%"]];
  const now = el("div", { class: "muted small", style: "margin-top:12px" });
  const bar = el("div", { class: "tabs sizes", role: "group", "aria-label": "Interface size", style: "margin:0" });
  const draw = () => {
    const pref = uiSizePref(), z = uiScale();
    put(bar, sizes.map(([v, l]) => el("button", { type: "button", "aria-pressed": String(pref === v), onclick: () => {
      try { v === "auto" ? localStorage.removeItem("ui-size") : localStorage.setItem("ui-size", v); } catch (e) { /* private window */ }
      draw(); } }, l)));
    put(now, pref === "auto" ? `Showing at ${Math.round(z * 100)}% for this window.` : `Pinned at ${Math.round(z * 100)}%.`);
  };
  draw();
  return el("div", { class: "card side-card", style: "margin-top:20px" }, el("h2", {}, icon("eye"), "Display"),
    el("p", { class: "muted small", style: "margin-top:-4px" }, "Text and layout scale together, as one, so letters keep their shape on any screen. Auto sizes the Studio to the window."),
    bar, now,
    /Mac/.test(navigator.userAgent) ? null   /* the Mac picks the screen's own resolution; the note is about Windows */
      : el("p", { class: "muted small", style: "margin:14px 0 0" }, "If letters look wide or squashed in every program, not just here, Windows is stretching a resolution the monitor wasn't made for. In Windows, open Settings › System › Display and pick the resolution marked (Recommended)."));
}

/* ---------------- boot ---------------- */
(async () => {
  const t0 = performance.now();
  const boot = document.getElementById("boot");
  let intro = false;
  try { intro = !sessionStorage.getItem("sb-intro"); sessionStorage.setItem("sb-intro", "1"); } catch (e) { intro = true; }
  if (boot && intro && !CALM) boot.prepend(logo3d({ sub: "STUDIO", sweep: 3.2, delay: .5, max: 6 })); else if (boot) boot.classList.add("done");
  const mark = document.querySelector(".mark");
  if (mark && window.SB_MARKS) put(mark, logo3d({ sub: "STUDIO", max: 14, delay: 2 }));
  const reveal = () => { if (!boot || boot.classList.contains("done")) return; setTimeout(() => { boot.classList.add("done"); setTimeout(() => boot.remove(), 600); }, Math.max(0, 1500 - (performance.now() - t0))); };
  try {
    CAT = await api.get("/api/catalog");
    VERSION = (await api.get("/api/health").catch(() => ({}))).version || "";
    AI = await api.get("/api/ai/status").catch(() => AI);
    MODE = (await api.get("/api/settings").catch(() => ({ ai_engine: {} }))).ai_engine.default_mode || "quick";
    window.addEventListener("hashchange", route);
    const beat = () => fetch("/api/heartbeat", { method: "POST" }).catch(() => {});
    beat(); setInterval(beat, 30000);
    setInterval(pollJobs, 8000); pollJobs();
    setInterval(dlWatch, 3000);
    COACH.started = true; coachStart();
    await route();
    reveal();
  } catch (e) { reveal(); put(app(), errBox("The engine did not respond: " + e.message)); }
})();
