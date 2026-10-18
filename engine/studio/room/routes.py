"""The Studio's local Room API (127.0.0.1 only): what ui/room.js calls. Each call goes through this computer's Room client,
which encrypts before anything leaves for the hub."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import httpx
from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from . import host as H
from . import service as S
from .client import RoomError

router = APIRouter(prefix="/api/room")


def _c(**hint):
    """The Room this request is about (this computer may be in several hosts' Rooms): found from the production, space,
    item, file or meeting it names; otherwise the one the page is on."""
    c = S.resolve(**hint) if hint else S.client()
    if c.state.get("status") != "approved":
        raise HTTPException(409, "This computer isn't in the Room yet.")
    return c


def _run(fn, *a, **kw):
    try:
        with S._LOCK:
            return fn(*a, **kw)
    except RoomError as e:
        raise HTTPException(400, str(e)) from e
    except ValueError as e:                    # a bad time, a malformed CSV
        raise HTTPException(400, str(e)) from e


def _token_from(link: str) -> str:
    """An invite link (https://hub/app/#join=TOKEN, or ?join=TOKEN) or the bare token."""
    link = (link or "").strip()
    if "join=" in link:
        u = urlparse(link)
        for part in (u.fragment, u.query):
            q = parse_qs(part.lstrip("/").split("?")[-1])
            if q.get("join"):
                return q["join"][0]
    return link


def _hub_from(link: str) -> str | None:
    u = urlparse((link or "").strip())
    return f"{u.scheme}://{u.netloc}" if u.scheme in ("http", "https") and u.netloc else None


# ------------------------------------------------------------------ setting up
@router.get("/state")
def state():
    c = S.client()
    approved = S.clients()
    if approved and c.state.get("status") != "approved":
        c = S.activate(approved[0])
    st = c.state.get("status") or "none"
    out = {"status": st, "hub": c.state.get("hub", ""), "name": (c.state.get("profile") or {}).get("name", ""),
           "joining": any(x.state.get("status") == "pending" for x in S.clients(None)), "host": H.status()}
    if st == "approved":
        S.start_live()
        S.resume_uploads()
    return out


@router.post("/hub")
def set_hub(body: dict = Body(...)):
    hub = (body.get("hub") or "").strip().rstrip("/")
    if not hub.startswith(("http://", "https://")):
        raise HTTPException(400, "Enter the Room's address, starting https://")
    if hub.startswith("http://") and not S.is_local(hub):
        raise HTTPException(400, "Use https:// for a Room on the internet. Plain http:// is only for this network.")
    try:
        h = httpx.get(hub + "/api/health", timeout=10, trust_env=not S.is_local(hub)).json()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, f"The Room at that address didn't answer ({type(e).__name__}).") from e
    S.client(hub=hub)
    return {"ok": True, "founded": h.get("founded"), "version": h.get("version")}


@router.post("/found")
def found(body: dict = Body(...)):
    c = S.client(hub=body.get("hub") or None)
    if c.state.get("status"):
        raise HTTPException(409, "This computer is already set up for a Room.")
    _run(c.bootstrap, body["token"].strip(), body["name"].strip(), body.get("role", "Executive").strip())
    S.start_live()
    return {"ok": True}


def _host_and_found(name: str) -> "S.RoomClient":
    """Run the Room on this computer (if it isn't already) and make this computer's owner its first executive."""
    try:
        H.start()
    except RoomError as e:
        raise HTTPException(400, str(e)) from e
    c = S.own()
    if c:
        return S.activate(c)
    if not name:
        raise HTTPException(400, "Enter your name first.")
    tok = H.founder_token()
    if not tok:
        raise HTTPException(409, "This computer's Room already has its first executive. Join it with an invite instead.")
    c = S.client(hub=H.local())
    _run(c.bootstrap, tok, name, "Executive")
    S.start_live()
    return c


@router.post("/host")
def host_room(body: dict = Body(...)):
    """Start a project on this computer: the Room runs here and everyone invited connects to this computer."""
    name, prod = (body.get("name") or "").strip(), (body.get("production") or "").strip()
    if not prod:
        raise HTTPException(400, "Name the production.")
    c = _host_and_found(name[:120])
    pid = _run(c.create_production, prod[:120])
    S.bumped()
    return {"id": pid, "address": H.address()}


@router.post("/join")
def join(body: dict = Body(...)):
    link = body.get("invite", "")
    hub = _hub_from(link) or body.get("hub")
    c = S.client(hub=hub) if hub else S.client()
    if not c.state.get("hub") and not getattr(c, "_http", None):
        raise HTTPException(400, "Paste the whole invite link you were sent (it starts http).")
    if c.state.get("status") == "approved":
        raise HTTPException(409, "You're already in this Room. Its productions are in the switcher.")
    _run(c.join, _token_from(link), (body.get("name") or "").strip())
    return _run(c.join_progress)


@router.get("/join")
def join_progress():
    c = next(iter(S.clients("pending")), None) or S.client()
    if c.state.get("status") not in ("pending", "approved"):
        return {"stage": "none"}
    r = _run(c.join_progress)
    if r["stage"] == "approved":
        S.start_live()
    return r


@router.post("/leave")
def leave():
    """Forget the Room on this computer (keys and cache). The executive should also remove the device."""
    c = next(iter(S.clients("pending") + S.clients("declined") + S.clients("revoked")), None)
    S.stop_live()
    with S._LOCK:
        if c is not None and c.dir != S.folder():          # one host's Room this computer never got into
            S._CLIENTS.pop(str(c.dir), None)
            shutil.rmtree(c.dir, ignore_errors=True)
        elif not S.clients():
            shutil.rmtree(S.folder(), ignore_errors=True)
            S._CLIENTS.clear()
        S._CLIENT = None
    S.start_live()
    return {"ok": True}


# ------------------------------------------------------------------ the room
@router.get("/view")
def view(production: str | None = None):
    c = _c(production=production) if production else _c()
    S.start_live()
    return _run(S.view, c, production)


@router.post("/sync")
def sync():
    c = _c()
    _run(c.sync)
    S.bumped()
    return {"ok": True}


@router.get("/wait")
async def wait(since: int = 0):
    """Long poll: returns when something changed in the Room (or after 25 s)."""
    return {"seq": await run_in_threadpool(S.wait, since, 25)}


@router.get("/space/{sid}")
def space(sid: str, oversight: bool = False):
    return _run(S.space_view, _c(space=sid), sid, open_oversight=oversight)


@router.get("/search")
def search(production: str, q: str):
    return _run(S.search, _c(production=production), production, q)


@router.post("/oversight-seen")
def oversight_seen():
    c = _c()
    c.state["oversight_seen"] = True
    c._save_state()
    return {"ok": True}


@router.post("/notifications-seen")
def notifications_seen(body: dict = Body(...)):
    c = _c()
    c.state["notes_seen"] = max(int(c.state.get("notes_seen", 0)), int(body.get("id", 0)))
    c._save_state()
    return {"ok": True}


@router.post("/message")
def message(body: dict = Body(...)):
    c = _c(space=body["space"])
    sid, text = body["space"], (body.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "Write a message first.")
    sv = _run(S.space_view, c, sid, open_oversight=False)
    mentions = S.mentions_in(text, sv.get("members") or [])
    _run(c.post, [sid], "msg", {"text": text[:8000]}, mentions=mentions)
    S.bumped()
    return {"ok": True}


@router.post("/note")
def note(body: dict = Body(...)):
    spaces = [s for s in body.get("spaces", []) if s]
    c = _c(space=spaces[0]) if spaces else _c()
    title = (body.get("title") or "").strip()
    if not spaces or not title:
        raise HTTPException(400, "Give the note a title and pick where it goes.")
    status = body.get("status") if body.get("status") in S.NOTE_STATUSES else "Open"
    _run(c.post, spaces, "note", {"title": title[:300], "body": (body.get("body") or "")[:8000], "status": status,
                                  "pinned": bool(body.get("pinned"))})
    S.bumped()
    return {"ok": True}


@router.post("/note/{nid}")
def note_update(nid: str, body: dict = Body(...)):
    c = _c(item=nid)
    it = c.items.get(nid)
    if not it:
        raise HTTPException(404, "Unknown note.")
    upd = {}
    if body.get("status") in S.NOTE_STATUSES:
        upd["status"] = body["status"]
    if "pinned" in body:
        upd["pinned"] = bool(body["pinned"])
    spaces = [s for s, _ in it["h"]["spaces"] if (s, c.space(s)["epoch"]) in c.keys]
    _run(c.post, spaces, "note_update", upd, ref=nid)
    S.bumped()
    return {"ok": True}


@router.post("/upload")
async def upload(space: str = Form(...), file: UploadFile = File(...), note: str = Form(""),
                 note_title: str = Form(""), note_spaces: str = Form("")):
    _c(space=space)
    tmp = Path(tempfile.mkdtemp(dir=S.folder())) / "upload.bin"
    size = 0
    with open(tmp, "wb") as fh:
        while chunk := await file.read(1 << 20):
            fh.write(chunk)
            size += len(chunk)
    card = None
    if note_title.strip():
        card = {"spaces": [s for s in note_spaces.split(",") if s] or [space],
                "payload": {"title": note_title.strip()[:300], "body": note[:8000], "status": "Open", "pinned": False}}
    key = S.start_upload(space, Path(file.filename or "file").name, tmp, size, note="" if card else note[:2000], note_card=card)
    return {"key": key}


@router.get("/uploads")
def uploads():
    return list(S.UPLOADS.values())


@router.get("/file/{fid}")
def download(fid: str):
    c = _c(file=fid)
    f = next((x for x in c.files() if x["id"] == fid), None)
    if not f:
        raise HTTPException(404, "That file isn't visible to you.")
    it = iter(c.download_iter(fid))
    try:
        first = next(it)                    # fail before the download starts if the first part can't be opened
    except RoomError as e:
        raise HTTPException(400, str(e)) from e

    def gen():
        yield first
        yield from it
    safe = "".join(ch for ch in f["name"] if ch not in '\\/:*?"<>|') or "file"
    return StreamingResponse(gen(), media_type="application/octet-stream",
                             headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(safe)}",
                                      "Content-Length": str(f["size"])})


