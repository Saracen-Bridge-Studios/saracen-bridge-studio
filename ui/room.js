"use strict";
/* The Room (1.0.8): a private, encrypted team hub per production: board, chat, files, call sheets, voice and meetings.
   The page talks only to the local Studio (/api/room/...), which holds this computer's keys and encrypts before anything
   leaves for the hub. Design: docs/DESIGN.md (gold and ivory states, no plum on Room surfaces, no flashing). */

Object.assign(ICONS, {
  hash: "M9.5 3.5 7.5 20.5M16.5 3.5l-2 17M4 9h16.5M3.5 15H20",
  board: "M4 4.5h7v7H4zM13 4.5h7v4h-7zM13 10.5h7v9h-7zM4 13.5h7v6H4z",
  mic: "M12 14.5a3 3 0 0 0 3-3v-5a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3zM5.5 11a6.5 6.5 0 0 0 13 0M12 17.5v3",
  micoff: "M9 6.5a3 3 0 0 1 6 0v5a3 3 0 0 1-.9 2.1M5.5 11a6.5 6.5 0 0 0 10.4 5.2M12 17.5v3M4 4l16 16",
  video: "M3.5 7h11v10h-11zM14.5 10.5l6-3.5v10l-6-3.5",
  pin: "M14.5 4.5l5 5-3 1-3.5 3.5.5 4-2 .5-3-3-4.5 4.5M9.5 12.5l-3-3 .5-2 4 .5 3.5-3.5z",
  bell: "M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15zM10 20.5a2 2 0 0 0 4 0",
  shield: "M12 3.5l7.5 3v5.5c0 4.5-3.2 7.7-7.5 9-4.3-1.3-7.5-4.5-7.5-9V6.5z",
  hand: "M8 13V6.5a1.5 1.5 0 0 1 3 0V11M11 10.5V5a1.5 1.5 0 0 1 3 0v6M14 11V6.5a1.5 1.5 0 0 1 3 0V14c0 4-2.5 6.5-6 6.5-2.6 0-4.2-1.4-5.5-3.6L4 14a1.5 1.5 0 0 1 2.5-1.6L8 14",
  door: "M6 20.5V4.5a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v16M3.5 20.5h17M14.5 12h.01",
});

const RM = { st: null, v: null, prod: null, space: "board", tab: "board", sv: null, seq: 0, loop: 0, seenNote: 0, q: "" };
const TIERS = [["producer", "Producer"], ["key", "Key personnel"], ["crew", "Crew"], ["cast", "Cast"], ["guest", "Guest"]];
const STATUSES = ["Open", "Needs review", "Decision", "Done"];
const STATUS_PILL = { Open: "", "Needs review": "WARN", Decision: "PASS", Done: "DONE" };
const bytes = n => n == null ? "—" : n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(0)} KB` : n < 1073741824 ? `${(n / 1048576).toFixed(1)} MB` : `${(n / 1073741824).toFixed(2)} GB`;
const when = ts => { const d = new Date(ts * 1000), now = new Date(); const same = d.toDateString() === now.toDateString();
  return same ? d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }) : d.toLocaleDateString("en-GB", { day: "numeric", month: "short" }); };
function roomBadge() { const v = RM.v; if (!v) return null; const n = (v.pending || 0) + (v.notifications || []).length; return n ? n : null; }
const onRoom = () => (location.hash || "").startsWith("#/room");

async function roomRoute(a, b) {
  RM.st = await api.get("/api/room/state");
  if (a === "joining") return roomJoining();
  if (RM.st.status === "none" || RM.st.status === "declined" || RM.st.status === "revoked") return roomSetup();
  if (RM.st.status === "pending") return roomJoining();
  if (a === "access") return roomAccess();
  if (a === "callsheet" && typeof callsheetEditor === "function") return callsheetEditor(b);
  if (a === "meet" && typeof meetPage === "function") return meetPage(b);
  return roomMain(a, b);
}

/* ---------------- joining or founding a Room ---------------- */
function roomSetup() {
  topbar(["Studio", "Room"]);
  const link = el("input", { type: "text", placeholder: "Paste the invite link you were sent", "aria-label": "Invite link", style: "width:100%" });
  const name = el("input", { type: "text", placeholder: "Your name", "aria-label": "Your name", style: "width:100%" });
  const fname = el("input", { type: "text", placeholder: "Your name", "aria-label": "Your name", style: "width:100%" });
  const prod = el("input", { type: "text", placeholder: "e.g. SHADE", "aria-label": "Production name", style: "width:100%" });
  const busy = async (btn, fn) => { btn.disabled = true; try { await fn(); } catch (e) { toast("bad", "Couldn't do that", e.message); } btn.disabled = false; };
  put(app(), el("h1", {}, "The Room"),
    el("p", { class: "lede" }, "A private, encrypted hub for each production: a board, channels, files, call sheets and meetings. Everything is encrypted on this computer before it leaves, and only the people who can see a space can read it."),
    el("div", { class: "room-setup" },
      el("div", { class: "card" }, el("h2", {}, icon("door"), "Join with an invite"),
        el("p", { class: "muted small" }, "Someone at your production sent you a link. Paste it here, then an executive checks three safety words with you on a call before this computer gets in."),
        el("label", { class: "f" }, "Invite link", link), el("label", { class: "f", style: "margin-top:12px" }, "Your name", name),
        el("div", { class: "row", style: "margin-top:18px" }, el("button", { type: "button", class: "btn primary", onclick: e => busy(e.currentTarget, async () => {
          if (!link.value.trim()) throw new Error("Paste the invite link first.");
          await api.post("/api/room/join", { invite: link.value.trim(), name: name.value.trim() }); location.hash = "#/room/joining"; route(); }) }, "Join"))),
      el("div", { class: "card" }, el("h2", {}, icon("reel"), "Start a production"),
        el("p", { class: "muted small" }, "The production lives on this computer. You invite people with a link, and they connect to it here. Nothing to install and no web address needed."),
        el("label", { class: "f" }, "Your name", fname), el("label", { class: "f", style: "margin-top:12px" }, "Production", prod),
        el("div", { class: "row", style: "margin-top:18px" }, el("button", { type: "button", class: "btn primary", onclick: e => busy(e.currentTarget, async () => {
          if (!fname.value.trim() || !prod.value.trim()) throw new Error("Enter your name and the production's name.");
          const r = await api.post("/api/room/host", { name: fname.value.trim(), production: prod.value.trim() });
          toast("ok", `${prod.value.trim()} is set up`, "It runs on this computer. Invite people from Members & access.");
          RM.prod = r.id; RM.space = "board"; location.hash = `#/room/${r.id}`; route(); }) }, "Start")))));
}

