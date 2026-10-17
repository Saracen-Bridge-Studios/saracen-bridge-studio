"use strict";
/* Voice huddles and meetings in the Room (1.0.8), on LiveKit with end-to-end encryption.
   The system default microphone is used automatically and followed when it changes; noise suppression and echo
   cancelling are on. Speaking is shown by a steady gold ring (never a pulse). Executives decide who is on stage in
   a meeting; everyone else watches and can raise a hand. If this window can't do end-to-end encryption, the meeting
   is blocked with a plain message: encryption is never silently dropped. */

const MEET = { room: null, info: null, onStage: false, muted: false, speaking: new Set(), hands: new Set(), chat: [], meter: null, mic: "", devTimer: null };
const LK = () => window.LivekitClient;
const nameOf = u => { const p = (RM.v && RM.v.people || []).find(x => x.user === u); return p ? p.name : (RM.v && RM.v.me.user === u ? RM.v.me.name : "Someone"); };
const initialsOf = u => nameOf(u).split(/\s+/).map(x => x[0]).slice(0, 2).join("").toUpperCase();

async function micLabel() {
  try {
    const ds = (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === "audioinput");
    const d = ds.find(x => x.deviceId === "default") || ds[0];
    MEET.mic = d ? (d.label ? d.label.replace(/^Default - /, "") + " (system default)" : "System default microphone") : "";
  } catch (e) { MEET.mic = ""; }
  return MEET.mic;
}
if (navigator.mediaDevices && navigator.mediaDevices.addEventListener) {
  navigator.mediaDevices.addEventListener("devicechange", () => {           /* a newly plugged-in mic or earbuds take over */
    clearTimeout(MEET.devTimer);
    MEET.devTimer = setTimeout(async () => {
      await micLabel();
      if (MEET.room && MEET.onStage) { try { await MEET.room.switchActiveDevice("audioinput", "default"); toast("info", "Microphone switched", MEET.mic); } catch (e) { /* keep the old one */ } meterStart(); }
      voiceRefresh();
    }, 400);
  });
}

function voicePanel(v, sv) {
  const box = el("section", { class: "card voice", "aria-labelledby": "voice-h" });
  MEET.panel = box;
  voiceDraw(box, v, sv);
  return box;
}
function voiceRefresh() { if (MEET.panel && document.body.contains(MEET.panel)) voiceDraw(MEET.panel, RM.v, RM.sv); }

function voiceDraw(box, v, sv) {
  const inCall = !!MEET.room;
  const space = sv && !sv.locked_oversight && (sv.kind === "channel" || sv.kind === "dm") && sv.member ? sv : null;
  const label = inCall ? (MEET.info.kind === "meeting" ? MEET.info.title : `${MEET.spaceName || "huddle"}`) : space ? `${space.kind === "dm" ? space.name : "# " + space.name} huddle` : "";
  const people = inCall ? [...MEET.room.remoteParticipants.values()].map(p => p.identity).concat(MEET.room.localParticipant.identity) : [];
  put(box,
    el("div", { class: "vh" }, el("h2", { id: "voice-h" }, "Voice"), label ? el("span", { class: "vr" }, label) : null),
    inCall ? el("ul", { class: "plain talkers" }, people.map(u => el("li", { class: MEET.speaking.has(u) ? "speaking" : "" },
      el("span", { class: "av sm" }, initialsOf(u)), el("span", { class: "pn" }, nameOf(u) + (u === v.me.user ? " (you)" : ""),
        el("small", {}, MEET.speaking.has(u) ? "Speaking" : u === v.me.user && MEET.muted ? "Muted" : "Listening")))))
      : el("p", { class: "muted small" }, space ? "One click to talk with the people in this space." : "Open a channel or a conversation to start a huddle there."),
    el("div", { class: "mic" },
      el("div", { class: "mic-h" }, el("span", { class: "dot ok" }), el("b", {}, "Microphone"), el("span", { class: "muted small" }, "automatic")),
      el("div", { class: "small" }, MEET.mic || "The system default microphone"),
      inCall && MEET.onStage ? el("div", { class: "meter", role: "img", "aria-label": "Microphone level" }, Array.from({ length: 16 }, () => el("span"))) : null,
      el("div", { class: "muted small" }, "Noise suppression and echo cancelling are on. Plug in another mic and it switches automatically.")),
    el("div", { class: "row vb" },
      inCall ? el("button", { type: "button", class: "btn", onclick: meetLeave }, "Leave")
        : space ? el("button", { type: "button", class: "btn primary", onclick: () => huddleJoin(space) }, icon("mic"), "Join huddle") : null,
      inCall && MEET.onStage ? el("button", { type: "button", class: "btn", "aria-pressed": String(MEET.muted), onclick: meetMute }, icon(MEET.muted ? "micoff" : "mic"), MEET.muted ? "Unmute" : "Mute") : null,
      inCall && MEET.info.kind === "meeting" ? el("a", { class: "btn quiet", href: `#/room/meet/${MEET.info.meeting}` }, "Open the meeting") : null),
    !inCall && RM.space === "board" ? meetingsList(v) : null);
  if (inCall && MEET.onStage) meterStart();
}