@router.post("/dm")
def dm(body: dict = Body(...)):
    sid = _run(_c(production=body["production"]).dm, body["production"], body["user"])
    S.bumped()
    return {"id": sid}


# ------------------------------------------------------------------ productions, spaces, people (producers and executives)
@router.post("/productions")
def new_production(body: dict = Body(...)):
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "Name the production.")
    c = _host_and_found((body.get("you") or S._me(S.client(), None).get("name") or "").strip())   # always on this computer
    pid = _run(c.create_production, name[:120])
    S.bumped()
    return {"id": pid}


@router.post("/productions/{pid}/archive")
def archive(pid: str, body: dict = Body({})):
    c = _c(production=pid)
    _run(c._req, "POST", f"/api/productions/{pid}/archive", json={"archived": bool(body.get("archived", True))})
    _run(c.sync)
    S.bumped()
    return {"ok": True}


@router.post("/spaces")
def new_space(body: dict = Body(...)):
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "Name the space.")
    c = _c(production=body["production"])
    aud = {"tiers": body.get("tiers") or [], "departments": body.get("departments") or [], "second_ad": bool(body.get("second_ad"))}
    members = list(body.get("members") or [])
    if c.is_exec and c.me not in members:
        members.append(c.me)
    sid = _run(c.create_space, body["production"], name[:80], audience=aud, members=members)
    _run(c.sync)
    S.bumped()
    return {"id": sid}