async function roomJoining() {
  topbar(["Studio", "Room"]);
  const box = el("div", { class: "card room-words" });
  put(app(), el("h1", {}, "Joining the Room"), el("p", { class: "lede" }, "An executive approves this computer after you both check the same three words."), box);
  const tick = async () => {
    if (!onRoom()) return;
    let r;
    try { r = await api.get("/api/room/join"); } catch (e) { put(box, errBox(e)); return setTimeout(tick, 5000); }
    if (r.stage === "approved") { await roomOversightOnce(true); if (location.hash !== "#/room") { location.hash = "#/room"; return; } return route(); }
    if (r.stage === "declined" || r.stage === "none") {
      put(box, el("h2", {}, "This computer wasn't approved"), el("p", {}, "The invite was declined or has expired. Ask for a new invite."),
        el("button", { type: "button", class: "btn", onclick: async () => { await api.post("/api/room/leave", {}); if (location.hash !== "#/room") location.hash = "#/room"; else route(); } }, "Start again"));
      return;
    }
    if (r.stage === "waiting") put(box, el("h2", {}, icon("clock"), "Waiting for an executive"),
      el("p", {}, "Call the executive who approves new devices. Ask them to open Room › Members & access and press Check next to your name. Your safety words appear here then."));
    else put(box, el("h2", {}, "Your safety words"), el("div", { class: "words" }, r.words.map(w => el("span", {}, w))),
      el("p", {}, "Read these three words to the executive on the call. If their screen shows the same three words in the same order, they approve this computer."),
      el("p", { class: "muted small" }, "If the words are different, say so and stop: someone may be trying to get in between you."));
    setTimeout(tick, 2500);
  };
  tick();
}

async function roomOversightOnce(force) {
  const v = RM.v;
  if (!force && v && v.oversight_seen) return;
  await modal({ icon: "shield", title: "Oversight in the Room", body: [v ? v.oversight : "Executives on this production can read every space, file and private message in the Room. Every read is recorded in the audit log."], actions: [["I understand", true, true]] });
  await api.post("/api/room/oversight-seen", {}).catch(() => null);
  if (RM.v) RM.v.oversight_seen = true;
}

/* ---------------- the room: spaces on the left, board/chat/files in the middle, voice on the right ---------------- */
async function roomMain(a, b) {
  if (a && a.startsWith("p_")) RM.prod = a;
  if (b) RM.space = b;
  await roomLoad();
  roomDraw();
  roomLive();
}

async function roomLoad() {
  /* the open space first (opening it marks it read), then the view with its unread counts */
  RM.sv = RM.space !== "board" ? await api.get(`/api/room/space/${RM.space}`).catch(() => null) : null;
  RM.v = await api.get("/api/room/view" + (RM.prod ? `?production=${encodeURIComponent(RM.prod)}` : ""));
  RM.prod = RM.v.production;
  const known = new Set([...(RM.v.spaces || []), ...(RM.v.dms || []), RM.v.my_day].filter(Boolean).map(s => s.id));
  if (RM.space !== "board" && (!known.has(RM.space) || !RM.sv)) { RM.space = "board"; RM.tab = "board"; RM.sv = null; }
  roomNotify();
}

function roomNotify() {
  const ns = RM.v.notifications || [];
  const fresh = ns.filter(n => n.id > RM.seenNote);
  if (RM.seenNote && fresh.length) {
    const n = fresh[fresh.length - 1];
    const what = { mention: "mentioned you", dm: "sent you a message", callsheet: "posted a call sheet", reminder: "reminded you about the call sheet" }[n.kind] || "posted something";
    toast("info", `${n.who} ${what}`, n.where ? `In ${n.where}` : null);
  }
  if (ns.length) RM.seenNote = Math.max(RM.seenNote, ...ns.map(n => n.id));
  else if (!RM.seenNote) RM.seenNote = 1;
}

function roomTopbar() {
  topbar(["Room"]);
  const v = RM.v;
  const crumbs = document.querySelector("#topbar .crumbs");
  if (!crumbs || !v.production) return;
  const menu = el("div", { class: "prod-menu", role: "menu", hidden: true });
  const btn = el("button", { type: "button", class: "prod-switch", "aria-haspopup": "true", "aria-expanded": "false",
    onclick: () => { const open = menu.hidden; menu.hidden = !open; btn.setAttribute("aria-expanded", String(open)); } },
    el("span", { class: "lbl" }, "Production"), el("b", {}, v.production_name), v.archived ? el("span", { class: "muted small" }, "archived") : null, icon("arrow", "rot"));
  put(menu, el("div", { class: "pm-h" }, "Your productions"),
    v.productions.map(p => el("button", { type: "button", role: "menuitem", "aria-pressed": String(p.id === v.production),
      onclick: () => { menu.hidden = true; location.hash = `#/room/${p.id}`; } },
      el("span", { class: "pm-n" }, p.name, p.archived ? el("small", {}, " · archived") : null, p.here ? el("small", {}, " · on this computer") : null), el("span", { class: "pm-c" }, plural(p.members, "person", "people")))),
    el("button", { type: "button", class: "pm-new", onclick: () => { menu.hidden = true; roomNewProduction(); } }, icon("plus"), "Start a production"),
    el("button", { type: "button", class: "pm-new", onclick: () => { menu.hidden = true; roomJoinAnother(); } }, icon("door"), "Join with an invite"));
  if (!RM.menuOff) {          /* one listener for the page: a click outside an open menu closes it */
    RM.menuOff = e => document.querySelectorAll(".prod-menu:not([hidden])").forEach(m => { const w = m.closest(".prod-wrap");
      if (w && !w.contains(e.target)) { m.hidden = true; w.querySelector(".prod-switch")?.setAttribute("aria-expanded", "false"); } });
    document.addEventListener("click", RM.menuOff);
  }
  put(crumbs, el("div", { class: "prod-wrap" }, btn, menu),
    el("span", { class: "enc", title: "Messages, files and names are encrypted on this computer before they reach the Room's server." }, icon("lock"),
      v.live ? "Encrypted" : "Encrypted · reconnecting"));
}

function roomDraw() {
  const v = RM.v;
  roomTopbar();
  if (!v.production) {
    put(app(), el("h1", {}, "The Room"), el("p", { class: "lede" }, "Start a production on this computer, or join one with an invite. Each production has its own people, spaces, board, files and call sheets."),
      el("div", { class: "row" }, el("button", { type: "button", class: "btn primary", onclick: roomNewProduction }, icon("plus"), "Start a production"),
        el("button", { type: "button", class: "btn", onclick: roomJoinAnother }, icon("door"), "Join with an invite")));
    return;
  }
  const side = el("aside", { class: "room-side", "aria-label": "Spaces" });
  const item = (id, glyph, label, extra, unread) => el("button", { type: "button", class: "rs-item", "aria-pressed": String(RM.space === id),
    onclick: () => { RM.space = id; RM.tab = id === "board" ? "board" : "chat"; roomOpen(); } },
    el("span", { class: "g" }, glyph), el("span", { class: "t" }, label), extra || null, unread ? el("span", { class: "n" }, unread) : null);
  put(side,
    el("div", { class: "rs-grp" }, "Spaces"),
    item("board", icon("board"), "Production board"),
    v.my_day ? item(v.my_day.id, icon("clock"), "My day", null, v.my_day.unread) : null,
    v.spaces.map(s => item(s.id, icon("hash"), s.name, s.member ? null : el("span", { class: "ov", title: "You aren't in this space. Reading it is logged." }, icon("eye")), s.unread)),
    v.can_manage && !v.archived ? el("button", { type: "button", class: "rs-add", onclick: roomNewSpace }, icon("plus"), "New space") : null,
    el("div", { class: "rs-grp" }, "Direct"),
    v.dms.map(d => item(d.id, el("span", { class: "av" }, (d.name || "?").split(/\s+/).map(x => x[0]).slice(0, 2).join("").toUpperCase()), d.name,
      d.oversight ? el("span", { class: "ov", title: "Not your conversation. Reading it is logged." }, icon("eye")) : el("span", { class: "tierlbl" }, d.tier), d.unread)),
    !v.archived ? el("button", { type: "button", class: "rs-add", onclick: roomNewDM }, icon("plus"), "New message") : null,
    v.can_manage ? el("a", { class: "rs-access", href: "#/room/access" }, icon("users"), "Members & access", v.pending ? el("span", { class: "n" }, v.pending) : null) : null,
    v.can_manage && !v.archived ? el("a", { class: "rs-access", href: "#/room/callsheet" }, icon("doc"), "Call sheets") : null);
  const main = el("section", { class: "room-main" });
  const aside = el("aside", { class: "room-aside", "aria-label": "Voice and people" });
  put(app(), el("div", { class: "room" }, side, main, aside));
  roomCenter(main);
  roomAside(aside);
  roomDrop(main);
  if (v.problems && v.problems.length) console.warn("Room:", v.problems);
}

