"use strict";
/* Call sheets in the Room (1.0.8): the strip on the board, each person's own day, "Got it", reminders, and the
   producers' editor (day facts, scenes, per-person times typed or from CSV, the PDF, publish as a new version). */

function callsheetStrip(cs) {
  const v = RM.v;
  const mine = cs.my_row || {};
  const myTime = mine.pickup ? ["pickup", mine.pickup] : mine.call ? ["your call", mine.call] : null;
  return el("article", { class: "cs-strip", "aria-label": "Today's call sheet" },
    el("div", { class: "cs-a" }, el("div", { class: "lbl" }, `Call sheet · ${cs.day}${cs.date ? " · " + dateOnly(cs.date) : ""}`),
      el("div", { class: "big" }, myTime && !cs.can_remind ? myTime[1] : cs.unit_call),
      el("div", { class: "sub" }, myTime && !cs.can_remind ? `${myTime[0]} · unit call ${cs.unit_call} · v${cs.version}` : `unit call · v${cs.version} · posted ${when(cs.posted)}`)),
    el("div", { class: "cs-b" }, el("div", { class: "lbl" }, "Location"), el("div", {}, cs.location || "—", cs.weather_cover ? el("span", { class: "muted" }, ` · weather cover: ${cs.weather_cover}`) : null),
      el("div", { class: "lbl", style: "margin-top:8px" }, "Scenes"), el("div", {}, (cs.scenes || []).map(s => s.no).filter(Boolean).join(", ") || "—")),
    cs.can_remind ? el("div", { class: "cs-c" }, el("div", { class: "lbl" }, "Confirmed"), el("div", { class: "big" }, `${cs.confirmed} / ${cs.expected}`), el("div", { class: "sub" }, "tapped “Got it”"))
      : cs.on_sheet ? el("div", { class: "cs-c" }, el("div", { class: "lbl" }, "You"), cs.me_confirmed ? el("div", { class: "ok-text" }, icon("check"), " Confirmed") : el("div", { class: "sub" }, "Let the production office know you've seen this version.")) : null,
    el("div", { class: "cs-d" },
      el("button", { type: "button", class: "btn sm", onclick: () => callsheetOpen(cs) }, "Open call sheet"),
      cs.on_sheet && !cs.me_confirmed ? el("button", { type: "button", class: "btn sm primary", onclick: () => callsheetConfirm(cs) }, "Got it") : null,
      cs.can_remind && cs.expected > cs.confirmed ? el("button", { type: "button", class: "btn sm", onclick: async () => {
        try { const r = await api.post(`/api/room/callsheets/item/${cs.item}/remind`, {}); toast("ok", `Reminded ${plural(r.reminded, "person", "people")}`); } catch (e) { toast("bad", "Couldn't send reminders", e.message); }
      } }, `Remind the ${cs.expected - cs.confirmed} who haven't`) : null,
      cs.can_remind && v && !v.archived ? el("a", { class: "btn sm quiet", href: `#/room/callsheet/${cs.lineage}` }, "New version") : null));
}

async function callsheetConfirm(cs) {
  try { await api.post(`/api/room/callsheets/item/${cs.item}/confirm`, {}); toast("ok", "Confirmed", "The production office can see you've got it."); await roomLoad(); roomDraw(); }
  catch (e) { toast("bad", "Couldn't confirm", e.message); }
}

function callsheetRows(cs) {
  const row = cs.my_row;
  if (!row) return null;
  const steps = [["Pickup", row.pickup, row.driver ? `Driver: ${row.driver}` : "", row.pickup_address], ["Hair and make-up", row.hmu], ["Costume", row.costume], ["On set", row.on_set], ["Your call", row.call]]
    .filter(s => s[1]);
  return el("div", { class: "cs-mine" }, el("div", { class: "lbl" }, "Your day"),
    steps.map(([what, t, extra, addr]) => el("div", { class: "cs-step" }, el("span", { class: "t" }, t), el("span", {}, el("b", {}, what), extra ? el("small", {}, extra) : null, addr ? el("small", {}, addr) : null))),
    row.character ? el("p", { class: "small muted" }, `Character: ${row.character}`) : null, row.scenes ? el("p", { class: "small muted" }, `Your scenes: ${row.scenes}`) : null,
    row.notes ? el("p", { class: "small" }, row.notes) : null,
    el("p", { class: "muted small" }, "Only you and the production office see your pickup details."));
}

