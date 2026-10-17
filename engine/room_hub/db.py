"""The hub's store: SQLite for metadata, encrypted blobs on disk. Nothing here is plaintext content: names, messages,
notes, call sheets and files arrive encrypted by the devices, and the hub keeps only ids, tiers, times and sizes."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, exec INTEGER DEFAULT 0, founder INTEGER DEFAULT 0,
  deleted INTEGER DEFAULT 0, seq INTEGER);
CREATE TABLE IF NOT EXISTS devices (id TEXT PRIMARY KEY, user TEXT, x TEXT, ed TEXT, status TEXT, record TEXT,
  invite TEXT, commit_ TEXT, n_joiner TEXT, approver TEXT, n_approver TEXT, created INTEGER, seq INTEGER);
CREATE TABLE IF NOT EXISTS exec_grants (id INTEGER PRIMARY KEY AUTOINCREMENT, rec TEXT, seq INTEGER);
CREATE TABLE IF NOT EXISTS revocations (id INTEGER PRIMARY KEY AUTOINCREMENT, device TEXT, rec TEXT, seq INTEGER);
CREATE TABLE IF NOT EXISTS invites (id TEXT PRIMARY KEY, token_hash TEXT UNIQUE, production TEXT, tier TEXT,
  department TEXT, second_ad INTEGER DEFAULT 0, user TEXT, details TEXT, created_by TEXT, status TEXT,
  expires INTEGER, seq INTEGER);
CREATE TABLE IF NOT EXISTS productions (id TEXT PRIMARY KEY, created_by TEXT, created INTEGER, archived INTEGER,
  seq INTEGER);
CREATE TABLE IF NOT EXISTS memberships (user TEXT, production TEXT, tier TEXT, department TEXT,
  second_ad INTEGER DEFAULT 0, seq INTEGER, PRIMARY KEY (user, production));
CREATE TABLE IF NOT EXISTS spaces (id TEXT PRIMARY KEY, production TEXT, kind TEXT, audience TEXT, owner TEXT,
  epoch INTEGER, created_by TEXT, seq INTEGER, rotate INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS space_members (space TEXT, user TEXT, seq INTEGER, PRIMARY KEY (space, user));
CREATE TABLE IF NOT EXISTS wraps (space TEXT, epoch INTEGER, device TEXT, w TEXT, seq INTEGER,
  PRIMARY KEY (space, epoch, device));
CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, production TEXT, kind TEXT, author TEXT, device TEXT,
  subject TEXT, body TEXT, ts INTEGER, seq INTEGER);
CREATE TABLE IF NOT EXISTS item_spaces (item TEXT, space TEXT, PRIMARY KEY (item, space));
CREATE TABLE IF NOT EXISTS tombstones (item TEXT PRIMARY KEY, seq INTEGER);
CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, space TEXT, lineage TEXT, version INTEGER, chunks INTEGER,
  size INTEGER, status TEXT, created_by TEXT, item TEXT, seq INTEGER);
CREATE TABLE IF NOT EXISTS grants (id TEXT PRIMARY KEY, production TEXT, a TEXT, b TEXT, granted_by TEXT,
  revoked INTEGER DEFAULT 0, seq INTEGER);
CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, production TEXT,
  kind TEXT, item TEXT, ts INTEGER, seq INTEGER);
CREATE TABLE IF NOT EXISTS confirmations (item TEXT, version INTEGER, user TEXT, ts INTEGER, seq INTEGER,
  PRIMARY KEY (item, version, user));
CREATE TABLE IF NOT EXISTS tokens (hash TEXT PRIMARY KEY, device TEXT, expires INTEGER);
DROP TABLE IF EXISTS challenges;
CREATE TABLE challenges (device TEXT, challenge TEXT, expires INTEGER, PRIMARY KEY (device, challenge));
CREATE TABLE IF NOT EXISTS push_subs (device TEXT PRIMARY KEY, sub TEXT);
CREATE TABLE IF NOT EXISTS audit (n INTEGER PRIMARY KEY AUTOINCREMENT, seq INTEGER, ts INTEGER, actor TEXT,
  device TEXT, action TEXT, production TEXT, target TEXT, prev TEXT, hash TEXT);
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT, 'audit is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT, 'audit is append-only'); END;
CREATE INDEX IF NOT EXISTS items_seq ON items (seq);
CREATE INDEX IF NOT EXISTS wraps_dev ON wraps (device, seq);
CREATE INDEX IF NOT EXISTS item_spaces_space ON item_spaces (space);
"""