function meetingsList(v) {
  const box = el("div", { class: "meet-list" }, el("div", { class: "muted small" }, "Loading meetings…"));
  api.get(`/api/room/meetings?production=${encodeURIComponent(v.production)}`).then(list => {
    const ms = list.filter(m => m.kind === "meeting");
    put(box, el("div", { class: "lbl" }, "Meetings"),
      ms.length ? ms.map(m => el("div", { class: "meet-row" }, el("div", {}, el("b", {}, m.title),
        el("div", { class: "muted small" }, m.starts ? new Date(m.starts).toLocaleString("en-GB", { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) : "Now")),
        el("div", { class: "row" }, el("button", { type: "button", class: "btn sm primary", onclick: () => meetingJoin(m.id) }, "Join"),
          m.starts ? el("a", { class: "btn sm quiet", href: `/api/room/meetings/${m.id}/ics?production=${encodeURIComponent(v.production)}`, download: "meeting.ics" }, "Add to calendar") : null)))
        : el("p", { class: "muted small" }, "No meetings scheduled."),
      v.can_manage && !v.archived ? el("button", { type: "button", class: "btn sm", onclick: meetingSchedule }, icon("plus"), "Schedule a meeting") : null);
  }).catch(() => put(box));
  return box;
}

async function micConsent() {
  let ok = false;
  try { ok = localStorage.getItem("room-mic-ok") === "1"; } catch (e) { /* private window */ }
  if (ok) return true;
  const yes = await modal({ icon: "mic", title: "Use your microphone?", body: ["Huddles and meetings use your microphone. The Studio picks the system default automatically and follows it if you plug in another.",
    "Next, Windows or the browser asks you once to allow it."], actions: [["Not now", false], ["Continue", true, true]] });
  if (yes) try { localStorage.setItem("room-mic-ok", "1"); } catch (e) { /* private window */ }
  return !!yes;
}

async function huddleJoin(space) {
  if (!(await micConsent())) return;
  try { const info = await api.post("/api/room/huddle", { space: space.id }); MEET.spaceName = `${space.kind === "dm" ? space.name : "# " + space.name} huddle`; await meetConnect(info); }
  catch (e) { toast("bad", "Couldn't join", e.message); }
}

async function meetingJoin(mid) {
  location.hash = `#/room/meet/${mid}`;
}

async function meetConnect(info) {
  const L = LK();
  if (!L) throw new Error("The meeting software didn't load. Restart the Studio.");
  if (!L.isE2EESupported()) {
    await modal({ icon: "lock", title: "This window can't encrypt calls", body: ["The Room only holds calls with end-to-end encryption, and this window doesn't support it. Open the Studio in Microsoft Edge or Chrome and join from there."], actions: [["OK", true, true]] });
    throw new Error("End-to-end encryption isn't available in this window, so the call wasn't joined.");
  }
  if (MEET.room) await meetLeave();
  const keyProvider = new L.ExternalE2EEKeyProvider();
  const raw = Uint8Array.from(atob(info.key.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - info.key.length % 4) % 4)), c => c.charCodeAt(0));
  await keyProvider.setKey(raw.buffer);
  const room = new L.Room({ adaptiveStream: true, dynacast: true,
    encryption: { keyProvider, worker: new Worker("/ui/vendor/livekit-client.e2ee.worker.js") },
    audioCaptureDefaults: { deviceId: "default", noiseSuppression: true, echoCancellation: true, autoGainControl: true } });
  MEET.room = room; MEET.info = info; MEET.onStage = info.on_stage; MEET.muted = false; MEET.speaking = new Set(); MEET.hands = new Set(); MEET.chat = [];
  const E = L.RoomEvent;
  const sink = document.getElementById("meet-audio") || document.body.appendChild(el("div", { id: "meet-audio", hidden: true }));
  room.on(E.TrackSubscribed, (track, pub, p) => { if (track.kind === "audio") sink.append(track.attach()); else meetPaint(); })
    .on(E.TrackUnsubscribed, track => { track.detach().forEach(n => n.remove()); meetPaint(); })
    .on(E.ActiveSpeakersChanged, sp => { MEET.speaking = new Set(sp.map(p => p.identity)); meetPaint(); })
    .on(E.ParticipantConnected, meetPaint).on(E.ParticipantDisconnected, meetPaint)
    .on(E.ParticipantAttributesChanged, (changed, p) => { (p.attributes && p.attributes.hand === "up") ? MEET.hands.add(p.identity) : MEET.hands.delete(p.identity); meetPaint(); })
    .on(E.ParticipantPermissionsChanged, async (prev, p) => {
      if (p !== room.localParticipant) return;
      const can = !!(p.permissions && p.permissions.canPublish);
      if (can && !MEET.onStage) { MEET.onStage = true; await room.localParticipant.setAttributes({ hand: "" }).catch(() => null); await room.localParticipant.setMicrophoneEnabled(true).catch(() => null); toast("ok", "You're on stage", "Your microphone is on."); }
      if (!can && MEET.onStage) { MEET.onStage = false; meterStop(); toast("info", "You're watching again"); }
      meetPaint();
    })
    .on(E.DataReceived, (payload, p, kind, topic) => { if (topic === "chat") { try { MEET.chat.push({ who: p ? p.identity : "", text: new TextDecoder().decode(payload), ts: Date.now() / 1000 }); meetPaint(); } catch (e) { /* ignore */ } } })
    .on(E.EncryptionError, () => toast("bad", "Encryption problem", "Some audio or video couldn't be decrypted."))
    .on(E.Disconnected, () => { meterStop(); MEET.room = null; meetPaint(); voiceRefresh(); });
  await room.setE2EEEnabled(true);
  await room.connect(info.url, info.token);
  await micLabel();
  if (MEET.onStage) await room.localParticipant.setMicrophoneEnabled(true);
  meetPaint(); voiceRefresh();
}

