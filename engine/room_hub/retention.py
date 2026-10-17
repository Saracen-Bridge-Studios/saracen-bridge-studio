"""Retention: a production's Room data is deleted 90 days after it is archived (the audit log keeps only ids)."""
from __future__ import annotations

import threading
import time

DAYS = 90


def purge(store, now: float | None = None) -> list[str]:
    """Delete every archived production older than DAYS: items, files and their blobs, spaces, keys, memberships,
    invites, notifications and confirmations. Returns the productions deleted."""
    now = now or time.time()
    gone = []
    for p in store.q("SELECT id FROM productions WHERE archived IS NOT NULL AND archived < ?", (now - DAYS * 86400,)):
        pid = p["id"]
        with store.tx() as seq:
            for f in store.q("SELECT f.id, f.chunks FROM files f JOIN spaces s ON s.id=f.space WHERE s.production=?", (pid,)):
                for i in range(f["chunks"]):
                    try:
                        store.chunk_path(f["id"], i).unlink()
                    except OSError:
                        pass
                try:
                    store.chunk_path(f["id"], 0).parent.rmdir()
                except OSError:
                    pass
                store.x("DELETE FROM files WHERE id=?", (f["id"],))
            for r in store.q("SELECT id FROM items WHERE production=?", (pid,)):
                store.x("INSERT OR REPLACE INTO tombstones (item, seq) VALUES (?,?)", (r["id"], seq))
            store.x("DELETE FROM confirmations WHERE item IN (SELECT id FROM items WHERE production=?)", (pid,))
            store.x("DELETE FROM item_spaces WHERE item IN (SELECT id FROM items WHERE production=?)", (pid,))
            store.x("DELETE FROM items WHERE production=?", (pid,))
            store.x("DELETE FROM wraps WHERE space IN (SELECT id FROM spaces WHERE production=?)", (pid,))
            store.x("DELETE FROM space_members WHERE space IN (SELECT id FROM spaces WHERE production=?)", (pid,))
            store.x("DELETE FROM spaces WHERE production=?", (pid,))
            store.x("DELETE FROM memberships WHERE production=?", (pid,))
            store.x("DELETE FROM invites WHERE production=?", (pid,))
            store.x("DELETE FROM notifications WHERE production=?", (pid,))
            store.x("DELETE FROM grants WHERE production=?", (pid,))
            store.x("DELETE FROM productions WHERE id=?", (pid,))
            store.audit(seq, "hub", "", "deleted an archived production's data", pid, {"after_days": DAYS})
        gone.append(pid)
    return gone


def start(store) -> threading.Event:
    """Run the purge every six hours in the background (the hub's serve command starts this)."""
    stop = threading.Event()

    def loop():
        while True:
            try:
                purge(store)
            except Exception:  # noqa: BLE001 - try again at the next round
                pass
            if stop.wait(6 * 3600):
                return
    threading.Thread(target=loop, daemon=True, name="room-retention").start()
    return stop


def install(app, store):
    app.state.retention = None