async function roomOpen() {
  if (RM.space !== "board") {
    const d = (RM.v.dms || []).find(x => x.id === RM.space);
    if (d && !d.oversight) await roomOversightOnce(false);
  }
  history.replaceState(null, "", `#/room/${RM.prod}${RM.space !== "board" ? "/" + RM.space : ""}`);
  await roomLoad(); roomDraw();
}

function roomCenter(main) {
  const v = RM.v, sv = RM.sv;
  const isBoard = RM.space === "board";
  const title = isBoard ? "Production board" : (sv && sv.name) || "";
  const about = isBoard ? `Notes, decisions and files for ${v.production_name}, showing only what you're allowed to see.` : (sv && sv.about) || "";
  const search = el("input", { type: "search", placeholder: `Search ${v.production_name}: messages, notes and files`, "aria-label": "Search the room", value: RM.q });
  const results = el("div", { class: "rm-results" });
  let t = null;
  search.addEventListener("input", () => { clearTimeout(t); t = setTimeout(async () => {
    RM.q = search.value; if (RM.q.trim().length < 2) return put(results);
    const r = await api.get(`/api/room/search?production=${encodeURIComponent(v.production)}&q=${encodeURIComponent(RM.q)}`).catch(() => []);
    put(results, r.length ? el("div", { class: "card flush" }, r.map(x => el("button", { type: "button", class: "rm-hit", onclick: () => { if (x.space) { RM.space = x.space; RM.tab = x.kind === "note" ? "board" : x.kind === "file" ? "files" : "chat"; RM.q = ""; roomOpen(); } } },
      el("span", { class: "k" }, x.kind === "note" ? "Note" : x.kind === "file" ? "File" : "Message"), el("span", { class: "x" }, x.text), el("span", { class: "w" }, `${x.author} · ${x.space_name} · ${when(x.ts)}`))))
      : el("p", { class: "muted small" }, "Nothing matches."));
  }, 220); });
  const tabsBar = el("div", { class: "tabs", role: "group", "aria-label": "View" },
    (isBoard ? [["board", "Board"]] : [["board", "Board"], ["chat", "Chat"], ["files", "Files"]]).map(([id, label]) =>
      el("button", { type: "button", "aria-pressed": String(RM.tab === id), onclick: () => { RM.tab = id; roomDraw(); } }, label)));
  const body = el("div", { class: "rm-body" });
  put(main, el("div", { class: "rm-head" }, el("div", {}, el("h1", {}, title), el("p", { class: "lede" }, about)), el("label", { class: "rm-search" }, icon("search"), search)),
    results, tabsBar, body);
  if (!isBoard && sv && sv.locked_oversight) {
    return put(body, el("div", { class: "card oversight-card" }, el("h2", {}, icon("eye"), "You aren't in this space"),
      el("p", {}, "As an executive you can read it. The read is recorded in the audit log, which every executive can see."),
      el("button", { type: "button", class: "btn", onclick: async () => { RM.sv = await api.get(`/api/room/space/${RM.space}?oversight=true`); roomDraw(); } }, icon("eye"), "Read it (logged)")));
  }
  if (sv && sv.error) return put(body, errBox({ message: sv.error }));
  if (RM.tab === "board") return roomBoard(body);
  if (RM.tab === "chat") return roomChat(body);
  return roomFiles(body);
}

/* ---------------- board ---------------- */
function roomBoard(body) {
  const v = RM.v;
  const notes = RM.space === "board" ? v.board : v.board.filter(n => n.space_ids.includes(RM.space));
  const personal = RM.sv && RM.sv.kind === "personal";
  const strip = (RM.space === "board" || personal) && v.callsheet && typeof callsheetStrip === "function"
    ? [callsheetStrip(v.callsheet), personal ? callsheetRows(v.callsheet) : null] : null;
  const canPost = !v.archived && (RM.space === "board" ? (v.spaces.some(s => s.member) || !!v.my_day) : !!(RM.sv && RM.sv.member));
  put(body, strip,
    el("div", { class: "board-grid" },
      canPost ? el("button", { type: "button", class: "note-new", onclick: () => roomNoteDialog() }, el("span", { class: "plus" }, icon("plus")), el("b", {}, "Leave a note"), el("span", {}, "or drop files here")) : null,
      notes.map(n => el("article", { class: "note-card" + (n.pinned ? " pinned" : "") },
        el("div", { class: "nc-top" }, n.pinned ? el("span", { class: "pin", title: "Pinned" }, icon("pin")) : null, el("span", { class: "sp" }, n.spaces.join(" · ")), el("span", { class: "wh" }, when(n.ts))),
        el("h3", {}, n.title), n.body ? el("p", {}, n.body) : null,
        el("div", { class: "nc-foot" },
          el("button", { type: "button", class: `pill ${STATUS_PILL[n.status] || ""} st`, title: "Change status", onclick: ev => roomStatusMenu(ev.currentTarget, n) }, n.status),
          n.file ? el("a", { class: "fchip", href: `/api/room/file/${n.file.id}`, download: n.file.name }, icon("file"), n.file.name, el("small", {}, bytes(n.file.size))) : null,
          el("span", { class: "by" }, n.author)))),
      !notes.length && !canPost ? el("p", { class: "muted" }, "Nothing on the board yet.") : null));
}