async function meetLeave() { const r = MEET.room; MEET.room = null; meterStop(); if (r) await r.disconnect().catch(() => null); document.getElementById("meet-audio")?.replaceChildren(); voiceRefresh(); meetPaint(); }
async function meetMute() { if (!MEET.room) return; MEET.muted = !MEET.muted; await MEET.room.localParticipant.setMicrophoneEnabled(!MEET.muted).catch(() => null); voiceRefresh(); meetPaint(); }

/* level meter: smoothed, ~15 updates a second, a static reading under reduced motion */
function meterStart() {
  meterStop();
  const pub = MEET.room && [...MEET.room.localParticipant.audioTrackPublications.values()][0];
  const mst = pub && pub.track && pub.track.mediaStreamTrack;
  if (!mst) return setTimeout(() => MEET.room && MEET.onStage && !MEET.meter && meterStart(), 500);
  const ctx = new AudioContext(); const an = ctx.createAnalyser(); an.fftSize = 512;
  ctx.createMediaStreamSource(new MediaStream([mst])).connect(an);
  const buf = new Uint8Array(an.fftSize); let level = 0, last = 0;
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const tick = t => {
    if (!MEET.meter) return;
    MEET.meter.raf = requestAnimationFrame(tick);
    if (t - last < (calm ? 500 : 66)) return; last = t;
    an.getByteTimeDomainData(buf); let peak = 0; for (const v of buf) peak = Math.max(peak, Math.abs(v - 128));
    const target = MEET.muted ? 0 : Math.min(1, peak / 64);
    level = target > level ? level + (target - level) * 0.5 : level + (target - level) * 0.15;
    document.querySelectorAll(".meter").forEach(m => [...m.children].forEach((b, i) => b.classList.toggle("on", i / 16 < level)));
  };
  MEET.meter = { ctx, raf: requestAnimationFrame(tick) };
}
function meterStop() { if (MEET.meter) { cancelAnimationFrame(MEET.meter.raf); MEET.meter.ctx.close().catch(() => null); MEET.meter = null; } }