def _audit_hash(seq, ts, actor, device, action, production, target, prev) -> str:
    body = json.dumps([seq, ts, actor, device, action, production, target, prev], sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


class Store:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.blobs = self.root / "blobs"
        self.blobs.mkdir(exist_ok=True)
        self.lock = threading.RLock()
        self.c = sqlite3.connect(self.root / "hub.sqlite3", check_same_thread=False, isolation_level=None)
        self.c.row_factory = sqlite3.Row
        self.c.execute("PRAGMA journal_mode=WAL")
        self.c.execute("PRAGMA foreign_keys=ON")
        self.c.executescript(SCHEMA)
        self._seq = int(self.meta("seq") or 0)
        self.listeners: list = []          # callables(seq, users or None)

    # ------------------------------------------------------------ basics
    def meta(self, k: str, v: str | None = None):
        if v is None:
            r = self.c.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
            return r["v"] if r else None
        self.c.execute("INSERT OR REPLACE INTO meta (k, v) VALUES (?, ?)", (k, v))
        return v

    @contextmanager
    def tx(self, users=None):
        """One write transaction. Every row written inside it takes the transaction's sequence number, which is how
        devices sync ("everything I can see after seq N"). users: who to wake (None: everyone)."""
        with self.lock:
            self.c.execute("BEGIN IMMEDIATE")
            try:
                self._seq += 1
                self.meta("seq", str(self._seq))
                yield self._seq
                self.c.execute("COMMIT")
            except BaseException:
                self.c.execute("ROLLBACK")
                self._seq = int(self.meta("seq") or 0)
                raise
        for fn in list(self.listeners):
            try:
                fn(self._seq, users)
            except Exception:  # noqa: BLE001 - a listener must never break a write
                pass

    @property
    def seq(self) -> int:
        return self._seq

    def q(self, sql: str, args=()):
        with self.lock:
            return self.c.execute(sql, args).fetchall()

    def one(self, sql: str, args=()):
        with self.lock:
            return self.c.execute(sql, args).fetchone()

    def x(self, sql: str, args=()):
        return self.c.execute(sql, args)

    # ------------------------------------------------------------ audit (append-only, hash-chained)
    def audit(self, seq: int, actor: str, device: str, action: str, production: str | None, target: dict):
        prev = self.c.execute("SELECT hash FROM audit ORDER BY n DESC LIMIT 1").fetchone()
        prev_h = prev["hash"] if prev else "0" * 64
        ts = int(time.time())
        self.c.execute("INSERT INTO audit (seq, ts, actor, device, action, production, target, prev, hash) "
                       "VALUES (?,?,?,?,?,?,?,?,?)", (seq, ts, actor, device, action, production,
                                                      json.dumps(target, sort_keys=True), prev_h,
                                                      _audit_hash(seq, ts, actor, device, action, production, target, prev_h)))

    def audit_ok(self) -> bool:
        """The chain is intact: every line names the hash of the one before and hashes to what it says."""
        prev = "0" * 64
        for r in self.q("SELECT * FROM audit ORDER BY n"):
            h = _audit_hash(r["seq"], r["ts"], r["actor"], r["device"], r["action"], r["production"],
                            json.loads(r["target"]), r["prev"])
            if r["prev"] != prev or r["hash"] != h:
                return False
            prev = r["hash"]
        return True

    # ------------------------------------------------------------ blobs
    def chunk_path(self, file_id: str, i: int) -> Path:
        d = self.blobs / file_id[:2] / file_id
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{i:06d}"