function roomStatusMenu(anchor, n) {
  const menu = el("div", { class: "pop-menu", role: "menu" }, STATUSES.map(s => el("button", { type: "button", role: "menuitemradio", "aria-checked": String(s === n.status),
    onclick: async () => { menu.remove(); try { await api.post(`/api/room/note/${n.id}`, { status: s }); await roomLoad(); roomDraw(); } catch (e) { toast("bad", "Couldn't change it", e.message); } } }, s)),
    el("hr"), el("button", { type: "button", onclick: async () => { menu.remove(); await api.post(`/api/room/note/${n.id}`, { pinned: !n.pinned }).catch(e => toast("bad", "Couldn't change it", e.message)); await roomLoad(); roomDraw(); } }, n.pinned ? "Unpin" : "Pin to the top"));
  document.querySelectorAll(".pop-menu").forEach(m => m.remove());
  anchor.after(menu);
  setTimeout(() => document.addEventListener("click", function off(e) { if (!menu.contains(e.target)) { menu.remove(); document.removeEventListener("click", off); } }), 0);
}

function postable() {
  const v = RM.v;
  return [...v.spaces.filter(s => s.member && s.has_key).map(s => [s.id, "# " + s.name]), ...(v.my_day ? [[v.my_day.id, "My day"]] : [])];
}

async function roomNoteDialog(file) {
  const opts = postable();
  if (!opts.length) return toast("info", "Nowhere to post yet", "You aren't in any space on this production.");
  const title = el("input", { type: "text", placeholder: "Title", "aria-label": "Title", style: "width:100%", value: file ? file.name : "" });
  const text = el("textarea", { placeholder: "What everyone needs to know", "aria-label": "Note", rows: 4, style: "width:100%;height:auto;padding:10px 12px" });
  const status = el("select", { "aria-label": "Status" }, STATUSES.map(s => el("option", { value: s }, s)));
  const pin = el("input", { type: "checkbox", "aria-label": "Pin to the top" });
  const start = RM.space !== "board" && opts.some(([id]) => id === RM.space) ? RM.space : opts[0][0];
  const boxes = opts.map(([id, label]) => [id, el("input", { type: "checkbox", checked: id === start })]);
  const pick = file ? null : el("input", { type: "file", "aria-label": "Attach a file" });
  const ok = await modal({ icon: "board", title: "Leave a note", body: [
    el("label", { class: "f" }, "Title", title), el("label", { class: "f", style: "margin-top:10px" }, "Note", text),
    el("div", { class: "row", style: "margin-top:10px" }, el("label", { class: "f" }, "Status", status), el("label", { class: "chk" }, pin, "Pin to the top")),
    el("div", { class: "f", style: "margin-top:12px" }, el("span", {}, "Share with"), el("div", { class: "chk-list" }, boxes.map(([id, b]) => el("label", { class: "chk" }, b, opts.find(o => o[0] === id)[1])))),
    el("p", { class: "muted small" }, "Only people who can see one of these spaces see the note."),
    pick ? el("label", { class: "f", style: "margin-top:10px" }, "Attach a file (optional)", pick) : el("p", { class: "small" }, icon("file"), " ", file.name, " · ", bytes(file.size))],
    actions: [["Cancel", false], ["Post", true, true]] });
  if (!ok) return;
  const spaces = boxes.filter(([, b]) => b.checked).map(([id]) => id);
  if (!spaces.length || !title.value.trim()) return toast("bad", "Not posted", "Give the note a title and pick at least one space.");
  const f = file || (pick && pick.files[0]);
  try {
    if (f) {
      const fd = new FormData();
      fd.append("space", spaces[0]); fd.append("file", f); fd.append("note", text.value); fd.append("note_title", title.value.trim()); fd.append("note_spaces", spaces.join(","));
      await api.form("/api/room/upload", fd);
      toast("info", "Encrypting and sending", `${f.name}: the note appears when it's done.`);
      if (pin.checked || status.value !== "Open") toast("info", "Set the status and pin after it appears");
    } else await api.post("/api/room/note", { spaces, title: title.value.trim(), body: text.value, status: status.value, pinned: pin.checked });
    await roomLoad(); roomDraw();
  } catch (e) { toast("bad", "Couldn't post", e.message); }
}