/* ---------------- scheduling ---------------- */
async function meetingSchedule() {
  const v = RM.v;
  const title = el("input", { type: "text", placeholder: "Production meeting", "aria-label": "Title", style: "width:100%" });
  const when = el("input", { type: "datetime-local", "aria-label": "When" });
  const mins = el("input", { type: "number", value: 60, min: 5, max: 600, "aria-label": "Minutes", style: "width:90px" });
  const agenda = el("textarea", { rows: 3, placeholder: "Agenda (optional)", style: "width:100%;height:auto;padding:10px 12px", "aria-label": "Agenda" });
  const opts = postable();
  const boxes = opts.map(([id, label]) => [id, el("input", { type: "checkbox", checked: /Production office|Heads of department/.test(label) })]);
  const ok = await modal({ icon: "video", title: "Schedule a meeting", body: [el("label", { class: "f" }, "Title", title),
    el("div", { class: "row", style: "margin-top:10px" }, el("label", { class: "f" }, "When", when), el("label", { class: "f" }, "Minutes", mins)),
    el("label", { class: "f", style: "margin-top:10px" }, "Agenda", agenda),
    el("div", { class: "f", style: "margin-top:12px" }, el("span", {}, "Who can join"), el("div", { class: "chk-list" }, boxes.map(([id, b]) => el("label", { class: "chk" }, b, opts.find(o => o[0] === id)[1])))),
    el("p", { class: "muted small" }, "Up to 75 people. Executives are on stage and bring others up; everyone else watches and can raise a hand. Not recorded.")],
    actions: [["Cancel", false], ["Schedule", true, true]] });
  if (!ok) return;
  try {
    await api.post("/api/room/meetings", { production: v.production, title: title.value.trim(), starts: when.value ? new Date(when.value).toISOString() : null,
      minutes: Number(mins.value) || 60, agenda: agenda.value, spaces: boxes.filter(([, b]) => b.checked).map(([id]) => id) });
    toast("ok", "Meeting scheduled", "Everyone invited is notified and can add it to their calendar."); voiceRefresh();
  } catch (e) { toast("bad", "Couldn't schedule it", e.message); }
}

/* ---------------- the meeting page: stage, audience, hands, chat ---------------- */
async function meetPage(mid) {
  if (!RM.v) await roomLoad();
  roomTopbar();
  const box = el("div", { class: "meet" });
  put(app(), box);
  MEET.page = box;
  if (!MEET.room || MEET.info.meeting !== mid) {
    put(box, el("div", { class: "card" }, el("h1", {}, "Joining…")));
    if (!(await micConsent().catch(() => false))) { location.hash = `#/room/${RM.prod}`; return; }
    try { await meetConnect(await api.post(`/api/room/meetings/${mid}/join`, {})); }
    catch (e) { put(box, el("div", { class: "card" }, el("h2", {}, "Couldn't join the meeting"), errBox(e), el("a", { class: "btn", href: `#/room/${RM.prod}` }, "Back to the Room"))); return; }
  }
  meetPaint();
}