async function callsheetOpen(cs) {
  const body = [
    el("div", { class: "cs-facts" }, facts([["Day", `${cs.day}${cs.date ? " · " + dateOnly(cs.date) : ""}`], ["Unit call", cs.unit_call], ["Version", `v${cs.version}`],
      ["Location", cs.location], ["Weather cover", cs.weather_cover], ["Base and parking", cs.base], ["Nearest hospital", cs.hospital]])),
    callsheetRows(cs),
    (cs.scenes || []).length ? table(["Scene", "Set", "Pages", "Note"], el("tbody", {}, cs.scenes.map(s => el("tr", {}, el("td", { class: "mono" }, s.no), el("td", {}, s.slug), el("td", {}, s.pages), el("td", {}, s.note))))) : null,
    cs.notes ? el("p", { style: "white-space:pre-wrap" }, cs.notes) : null,
    cs.pdf ? el("p", {}, el("a", { class: "fchip", href: `/api/room/file/${cs.pdf.id}`, download: cs.pdf.name }, icon("file"), cs.pdf.name, el("small", {}, bytes(cs.pdf.size)))) : null,
    cs.people ? el("details", {}, el("summary", {}, `Everyone on it (${cs.confirmed} of ${cs.expected} confirmed)`),
      table(["Person", "Call", "Pickup", "H&MU", "Costume", "On set", ""], el("tbody", {}, cs.people.map(p => el("tr", {}, el("td", {}, p.name, el("div", { class: "muted small" }, p.tier)),
        el("td", {}, p.call || ""), el("td", {}, p.pickup || ""), el("td", {}, p.hmu || ""), el("td", {}, p.costume || ""), el("td", {}, p.on_set || ""),
        el("td", {}, p.confirmed ? el("span", { class: "pill PASS" }, "Got it") : el("span", { class: "muted small" }, "Not yet"))))))) : null];
  const act = await modal({ icon: "doc", title: `Call sheet · ${cs.day}`, body, actions: [cs.on_sheet && !cs.me_confirmed ? ["Got it", "confirm", true] : null, ["Close", null, !(cs.on_sheet && !cs.me_confirmed)]].filter(Boolean) });
  if (act === "confirm") callsheetConfirm(cs);
}