@router.post("/spaces/{sid}/people")
def space_people(sid: str, body: dict = Body(...)):
    c = _c(space=sid)
    _run(c._req, "POST", f"/api/spaces/{sid}/members", json={"add": body.get("add", []), "remove": body.get("remove", [])})
    _run(c.sync)
    S.bumped()
    return {"ok": True}


@router.post("/departments")
def new_department(body: dict = Body(...)):
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "Name the department.")
    dep = _run(_c(production=body["production"]).add_department, body["production"], name[:80])
    S.bumped()
    return {"id": dep}


@router.post("/invite")
def invite(body: dict = Body(...)):
    c = _c(production=body["production"]) if body.get("production") else _c()
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "Who are you inviting?")
    r = _run(c.invite, body.get("production"), body.get("tier"), name[:120], role=(body.get("role") or "")[:120],
             department=body.get("department") or "", second_ad=bool(body.get("second_ad")),
             user=body.get("user"), company=bool(body.get("company")))
    base = H.address() if S._hosted_here(c) else c.state["hub"]      # people reach a host's PC on its network address
    link = f"{base}/app/#join={r['token']}"
    return {"link": link, "expires_in_days": r["expires_in_days"]}


@router.get("/access")
def access(production: str):
    from . import access as A
    return _run(A.view, _c(production=production), production)


