"""The hub's live channel (1.0.8): a WebSocket that says "something changed" (a sequence number, never content), and
that lets the hub stop cleanly while phones and Studios are still connected."""
import json
import socket
import threading
import time

import uvicorn
from websockets.sync.client import connect

from room_world import World


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_live_pings_carry_only_a_number_and_the_hub_stops_with_links_open(tmp_path):
    w = World(tmp_path)
    port = free_port()
    assert port != 8799
    server = uvicorn.Server(uvicorn.Config(w.app, host="127.0.0.1", port=port, log_level="warning"))
    th = threading.Thread(target=server.run, daemon=True)
    th.start()
    end = time.time() + 10
    while not server.started and time.time() < end:
        time.sleep(0.05)
    assert server.started

    ws = connect(f"ws://127.0.0.1:{port}/api/live", open_timeout=5, proxy=None)
    ws.send(json.dumps({"token": w.tim._bearer()}))
    first = json.loads(ws.recv(timeout=5))
    assert set(first) == {"seq"}
    w.tim.create_production("ZZLIVEPRODZZ")
    msg = json.loads(ws.recv(timeout=5))
    assert set(msg) == {"seq"} and msg["seq"] > first["seq"]

    # a link that never closes must not hold the hub open when the service is stopped
    t0 = time.time()
    server.should_exit = True
    th.join(timeout=10)
    assert not th.is_alive(), "the hub didn't stop while a live link was open"
    assert time.time() - t0 < 8
    ws.close()


def test_live_refuses_a_bad_token(tmp_path):
    w = World(tmp_path)
    port = free_port()
    server = uvicorn.Server(uvicorn.Config(w.app, host="127.0.0.1", port=port, log_level="warning"))
    th = threading.Thread(target=server.run, daemon=True)
    th.start()
    end = time.time() + 10
    while not server.started and time.time() < end:
        time.sleep(0.05)
    with connect(f"ws://127.0.0.1:{port}/api/live", open_timeout=5, proxy=None) as ws:
        ws.send(json.dumps({"token": "not-a-token"}))
        try:
            ws.recv(timeout=5)
            closed = False
        except Exception as e:  # noqa: BLE001
            closed = getattr(getattr(e, "rcvd", None), "code", None) == 4401
        assert closed
    server.should_exit = True
    th.join(timeout=10)