function meetPaint() {
  voiceRefresh();
  const box = MEET.page;
  if (!box || !document.body.contains(box) || !MEET.room) return;
  const room = MEET.room, info = MEET.info, me = room.localParticipant;
  const all = [me, ...room.remoteParticipants.values()];
  const onStage = p => p.permissions ? !!p.permissions.canPublish : p === me && MEET.onStage;
  const stage = all.filter(onStage), audience = all.filter(p => !onStage(p));
  const tile = p => {
    const cam = [...p.videoTrackPublications.values()].find(t => t.track && !t.isMuted);
    const t = el("div", { class: "tile-v" + (MEET.speaking.has(p.identity) ? " speaking" : "") },
      cam ? null : el("span", { class: "big-ini" }, initialsOf(p.identity)),
      el("span", { class: "nm" }, nameOf(p.identity) + (p === me ? " (you)" : "")),
      info.can_direct && p !== me ? el("div", { class: "tile-act" },
        el("button", { type: "button", class: "btn sm quiet", onclick: () => meetDirect(p.identity, false) }, "Send back to watching"),
        [...p.audioTrackPublications.values()][0] ? el("button", { type: "button", class: "btn sm quiet", onclick: () => meetMuteOther(p) }, "Mute") : null) : null);
    if (cam) { const v = cam.track.attach(); v.muted = true; t.prepend(v); }
    return t;
  };
  const hands = audience.filter(p => MEET.hands.has(p.identity));
  const chatIn = el("input", { type: "text", placeholder: "Message everyone in the meeting", "aria-label": "Meeting chat" });
  const sendChat = async () => { const t = chatIn.value.trim(); if (!t) return; chatIn.value = ""; await me.publishData(new TextEncoder().encode(t), { reliable: true, topic: "chat" }); MEET.chat.push({ who: me.identity, text: t, ts: Date.now() / 1000 }); meetPaint(); };
  chatIn.addEventListener("keydown", e => { if (e.key === "Enter") sendChat(); });
  put(box,
    el("div", { class: "meet-main" },
      el("div", { class: "meet-head" }, el("div", {}, el("h1", {}, info.title || "Meeting"), el("p", { class: "lede" }, `${plural(stage.length, "person", "people")} on stage · ${plural(audience.length, "person", "people")} watching · up to ${info.max}`)),
        el("div", { class: "row" },
          MEET.onStage ? el("button", { type: "button", class: "btn", onclick: meetMute }, icon(MEET.muted ? "micoff" : "mic"), MEET.muted ? "Unmute" : "Mute") : null,
          MEET.onStage ? el("button", { type: "button", class: "btn", onclick: async () => { const on = ![...me.videoTrackPublications.values()].some(t => t.track && !t.isMuted); await me.setCameraEnabled(on).catch(e => toast("bad", "Camera", e.message)); meetPaint(); } }, icon("video"), "Camera") : null,
          !MEET.onStage ? el("button", { type: "button", class: "btn", "aria-pressed": String(MEET.hands.has(me.identity)), onclick: async () => {
            const up = !MEET.hands.has(me.identity); await me.setAttributes({ hand: up ? "up" : "" }).catch(() => null); up ? MEET.hands.add(me.identity) : MEET.hands.delete(me.identity); meetPaint(); } }, icon("hand"), MEET.hands.has(me.identity) ? "Lower hand" : "Raise hand") : null,
          el("button", { type: "button", class: "btn", onclick: async () => { await meetLeave(); location.hash = `#/room/${RM.prod}`; } }, "Leave"),
          info.can_direct ? el("button", { type: "button", class: "btn quiet", onclick: async () => { if (await modal({ icon: "alert", title: "End the meeting for everyone?", actions: [["Cancel", false], ["End it", true, true]] })) { await api.post(`/api/room/meetings/${info.meeting}/end`, {}); await meetLeave(); location.hash = `#/room/${RM.prod}`; } } }, "End") : null)),
      el("div", { class: "stage" }, stage.map(tile)),
      !MEET.onStage ? el("p", { class: "muted small" }, MEET.hands.has(me.identity) ? "Hand raised. An executive can bring you on stage to speak." : "You're watching. Raise your hand if you need to speak.") : null,
      info.can_direct ? el("section", { class: "card aud" }, el("h2", {}, `Watching (${audience.length})`, hands.length ? el("small", {}, ` · ${hands.length} hand${hands.length > 1 ? "s" : ""} up`) : null),
        el("ul", { class: "plain people" }, audience.sort((a, b) => MEET.hands.has(b.identity) - MEET.hands.has(a.identity)).map(p => el("li", {},
          el("span", { class: "av sm" }, initialsOf(p.identity)), el("span", { class: "pn" }, nameOf(p.identity), MEET.hands.has(p.identity) ? el("small", { class: "hand" }, "Hand raised") : null),
          el("button", { type: "button", class: "btn sm", onclick: () => meetDirect(p.identity, true) }, "Bring on stage"))))) : null),
    el("aside", { class: "card meet-chat" }, el("h2", {}, "Chat"),
      el("div", { class: "mc-list" }, MEET.chat.length ? MEET.chat.map(m => el("div", { class: "mc" }, el("b", {}, nameOf(m.who)), " ", m.text)) : el("p", { class: "muted small" }, "Messages here aren't kept after the meeting.")),
      el("div", { class: "composer" }, chatIn, el("button", { type: "button", class: "btn primary sm", onclick: sendChat }, "Send"))));
}

async function meetDirect(user, on) {
  try { await api.post(`/api/room/meetings/${MEET.info.meeting}/stage`, { user, on }); } catch (e) { toast("bad", "Couldn't change that", e.message); }
}
async function meetMuteOther(p) {
  const pub = [...p.audioTrackPublications.values()][0];
  if (!pub) return;
  try { await api.post(`/api/room/meetings/${MEET.info.meeting}/mute`, { user: p.identity, track: pub.trackSid }); } catch (e) { toast("bad", "Couldn't mute", e.message); }
}