/* ---------------- chat ---------------- */
function roomChat(body) {
  const sv = RM.sv;
  if (!sv) return;
  const list = el("div", { class: "chat-list", role: "log", "aria-label": "Messages" },
    sv.messages.length ? sv.messages.map(m => el("div", { class: "msg-row" + (m.mine ? " mine" : "") },
      el("div", { class: "av" }, m.initials),
      el("div", { class: "mb" }, el("div", { class: "mh" }, el("b", {}, m.author), m.tier ? el("span", { class: "tierlbl" }, m.tier) : null, el("span", { class: "wh" }, when(m.ts))),
        m.text ? el("div", { class: "mt" }, roomMentions(m.text)) : null,
        m.file ? el("a", { class: "fchip", href: `/api/room/file/${m.file.id}`, download: m.file.name }, icon("file"), m.file.name, el("small", {}, bytes(m.file.size) + (m.file.version > 1 ? ` · v${m.file.version}` : ""))) : null)))
      : el("p", { class: "muted" }, sv.kind === "dm" ? "No messages yet. Say hello." : "No messages yet."));
  const canSend = sv.member && sv.has_key && !RM.v.archived;
  const input = el("input", { type: "text", placeholder: canSend ? `Message ${sv.kind === "dm" ? sv.name : "# " + sv.name}` : "You can read this space but not post in it", "aria-label": "Message", disabled: !canSend, autocomplete: "off" });
  const sugg = el("div", { class: "mention-sugg", hidden: true });
  const send = async () => {
    const text = input.value.trim(); if (!text) return;
    input.disabled = true;
    try { await api.post("/api/room/message", { space: sv.id, text }); input.value = ""; RM.sv = await api.get(`/api/room/space/${sv.id}`); roomChat(body); body.querySelector("input")?.focus(); }
    catch (e) { toast("bad", "Not sent", e.message); input.disabled = false; }
  };
  input.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
  input.addEventListener("input", () => {
    const m = /@([\p{L}\w' -]{0,30})$/u.exec(input.value.slice(0, input.selectionStart));
    if (!m) return sugg.hidden = true;
    const q = m[1].toLowerCase();
    const hits = (sv.members || []).filter(p => p.name.toLowerCase().startsWith(q) || p.name.toLowerCase().includes(" " + q)).slice(0, 6);
    if (!hits.length) return sugg.hidden = true;
    put(sugg, hits.map(p => el("button", { type: "button", onclick: () => { input.value = input.value.slice(0, m.index) + "@" + p.name + " " + input.value.slice(input.selectionStart); sugg.hidden = true; input.focus(); } }, p.name, el("small", {}, p.tier_label))));
    sugg.hidden = false;
  });
  const attach = el("input", { type: "file", hidden: true, onchange: () => { if (attach.files[0]) roomUpload(attach.files[0], sv.id); attach.value = ""; } });
  put(body, list,
    el("div", { class: "composer" }, sugg,
      el("button", { type: "button", class: "btn quiet", "aria-label": "Attach a file", disabled: !canSend, onclick: () => attach.click() }, icon("plus")), attach,
      input, el("button", { type: "button", class: "btn primary", disabled: !canSend, onclick: send }, icon("send"), "Send")));
  list.scrollTop = list.scrollHeight;
}

function roomMentions(text) {
  const names = (RM.sv && RM.sv.members || []).map(p => p.name).filter(Boolean).sort((a, b) => b.length - a.length);
  if (!names.length) return text;
  const re = new RegExp("@(" + names.map(n => n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")", "g");
  const out = []; let last = 0, m;
  while ((m = re.exec(text))) { out.push(text.slice(last, m.index), el("span", { class: "mention" }, m[0])); last = m.index + m[0].length; }
  out.push(text.slice(last));
  return out;
}

/* ---------------- files ---------------- */
function roomFiles(body) {
  const sv = RM.sv;
  if (!sv) return;
  const up = (RM.v.uploads || []).filter(u => u.space === sv.id && u.stage !== "done");
  const canAdd = sv.member && sv.has_key && !RM.v.archived;
  const pick = el("input", { type: "file", multiple: true, hidden: true, onchange: () => { [...pick.files].forEach(f => roomUpload(f, sv.id)); pick.value = ""; } });
  put(body,
    el("div", { class: "notice files-note" }, el("div", { class: "ic" }, icon("lock")),
      el("div", { class: "grow" }, "Drop files anywhere to share them with ", el("b", {}, sv.name), ": only people who can see this space can open them. A file with the same name becomes a new version."),
      canAdd ? el("button", { type: "button", class: "btn sm", onclick: () => pick.click() }, icon("upload"), "Add files") : null, pick),
    up.length ? el("div", { class: "uploads" }, up.map(u => el("div", { class: "up" + (u.stage === "failed" ? " bad" : "") }, icon(u.stage === "failed" ? "alert" : "upload"),
      el("span", { class: "nm" }, u.name), el("span", { class: "muted small" }, u.stage === "failed" ? u.error + " It resumes on its own." : `${u.stage === "encrypting" ? "Encrypting" : "Sending"} · part ${u.done} of ${u.total}`),
      el("span", { class: "bar" }, el("i", { style: `width:${u.total ? Math.round(100 * u.done / u.total) : 0}%` }))))) : null,
    sv.files.length ? sideScroll(el("table", {}, el("thead", {}, el("tr", {}, ["File", "Shared by", "Visible to", "Size", ""].map(h => el("th", { class: h === "Size" ? "num" : null }, h)))),
      el("tbody", {}, sv.files.map(f => el("tr", {},
        el("td", {}, el("div", { class: "fname" }, icon("file"), el("span", {}, f.name), f.version > 1 ? el("span", { class: "ver", title: f.versions.map(x => `v${x.version} · ${x.by} · ${when(x.ts)}`).join("\n") }, `v${f.version}`) : null)),
        el("td", {}, f.by), el("td", { class: "small muted" }, sv.kind === "dm" ? "This conversation" : "# " + sv.name), el("td", { class: "num" }, bytes(f.size)),
        el("td", {}, el("a", { class: "btn sm quiet", href: `/api/room/file/${f.id}`, download: f.name }, icon("download"), "Download"),
          f.versions.length > 1 ? el("details", { class: "vers" }, el("summary", {}, "Earlier versions"), f.versions.slice(1).map(x => el("a", { href: `/api/room/file/${x.id}`, download: f.name }, `v${x.version} · ${x.by} · ${when(x.ts)}`))) : null))))))
      : el("p", { class: "muted" }, "No files here yet."));
}

async function roomUpload(file, space) {
  const fd = new FormData(); fd.append("space", space); fd.append("file", file);
  try { await api.form("/api/room/upload", fd); toast("info", "Encrypting and sending", file.name); RM.tab = "files"; await roomLoad(); roomDraw(); }
  catch (e) { toast("bad", "Couldn't send the file", e.message); }
}

function roomDrop(main) {
  let depth = 0;
  main.addEventListener("dragenter", e => { if (e.dataTransfer && [...e.dataTransfer.types].includes("Files")) { depth++; main.classList.add("dropping"); e.preventDefault(); } });
  main.addEventListener("dragover", e => { if (main.classList.contains("dropping")) e.preventDefault(); });
  main.addEventListener("dragleave", () => { if (--depth <= 0) { depth = 0; main.classList.remove("dropping"); } });
  main.addEventListener("drop", e => {
    e.preventDefault(); depth = 0; main.classList.remove("dropping");
    const files = [...(e.dataTransfer.files || [])]; if (!files.length) return;
    if (RM.space === "board") return roomNoteDialog(files[0]);
    if (!(RM.sv && RM.sv.member && RM.sv.has_key)) return toast("info", "You can't add files here");
    files.forEach(f => roomUpload(f, RM.space));
  });
}

/* ---------------- the right column: voice (meetings.js) and who's here ---------------- */
function roomAside(aside) {
  const v = RM.v, sv = RM.sv;
  const voice = typeof voicePanel === "function" ? voicePanel(v, sv) : null;
  const people = sv && sv.members ? sv.members : [];
  put(aside, voice,
    el("section", { class: "card ra-people" }, el("h2", {}, RM.space === "board" ? "On this production" : "In this space", el("small", {}, RM.space === "board" ? plural(v.people.length, "person", "people") : plural(people.length, "person", "people"))),
      el("ul", { class: "plain people" }, (RM.space === "board" ? v.people : people).slice(0, 40).map(p => el("li", {},
        el("span", { class: "av sm" }, p.initials), el("span", { class: "pn" }, p.name, el("small", {}, [p.tier_label, p.department].filter(Boolean).join(" · "))),
        p.can_reach && p.user !== v.me.user ? el("button", { type: "button", class: "btn sm quiet", "aria-label": `Message ${p.name}`, onclick: () => roomStartDM(p.user) }, icon("chat")) : null)))),
    el("p", { class: "muted small oversight-line" }, icon("shield"), " ", v.oversight));
}

async function roomStartDM(user) {
  try { const r = await api.post("/api/room/dm", { production: RM.prod, user }); await roomOversightOnce(false); RM.space = r.id; RM.tab = "chat"; await roomOpen(); }
  catch (e) { toast("bad", "Couldn't start the conversation", e.message); }
}

async function roomNewDM() {
  const reach = RM.v.people.filter(p => p.can_reach);
  if (!reach.length) return toast("info", "No one to message yet", "You can message the people your tier reaches; an executive can open more.");
  let chosen = null;
  const list = el("div", { class: "pick-list" }, reach.map(p => el("button", { type: "button", onclick: e => { chosen = p.user; list.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", "false")); e.currentTarget.setAttribute("aria-pressed", "true"); } },
    el("span", { class: "av sm" }, p.initials), el("span", {}, p.name, el("small", {}, [p.tier_label, p.department].filter(Boolean).join(" · "))))));
  const ok = await modal({ icon: "chat", title: "New message", body: [el("p", { class: "muted small" }, "People you can reach on this production."), list], actions: [["Cancel", false], ["Start", true, true]] });
  if (ok && chosen) roomStartDM(chosen);
}

async function roomNewProduction() {
  const name = el("input", { type: "text", placeholder: "e.g. SHADE", "aria-label": "Production name", style: "width:100%" });
  const ok = await modal({ icon: "reel", title: "Start a production", body: [el("p", { class: "muted small" }, "It lives on this computer, and the people you invite connect to it here. It starts with a Production office, Heads of department and Cast channel."), el("label", { class: "f" }, "Name", name)], actions: [["Cancel", false], ["Start", true, true]] });
  if (!ok || !name.value.trim()) return;
  try { const r = await api.post("/api/room/productions", { name: name.value.trim() }); RM.prod = r.id; RM.space = "board"; location.hash = `#/room/${r.id}`; }
  catch (e) { toast("bad", "Couldn't create it", e.message); }
}

async function roomJoinAnother() {
  const link = el("input", { type: "text", placeholder: "Paste the invite link you were sent", "aria-label": "Invite link", style: "width:100%" });
  const ok = await modal({ icon: "door", title: "Join with an invite", body: [el("p", { class: "muted small" }, "Someone sent you a link to their production. An executive there checks three safety words with you before you get in."), el("label", { class: "f" }, "Invite link", link)], actions: [["Cancel", false], ["Join", true, true]] });
  if (!ok || !link.value.trim()) return;
  try { await api.post("/api/room/join", { invite: link.value.trim(), name: (RM.v && RM.v.me && RM.v.me.name) || "" }); location.hash = "#/room/joining"; }
  catch (e) { toast("bad", "Couldn't join", e.message); }
}

async function roomNewSpace() {
  const v = RM.v;
  const name = el("input", { type: "text", placeholder: "e.g. locations", "aria-label": "Space name", style: "width:100%" });
  const tiers = TIERS.filter(([t]) => t !== "producer").map(([t, l]) => [t, el("input", { type: "checkbox" }), l]);
  const depts = v.departments.map(d => [d.id, el("input", { type: "checkbox" }), d.name]);
  const ad = el("input", { type: "checkbox" });
  const ppl = v.people.filter(p => p.user !== v.me.user && p.tier !== "producer").map(p => [p.user, el("input", { type: "checkbox" }), `${p.name} (${p.tier_label})`]);
  const ok = await modal({ icon: "hash", title: "New space", body: [
    el("label", { class: "f" }, "Name", name),
    el("div", { class: "f", style: "margin-top:12px" }, el("span", {}, "Who can see it"), el("p", { class: "muted small" }, "Producers and executives always can. Everyone else needs to match a tier (and a department, if you pick one), or be added by name."),
      el("div", { class: "chk-list" }, tiers.map(([, b, l]) => el("label", { class: "chk" }, b, l)), el("label", { class: "chk" }, ad, "the 2nd AD"))),
    depts.length ? el("div", { class: "f", style: "margin-top:10px" }, el("span", {}, "Only these departments"), el("div", { class: "chk-list" }, depts.map(([, b, l]) => el("label", { class: "chk" }, b, l)))) : null,
    ppl.length ? el("details", { style: "margin-top:10px" }, el("summary", {}, "Add people by name (guests, for example)"), el("div", { class: "chk-list" }, ppl.map(([, b, l]) => el("label", { class: "chk" }, b, l)))) : null,
    el("div", { class: "row", style: "margin-top:12px" }, el("button", { type: "button", class: "btn sm quiet", onclick: async () => {
      const n = el("input", { type: "text", "aria-label": "Department name" });
      const ok2 = await modal({ icon: "users", title: "New department", body: [el("label", { class: "f" }, "Name", n)], actions: [["Cancel", false], ["Create", true, true]] });
      if (ok2 && n.value.trim()) { await api.post("/api/room/departments", { production: v.production, name: n.value.trim() }).then(() => toast("ok", "Department created", "It has its own channel. Open New space again to use it.")).catch(e => toast("bad", "Couldn't create it", e.message)); await roomLoad(); roomDraw(); }
    } }, icon("plus"), "New department (with its own channel)"))],
    actions: [["Cancel", false], ["Create", true, true]] });
  if (!ok || !name.value.trim()) return;
  try {
    const r = await api.post("/api/room/spaces", { production: v.production, name: name.value.trim(), tiers: tiers.filter(([, b]) => b.checked).map(([t]) => t),
      departments: depts.filter(([, b]) => b.checked).map(([d]) => d), second_ad: ad.checked, members: ppl.filter(([, b]) => b.checked).map(([u]) => u) });
    RM.space = r.id; RM.tab = "chat"; await roomOpen();
  } catch (e) { toast("bad", "Couldn't create it", e.message); }
}

/* ---------------- live: the Studio holds the connection to the hub; the page long-polls the Studio ---------------- */
async function roomLive() {
  const me = ++RM.loop;
  while (me === RM.loop && onRoom() && RM.v && RM.v.production) {
    let r;
    try { r = await api.get(`/api/room/wait?since=${RM.seq}`); } catch (e) { await new Promise(res => setTimeout(res, 5000)); continue; }
    if (me !== RM.loop || !onRoom()) return;
    if (r.seq !== RM.seq) {
      RM.seq = r.seq;
      const typing = document.activeElement && document.activeElement.matches("input, textarea") && document.activeElement.value;
      const keep = typing ? document.activeElement.value : null;
      await roomLoad().catch(() => null);
      /* only the Room's main page redraws itself; Members & access, call sheets and a meeting keep their own state */
      if (!/^#\/room(\/p_[^/]+(\/s_[^/]+)?)?$/.test(location.hash || "#/room")) { if (typeof voiceRefresh === "function") voiceRefresh(); continue; }
      if (!document.querySelector(".scrim")) {
        roomDraw();
        if (keep) { const i = document.querySelector(".composer input"); if (i) { i.value = keep; i.focus(); } }
      }
      buildNav("#/room");
    }
  }
}

/* ---------------- Members & access ---------------- */
async function roomAccess() {
  if (!RM.v) await roomLoad();
  const v = RM.v;
  roomTopbar();
  const a = await api.get(`/api/room/access?production=${encodeURIComponent(v.production)}`);
  const pend = el("div", { class: "pending" });
  const drawPending = list => put(pend, list.length ? list.map(p => el("div", { class: "pend-row" },
    el("span", { class: "av" }, (p.name || "?").split(/\s+/).map(x => x[0]).slice(0, 2).join("").toUpperCase()),
    el("div", { class: "pd" }, el("b", {}, p.name), el("div", { class: "muted small" }, [`Invited by ${p.invited_by}`, p.production, [p.tier, p.department].filter(Boolean).join(" · ")].filter(Boolean).join(" · "))),
    el("div", { class: "pw" }, el("div", { class: "lbl" }, "Safety words"),
      p.problem ? el("div", { class: "bad-text" }, p.problem) : p.words ? el("div", { class: "words sm" }, p.words.map(w => el("span", {}, w)))
        : p.checking && !p.mine ? el("div", { class: "muted small" }, "Another executive is checking this device.")
        : p.waiting_for_them ? el("div", { class: "muted small" }, "Waiting for their device…")
        : el("button", { type: "button", class: "btn sm", onclick: async () => { await api.post(`/api/room/pending/${p.device}/check`, {}).catch(e => toast("bad", "Couldn't start the check", e.message)); roomAccess(); } }, "Check")),
    el("div", { class: "pa" },
      el("button", { type: "button", class: "btn sm quiet", onclick: async () => { if (await modal({ icon: "x", title: "Decline this device?", body: ["The invite closes. They'll need a new one."], actions: [["Keep waiting", false], ["Decline", true, true]] })) { await api.post(`/api/room/pending/${p.device}/decline`, {}); roomAccess(); } } }, "Decline"),
      el("button", { type: "button", class: "btn sm primary", disabled: !p.words, onclick: async () => {
        if (!(await modal({ icon: "shield", title: `Approve ${p.name}?`, body: [el("div", { class: "words" }, p.words.map(w => el("span", {}, w))), "Only approve if they read you exactly these three words, in this order, on the call."], actions: [["Not yet", false], ["They match: approve", true, true]] }))) return;
        try { await api.post(`/api/room/pending/${p.device}/approve`, {}); toast("ok", `${p.name} is in`, "Their keys are being shared now."); RM.v = null; roomAccess(); } catch (e) { toast("bad", "Couldn't approve", e.message); }
      } }, "Approve"))))
    : el("p", { class: "muted small" }, "Nobody is waiting."));
  drawPending(a.pending);
  const tierPill = t => el("span", { class: "tier-dot t-" + t }, S_TIER(t));
  put(app(),
    el("div", { class: "acc-head" }, el("div", {}, el("h1", {}, `Who sees what on ${v.production_name}`),
      el("p", { class: "lede" }, "Each production has its own people, tiers and spaces: someone can be a key on one film and not appear on the next. Everyone joins by invite, and an executive approves each device. Tier and department decide which spaces and people they see; anything else is hidden, not just locked.")),
      el("div", { class: "row" }, el("a", { class: "btn quiet", href: `#/room/${v.production}` }, "Back to the Room"), el("button", { type: "button", class: "btn primary", onclick: () => roomInvite(a) }, icon("plus"), "Invite someone"))),
    a.can_approve ? el("section", { class: "card acc-sec" }, el("div", { class: "sec-h" }, el("h2", {}, "Waiting for your approval"), el("span", { class: "muted small" }, "Check the safety words with them on a call before approving.")), pend) : null,
    a.invites.length ? el("section", { class: "card acc-sec" }, el("h2", {}, "Invites not yet used"),
      el("ul", { class: "plain" }, a.invites.map(i => el("li", {}, el("span", {}, `${i.name} · ${i.tier} · ${i.status} · ${plural(i.days_left, "day")} left`))))) : null,
    el("section", { class: "acc-sec" }, el("h2", { class: "section-title" }, "Tiers"),
      el("div", { class: "tier-grid" }, a.tiers.map(t => el("article", { class: "card tier-card" }, el("div", { class: "th" }, el("span", { class: "tier-dot t-" + t.tier }), el("h3", {}, t.name), el("span", { class: "c" }, t.count)),
        el("p", {}, t.sees), el("p", { class: "small" }, el("b", {}, "Can reach: "), t.reach))))),
    el("div", { class: "acc-cols" },
      el("section", { class: "card acc-sec" }, el("h2", {}, "Members"),
        sideScroll(el("table", {}, el("thead", {}, el("tr", {}, ["Person", "Tier", "Department", "Spaces", "Devices", ""].map(h => el("th", { class: h === "Devices" ? "num" : null }, h)))),
          el("tbody", {}, a.members.map(m => el("tr", {}, el("td", {}, el("b", {}, m.name), m.role ? el("div", { class: "muted small" }, m.role) : null),
            el("td", {}, tierPill(m.tier)), el("td", {}, m.department || "—", m.second_ad ? el("div", { class: "muted small" }, "2nd AD") : null),
            el("td", { class: "small" }, m.tier === "executive" ? "Everything" : m.tier === "producer" ? "All of this production" : (m.spaces.join(", ") || "—")),
            el("td", { class: "num" }, m.devices),
            el("td", {}, a.is_exec && m.tier !== "executive" ? el("button", { type: "button", class: "btn sm quiet", onclick: () => roomEditMember(a, m) }, "Edit") : null))))))),
      el("aside", { class: "stack" },
        el("section", { class: "card acc-sec" }, el("div", { class: "sec-h" }, el("h2", {}, "Extra contact grants"), a.is_exec ? el("button", { type: "button", class: "btn sm", onclick: () => roomGrant(a) }, "Add") : null),
          el("p", { class: "muted small" }, "People follow the org chart by default. A grant opens a line between two people outside it."),
          a.grants.length ? el("ul", { class: "plain grants" }, a.grants.map(g => el("li", {}, el("div", {}, el("b", {}, g.pair), el("div", { class: "muted small" }, g.by)),
            a.is_exec ? el("button", { type: "button", class: "btn sm quiet", "aria-label": "Revoke", onclick: async () => { await api.post(`/api/room/grants/${g.id}/revoke`, {}); roomAccess(); } }, icon("x")) : null))) : el("p", { class: "small muted" }, "None.")),
        el("section", { class: "card acc-sec" }, el("h2", {}, "Oversight notice"), el("p", {}, `“${a.oversight}”`),
          el("p", { class: "muted small" }, "Shown to each person when they join, and again before their first private message.")))),
    a.audit ? el("section", { class: "card acc-sec" }, el("div", { class: "sec-h" }, el("h2", {}, "Audit log"),
      el("span", { class: "muted small" }, a.audit.intact ? "Executives only. Covers every production. Entries can't be edited or deleted." : "Warning: the log's chain doesn't check out. Tell the person who runs the Room's server."),
      el("button", { type: "button", class: "btn sm quiet", onclick: () => roomExportAudit(a.audit.entries) }, icon("download"), "Export")),
      el("div", { class: "audit" }, a.audit.entries.slice(0, 120).map(e => el("div", { class: "au" }, el("span", { class: "wh" }, new Date(e.when * 1000).toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })),
        el("span", { class: "wt" }, e.what), el("span", { class: "k k-" + e.kind }, e.kind))))) : null,
    a.is_exec ? el("section", { class: "acc-sec" }, el("button", { type: "button", class: "btn quiet", onclick: async () => {
      const arch = !v.archived;
      if (!(await modal({ icon: "alert", title: arch ? `Archive ${v.production_name}?` : `Restore ${v.production_name}?`, body: [arch ? "Nobody can post in it any more. Its Room data is deleted 90 days after archiving." : "People can post in it again."], actions: [["Cancel", false], [arch ? "Archive" : "Restore", true, true]] }))) return;
      await api.post(`/api/room/productions/${v.production}/archive`, { archived: arch }).catch(e => toast("bad", "Couldn't do that", e.message)); RM.v = null; roomAccess();
    } }, v.archived ? "Restore this production" : "Archive this production")) : null);
  const tick = async () => { if (!(location.hash || "").startsWith("#/room/access")) return;
    try { const b2 = await api.get(`/api/room/access?production=${encodeURIComponent(v.production)}`); if (JSON.stringify(b2.pending) !== JSON.stringify(a.pending)) { a.pending = b2.pending; drawPending(b2.pending); } } catch (e) { /* hub busy */ }
    setTimeout(tick, 2500); };
  setTimeout(tick, 2500);
}
const S_TIER = t => ({ executive: "Executive", producer: "Producer", key: "Key personnel", crew: "Crew", cast: "Cast", guest: "Guest" })[t] || t;

async function roomInvite(a) {
  const v = RM.v;
  const name = el("input", { type: "text", "aria-label": "Name", style: "width:100%" });
  const role = el("input", { type: "text", placeholder: "e.g. Director of Photography", "aria-label": "Role", style: "width:100%" });
  const tier = el("select", { "aria-label": "Tier" }, TIERS.filter(([t]) => v.is_exec || t !== "producer").map(([t, l]) => el("option", { value: t, selected: t === "crew" }, l)));
  const dept = el("select", { "aria-label": "Department" }, el("option", { value: "" }, "None"), a.departments.map(d => el("option", { value: d.id }, d.name)));
  const ad = el("input", { type: "checkbox" });
  const ok = await modal({ icon: "users", title: `Invite someone to ${v.production_name}`, body: [
    el("label", { class: "f" }, "Name", name), el("label", { class: "f", style: "margin-top:10px" }, "Role", role),
    el("div", { class: "row", style: "margin-top:10px" }, el("label", { class: "f" }, "Tier", tier), el("label", { class: "f" }, "Department", dept), el("label", { class: "chk" }, ad, "2nd AD")),
    el("p", { class: "muted small" }, v.is_exec ? "You'll check their safety words when they join." : "An executive checks their safety words and approves them.")],
    actions: [["Cancel", false], ["Create invite", true, true]] });
  if (!ok) return;
  try {
    const r = await api.post("/api/room/invite", { production: v.production, name: name.value.trim(), role: role.value.trim(), tier: tier.value, department: dept.value, second_ad: ad.checked });
    /* 1.1.7: the invite as a QR code, for the Saracen Bridge iPhone app's scanner (or the phone's camera) */
    let qr = null;
    try { const q = qrcode(0, "M"); q.addData(r.link); q.make(); qr = el("div", { class: "invite-qr", "aria-label": "QR code of the invite link" }); qr.innerHTML = q.createSvgTag({ cellSize: 5, margin: 3, scalable: true }); } catch (e) { qr = null; }
    await modal({ icon: "check", title: "Send them this link", body: [el("div", { class: "invite-link" }, el("code", {}, r.link), copyBtn(r.link)),
      qr ? el("div", { class: "invite-qr-wrap" }, qr, el("p", { class: "muted small" }, "Or, with them here: they scan this in the Saracen Bridge app (Join with an invite, Scan the QR code).")) : null,
      `On a phone it opens the Room (in the Saracen Bridge app, or the browser); on a computer, they paste it into the Studio's Room page. It works once and expires in ${r.expires_in_days} days.`,
      "Send it however you like (text, email). It isn't a secret on its own: nobody gets in until the safety words match."], actions: [["Done", true, true]] });
    roomAccess();
  } catch (e) { toast("bad", "Couldn't create the invite", e.message); }
}

async function roomEditMember(a, m) {
  const v = RM.v;
  const name = el("input", { type: "text", value: m.name, "aria-label": "Name", style: "width:100%" });
  const role = el("input", { type: "text", value: m.role, "aria-label": "Role", style: "width:100%" });
  const tier = el("select", { "aria-label": "Tier" }, TIERS.map(([t, l]) => el("option", { value: t, selected: t === m.tier }, l)));
  const dept = el("select", { "aria-label": "Department" }, el("option", { value: "" }, "None"), a.departments.map(d => el("option", { value: d.id, selected: d.id === m.department_id }, d.name)));
  const ad = el("input", { type: "checkbox", checked: m.second_ad });
  const choice = await modal({ icon: "users", title: `Edit ${m.name}`, body: [
    el("label", { class: "f" }, "Name", name), el("label", { class: "f", style: "margin-top:10px" }, "Role", role),
    el("div", { class: "row", style: "margin-top:10px" }, el("label", { class: "f" }, "Tier", tier), el("label", { class: "f" }, "Department", dept), el("label", { class: "chk" }, ad, "2nd AD")),
    el("p", { class: "muted small" }, `${plural(m.devices, "device")}. Changing someone's tier or removing them gives the spaces they lose new keys, so they can't read anything new there.`)],
    actions: [["Cancel", null], ["Remove from production", "remove"], m.devices ? ["Remove a device…", "device"] : null, ["Make executive", "exec"], ["Save", "save", true]].filter(Boolean) });
  try {
    if (choice === "save") await api.post("/api/room/members/set", { production: v.production, user: m.user, tier: tier.value, department: dept.value, second_ad: ad.checked, name: name.value, role: role.value });
    if (choice === "remove" && await modal({ icon: "alert", title: `Remove ${m.name} from ${v.production_name}?`, body: ["They stop seeing this production at once, and its spaces get new keys."], actions: [["Cancel", false], ["Remove", true, true]] }))
      await api.post("/api/room/members/remove", { production: v.production, user: m.user });
    if (choice === "device") {
      const pick = await modal({ icon: "alert", title: "Remove which device?", body: ["The device stops working at once, and every space it could read gets new keys."], actions: [["Cancel", null], ...m.device_ids.map((d, i) => [`Device ${i + 1} (${d.slice(2, 8)})`, d])] });
      if (pick) await api.post(`/api/room/devices/${pick}/remove`, {});
    }
    if (choice === "exec" && await modal({ icon: "shield", title: `Make ${m.name} an executive?`, body: ["Executives see every production, space, file and private message, approve devices and read the audit log."], actions: [["Cancel", false], ["Make executive", true, true]] }))
      await api.post("/api/room/execs", { user: m.user, on: true });
    if (choice) { RM.v = null; roomAccess(); }
  } catch (e) { toast("bad", "Couldn't save", e.message); }
}

async function roomGrant(a) {
  const opts = a.members.filter(m => m.tier !== "executive").map(m => el("option", { value: m.user }, `${m.name} (${S_TIER(m.tier)})`));
  const p1 = el("select", { "aria-label": "First person" }, opts.map(o => o.cloneNode(true)));
  const p2 = el("select", { "aria-label": "Second person" }, opts.map(o => o.cloneNode(true)));
  if (p2.options.length > 1) p2.selectedIndex = 1;
  const ok = await modal({ icon: "users", title: "Open a line between two people", body: [el("div", { class: "row" }, el("label", { class: "f" }, "Person", p1), el("label", { class: "f" }, "and", p2)), el("p", { class: "muted small" }, "They can then message each other privately. The grant is recorded in the audit log.")], actions: [["Cancel", false], ["Grant", true, true]] });
  if (!ok || p1.value === p2.value) return;
  try { await api.post("/api/room/grants", { production: RM.v.production, a: p1.value, b: p2.value }); roomAccess(); } catch (e) { toast("bad", "Couldn't grant it", e.message); }
}

function roomExportAudit(entries) {
  const csv = ["When,What,Kind", ...entries.map(e => [new Date(e.when * 1000).toISOString(), e.what, e.kind].map(x => `"${String(x).replace(/"/g, '""')}"`).join(","))].join("\r\n");
  const a = el("a", { href: URL.createObjectURL(new Blob([csv], { type: "text/csv" })), download: "room_audit_log.csv" });
  document.body.append(a); a.click(); a.remove();
}