@router.post("/pending/{device}/check")
def pending_check(device: str):
    _run(_c().start_check, device)
    return {"ok": True}


@router.post("/pending/{device}/approve")
def pending_approve(device: str, body: dict = Body({})):
    c = _c()
    _run(c.approve, device, (body.get("name") or "").strip(), (body.get("role") or "").strip())
    S.bumped()
    return {"ok": True}


@router.post("/pending/{device}/decline")
def pending_decline(device: str):
    _run(_c().decline, device)
    return {"ok": True}


@router.post("/members/set")
def member_set(body: dict = Body(...)):
    c = _c(production=body["production"])
    _run(c.set_member, body["production"], body["user"], body["tier"], body.get("department") or "", bool(body.get("second_ad")))
    if body.get("name") is not None:
        _run(c.set_person, body["production"], body["user"], {"name": body["name"].strip(), "role": (body.get("role") or "").strip()})
    S.bumped()
    return {"ok": True}


@router.post("/members/remove")
def member_remove(body: dict = Body(...)):
    _run(_c(production=body["production"]).remove_member, body["production"], body["user"])
    S.bumped()
    return {"ok": True}


@router.post("/devices/{device}/remove")
def device_remove(device: str):
    _run(_c().revoke_device, device)
    S.bumped()
    return {"ok": True}


@router.post("/grants")
def grant(body: dict = Body(...)):
    c = _c(production=body["production"])
    gid = _run(c.grant_contact, body["production"], body["a"], body["b"])
    _run(c.sync)
    S.bumped()
    return {"id": gid}


@router.post("/grants/{gid}/revoke")
def grant_revoke(gid: str):
    c = _c()
    _run(c._req, "POST", f"/api/grants/{gid}/revoke")
    _run(c.sync)
    return {"ok": True}


@router.post("/execs")
def execs(body: dict = Body(...)):
    _run(_c().make_exec, body["user"], bool(body.get("on", True)))
    S.bumped()
    return {"ok": True}


# ------------------------------------------------------------------ call sheets
@router.get("/callsheets")
def callsheet_list(production: str):
    from . import callsheets as CS
    c = _c(production=production)
    out = []
    for lin, versions in CS.sheets(c, production).items():
        s = versions[0]
        conf = CS.confirmations(c, s["item"])
        out.append({"lineage": lin, "item": s["item"], "day": s["day"], "date": s["date"], "version": s["version"],
                    "unit_call": s["unit_call"], "location": s["location"], "expected": len(s.get("people") or []),
                    "confirmed": len(conf & set(s.get("people") or [])), "posted": s["ts"]})
    return sorted(out, key=lambda x: (x["date"] or "", x["posted"]), reverse=True)


@router.get("/callsheets/{lineage}")
def callsheet_get(lineage: str, production: str):
    from . import callsheets as CS
    c = _c(production=production)
    versions = CS.sheets(c, production).get(lineage)
    if not versions:
        raise HTTPException(404, "Unknown call sheet.")
    s = versions[0]
    rows = CS.rows_for(c, production, lineage, s["version"])
    return dict(s, rows=[dict(rows.get(u, {}), user=u) for u in s.get("people") or []],
                history=[{"version": v["version"], "posted": v["ts"]} for v in versions])