/* ---------------- the producers' editor ---------------- */
async function callsheetEditor(lineage) {
  if (!RM.v) await roomLoad();
  const v = RM.v;
  roomTopbar();
  if (!v.can_manage) { put(app(), errBox({ message: "Only producers and executives publish call sheets." })); return; }
  const list = await api.get(`/api/room/callsheets?production=${encodeURIComponent(v.production)}`).catch(() => []);
  let base = null;
  if (lineage) base = await api.get(`/api/room/callsheets/${lineage}?production=${encodeURIComponent(v.production)}`).catch(() => null);
  const f = k => el("input", { type: k === "date" ? "date" : "text", value: base ? base[k] || "" : "", "aria-label": k });
  const day = f("day"), date = f("date"), unit = f("unit_call"), loc = f("location"), wc = f("weather_cover"), basef = f("base"), hosp = f("hospital");
  day.placeholder = "Day 12"; unit.placeholder = "06:30"; loc.placeholder = "Quarry, Northfield"; wc.placeholder = "Stage B"; hosp.placeholder = "Name and address";
  [loc, wc, basef, hosp].forEach(x => x.style.width = "100%");
  const notes = el("textarea", { rows: 3, style: "width:100%;height:auto;padding:10px 12px", "aria-label": "Notes" }, base ? base.notes || "" : "");
  const scenes = base ? (base.scenes || []).map(s => ({ ...s })) : [];
  const ppl = v.people.filter(p => p.tier !== "executive");
  const rows = base ? base.rows.map(r => ({ ...r })) : [];
  const rowsBox = el("div", {});
  const isCast = u => (ppl.find(p => p.user === u) || {}).tier === "cast";
  const drawRows = () => put(rowsBox, sideScroll(el("table", { class: "cs-edit" },
    el("thead", {}, el("tr", {}, ["Person", "Call", "Pickup", "Pickup address", "Driver", "H&MU", "Costume", "On set", ""].map(h => el("th", {}, h)))),
    el("tbody", {}, rows.length ? rows.map((r, i) => el("tr", {},
      el("td", {}, el("select", { "aria-label": "Person", onchange: e => { r.user = e.target.value; drawRows(); } }, el("option", { value: "" }, "Pick someone"),
        ppl.map(p => el("option", { value: p.user, selected: p.user === r.user }, `${p.name} (${p.tier_label}${p.department ? ", " + p.department : ""})`)))),
      ["call", "pickup", "pickup_address", "driver", "hmu", "costume", "on_set"].map(k => {
        const inp = el("input", { type: "text", value: r[k] || "", "aria-label": k, placeholder: k === "pickup_address" ? "Address" : k === "driver" ? "Name" : isCast(r.user) === (k !== "call") ? "00:00" : "",
          style: `width:${k === "pickup_address" ? 180 : k === "driver" ? 110 : 70}px` });
        inp.addEventListener("change", () => r[k] = inp.value);
        return el("td", {}, inp);
      }),
      el("td", {}, el("button", { type: "button", class: "btn quiet sm", "aria-label": "Remove", onclick: () => { rows.splice(i, 1); drawRows(); } }, icon("x"))))) :
      el("tr", {}, el("td", { colspan: 9, class: "muted small" }, "Add the people on this call sheet."))))));
  drawRows();
  const csv = el("input", { type: "file", accept: ".csv,text/csv", hidden: true, onchange: async () => {
    const file = csv.files[0]; if (!file) return;
    try {
      const r = await api.post("/api/room/callsheets/csv", { production: v.production, text: await file.text() });
      r.rows.forEach(nr => { const ex = rows.find(x => x.user === nr.user); ex ? Object.assign(ex, nr) : rows.push(nr); });
      drawRows();
      toast(r.unknown.length ? "info" : "ok", `${plural(r.rows.length, "person", "people")} filled in`, r.unknown.length ? `Not found in the Room: ${r.unknown.join(", ")}` : null);
    } catch (e) { toast("bad", "Couldn't read the CSV", e.message); }
    csv.value = "";
  } });
  const pdf = el("input", { type: "file", accept: "application/pdf", "aria-label": "Call sheet PDF" });
  const next = base ? base.version + 1 : 1;
  const publish = async ev => {
    const btn = ev.currentTarget; btn.disabled = true;
    try {
      let pdfFile = base && base.pdf && !pdf.files[0] ? base.pdf : null;
      if (pdf.files[0]) { const fd = new FormData(); fd.append("production", v.production); fd.append("file", pdf.files[0]); pdfFile = await api.form("/api/room/callsheets/pdf", fd); }
      const r = await api.post("/api/room/callsheets", { production: v.production, lineage: base ? base.lineage : null, day: day.value, date: date.value, unit_call: unit.value,
        location: loc.value, weather_cover: wc.value, base: basef.value, hospital: hosp.value, notes: notes.value, scenes, rows: rows.filter(r => r.user), pdf: pdfFile });
      toast("ok", `Published version ${r.version}`, "Everyone on it is notified.");
      location.hash = `#/room/${v.production}`;
    } catch (e) { toast("bad", "Not published", e.message); btn.disabled = false; }
  };
  put(app(),
    el("div", { class: "acc-head" }, el("div", {}, el("h1", {}, base ? `${base.day}: new version` : "Call sheets"),
      el("p", { class: "lede" }, "Publish the day's call sheet. Everyone on it gets their own times on their phone and taps Got it. A new version notifies them again and starts the count from zero.")),
      el("a", { class: "btn quiet", href: `#/room/${v.production}` }, "Back to the Room")),
    !base && list.length ? el("section", { class: "card acc-sec" }, el("h2", {}, "Published"),
      el("div", { class: "list" }, list.map(s => el("a", { href: `#/room/callsheet/${s.lineage}` }, el("span", {}, el("span", { class: "ttl" }, `${s.day}${s.date ? " · " + dateOnly(s.date) : ""}`), el("span", { class: "meta" }, `v${s.version} · unit call ${s.unit_call} · ${s.location}`)),
        el("span", { class: "when" }, `${s.confirmed} / ${s.expected} confirmed`))))) : null,
    el("section", { class: "card acc-sec" }, el("h2", {}, base ? `Version ${next}` : "New call sheet"),
      el("div", { class: "row" }, el("label", { class: "f" }, "Day", day), el("label", { class: "f" }, "Date", date), el("label", { class: "f" }, "Unit call", unit)),
      el("div", { class: "cs-grid" }, el("label", { class: "f" }, "Location", loc), el("label", { class: "f" }, "Weather cover", wc), el("label", { class: "f" }, "Base and parking", basef), el("label", { class: "f" }, "Nearest hospital", hosp)),
      el("h2", { style: "margin-top:22px" }, "Scenes"),
      editTable([{ key: "no", label: "Scene", width: 70 }, { key: "slug", label: "Set", width: 260 }, { key: "pages", label: "Pages", width: 70 }, { key: "note", label: "Note", width: 220 }], scenes, { addLabel: "Add a scene", empty: "No scenes yet." }),
      el("label", { class: "f", style: "margin-top:18px" }, "Notes for everyone", notes),
      el("div", { class: "sec-h", style: "margin-top:22px" }, el("h2", {}, "People and times"),
        el("span", { class: "muted small" }, "Crew get a call time. Cast get pickup, hair and make-up, costume and on set. Pickup addresses and drivers go only to that person and the production office.")),
      rowsBox,
      el("div", { class: "row", style: "margin-top:10px" },
        el("button", { type: "button", class: "btn sm", onclick: () => { rows.push({}); drawRows(); } }, icon("plus"), "Add a person"),
        el("button", { type: "button", class: "btn sm quiet", onclick: () => { ppl.filter(p => !rows.some(r => r.user === p.user) && p.tier !== "guest" && p.tier !== "producer").forEach(p => rows.push({ user: p.user })); drawRows(); } }, "Add everyone on the production"),
        el("button", { type: "button", class: "btn sm quiet", onclick: () => csv.click() }, icon("upload"), "Fill times from a CSV"), csv),
      el("p", { class: "muted small" }, "CSV: a header row with Name, then any of Call, Pickup, Pickup address, Driver, H&MU, Costume, On set, Character, Scenes, Notes. Names must match the Room."),
      el("label", { class: "f", style: "margin-top:16px" }, base && base.pdf ? `Call sheet PDF (now: ${base.pdf.name}; pick a file to replace it)` : "Call sheet PDF (optional)", pdf),
      el("div", { class: "row", style: "margin-top:22px" }, el("button", { type: "button", class: "btn primary", onclick: publish }, `Publish ${base ? "version " + next : "call sheet"}`))));
}