@router.post("/callsheets/pdf")
async def callsheet_pdf(production: str = Form(...), file: UploadFile = File(...)):
    from . import callsheets as CS
    c = _c(production=production)
    data = await file.read()
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(413, "That PDF is over 50 MB.")
    spaces = CS.audience(c, production)
    if not spaces:
        raise HTTPException(400, "There's no channel to share the PDF in yet.")
    item = await run_in_threadpool(_run, c.upload, spaces[0], Path(file.filename or "callsheet.pdf").name, data,
                                   share=spaces[1:])
    return {"id": item["h"]["ref"], "name": item["payload"]["name"], "size": item["payload"]["size"]}


@router.post("/callsheets")
def callsheet_publish(body: dict = Body(...)):
    from . import callsheets as CS
    r = _run(CS.publish, _c(production=body["production"]), body["production"], body, pdf_file=body.get("pdf"))
    S.bumped()
    return r


@router.post("/callsheets/csv")
def callsheet_csv(body: dict = Body(...)):
    from . import callsheets as CS
    c = _c(production=body["production"])
    return _run(CS.parse_csv, body.get("text", ""), S.people(c, body["production"]))


@router.post("/callsheets/item/{item}/confirm")
def callsheet_confirm(item: str):
    from . import callsheets as CS
    _run(CS.confirm, _c(item=item), item)
    S.bumped()
    return {"ok": True}


@router.post("/callsheets/item/{item}/remind")
def callsheet_remind(item: str):
    from . import callsheets as CS
    return {"reminded": _run(CS.remind, _c(item=item), item)}


# ------------------------------------------------------------------ huddles and meetings
@router.get("/meetings")
def meetings_list(production: str):
    from . import meetings as M
    c = _c(production=production)
    rows = _run(M.listing, c, production, S.people(c, production))
    for m in rows:
        S.MEETINGS[m["id"]] = str(c.dir)
    return rows


@router.post("/huddle")
def huddle(body: dict = Body(...)):
    """Join the huddle in a space, starting it if nobody has yet."""
    from . import meetings as M
    c = _c(space=body["space"])
    sp = body["space"]
    m = _run(M.huddle_for, c, sp)
    mid = m["id"] if m else _run(M.start, c, c.space(sp)["production"], [sp], "huddle", "Huddle")
    S.MEETINGS[mid] = str(c.dir)
    return _run(M.join, c, mid)


@router.post("/meetings")
def meeting_new(body: dict = Body(...)):
    from . import meetings as M
    c = _c(production=body["production"])
    title = (body.get("title") or "").strip()
    spaces = [s for s in body.get("spaces") or [] if s]
    if not title or not spaces:
        raise HTTPException(400, "Give the meeting a title and pick who it's for.")
    mid = _run(M.start, c, body["production"], spaces, "meeting", title, body.get("starts"), int(body.get("minutes") or 60),
               body.get("agenda") or "")
    S.MEETINGS[mid] = str(c.dir)
    S.bumped()
    return {"id": mid}


@router.post("/meetings/{mid}/join")
def meeting_join(mid: str):
    from . import meetings as M
    return _run(M.join, _c(meeting=mid), mid)


@router.get("/meetings/{mid}")
def meeting_state(mid: str):
    c = _c(meeting=mid)
    return _run(c._req, "GET", f"/api/meetings/{mid}")


@router.post("/meetings/{mid}/stage")
def meeting_stage(mid: str, body: dict = Body(...)):
    return _run(_c(meeting=mid)._req, "POST", f"/api/meetings/{mid}/stage", json={"user": body["user"], "on": bool(body.get("on", True))})


@router.post("/meetings/{mid}/mute")
def meeting_mute(mid: str, body: dict = Body(...)):
    return _run(_c(meeting=mid)._req, "POST", f"/api/meetings/{mid}/mute", json={"user": body["user"], "track": body["track"]})


@router.post("/meetings/{mid}/end")
def meeting_end(mid: str):
    r = _run(_c(meeting=mid)._req, "POST", f"/api/meetings/{mid}/end")
    S.bumped()
    return r


@router.get("/meetings/{mid}/ics")
def meeting_ics(mid: str, production: str):
    from fastapi.responses import Response
    from . import meetings as M
    c = _c(production=production)
    name = next((p["name"] for p in S.productions(c) if p["id"] == production), "")
    return Response(_run(M.ics, c, mid, name), media_type="text/calendar",
                    headers={"Content-Disposition": 'attachment; filename="meeting.ics"'})
