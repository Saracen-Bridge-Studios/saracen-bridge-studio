"""The Room's crypto formats (1.0.8): tampering is detected, keys can't be replayed elsewhere, trust follows
executive approvals back to the founder."""
import pytest

import room_crypto as rc


def test_items_detect_any_change():
    d, k = rc.Device(), rc.new_key()
    it = rc.seal_item({"id": "m_1", "kind": "msg", "prod": "p_1", "ts": 1}, {"text": "hello"}, {"s_1": (1, k)}, d)
    assert rc.verify_item(it, d.ed_pk) and rc.open_item(it, "s_1", k) == {"text": "hello"}
    for change in (lambda x: x["h"].update(kind="note"), lambda x: x["h"].update(spaces=[["s_2", 1]]),
                   lambda x: x.update(ct=x["ct"][:-2] + ("A" if x["ct"][-2] != "A" else "B") + x["ct"][-1])):
        bad = {"h": dict(it["h"]), "ct": it["ct"], "keys": dict(it["keys"]), "sig": it["sig"]}
        change(bad)
        assert not rc.verify_item(bad, d.ed_pk)
    with pytest.raises(Exception):
        rc.open_item(it, "s_1", rc.new_key())


def test_an_item_key_cant_be_moved_to_another_space():
    d, k1, k2 = rc.Device(), rc.new_key(), rc.new_key()
    it = rc.seal_item({"id": "m_1", "kind": "msg", "prod": "p", "ts": 1}, {"t": 1}, {"s_1": (1, k1), "s_2": (4, k2)}, d)
    moved = dict(it, keys={"s_1": it["keys"]["s_2"], "s_2": it["keys"]["s_1"]})
    with pytest.raises(Exception):
        rc.open_item(moved, "s_1", k2)


def test_key_wraps_are_bound_to_space_epoch_and_device():
    a, b, c = rc.Device(), rc.Device(), rc.Device()
    k = rc.new_key()
    w = rc.wrap_key(k, "s_1", 2, b.public(), a)
    assert rc.unwrap_key(w, b) == k and rc.verify(a.ed_pk, rc.wrap_signed_bytes(w), w["sig"])
    with pytest.raises(Exception):
        rc.unwrap_key(w, c)                                      # someone else's wrap
    with pytest.raises(ValueError):
        rc.unwrap_key(dict(w, space="s_9"), b)                   # replayed for another space
    with pytest.raises(ValueError):
        rc.unwrap_key(dict(w, epoch=3), b)


def test_file_chunks_cant_be_reordered_or_dropped():
    k = rc.new_key()
    parts = [rc.encrypt_chunk(k, bytes([i]) * 100, "f_1", i, 3) for i in range(3)]
    assert rc.decrypt_chunk(k, parts[1], "f_1", 1, 3) == b"\x01" * 100
    with pytest.raises(Exception):
        rc.decrypt_chunk(k, parts[1], "f_1", 2, 3)
    with pytest.raises(Exception):
        rc.decrypt_chunk(k, parts[1], "f_1", 1, 2)               # a shortened file
    with pytest.raises(Exception):
        rc.decrypt_chunk(k, parts[1], "f_2", 1, 3)


def test_trust_follows_executive_approvals_to_the_founder():
    f, e2, crew, crew2, rogue = (rc.Device() for _ in range(5))
    fr = rc.device_record(f.public(), "u_f", f)
    recs = [rc.device_record(e2.public(), "u_e2", f), rc.device_record(crew.public(), "u_c", f),
            rc.device_record(crew2.public(), "u_c2", crew),            # approved by a non-executive: not trusted
            rc.device_record(rogue.public(), "u_r", rogue)]            # self-signed: not trusted
    t = rc.trusted_devices(fr, recs, [], [])
    assert set(t["devices"]) == {f.id, e2.id, crew.id}
    grant = rc.exec_grant("u_e2", True, f)
    recs.append(rc.device_record(rc.Device().public(), "u_x", e2))
    t = rc.trusted_devices(fr, recs, [grant], [])
    assert len(t["devices"]) == 4 and "u_e2" in t["execs"]
    t = rc.trusted_devices(fr, recs, [grant], [rc.revocation(crew.id, e2)])
    assert crew.id not in t["devices"]
    t = rc.trusted_devices(fr, recs, [grant], [rc.revocation(f.id, e2)])
    assert f.id in t["devices"]                                          # the founder can't be revoked
    with pytest.raises(ValueError):
        rc.trusted_devices(rc.device_record(f.public(), "u_f", e2), recs, [], [])


def test_signed_headers_are_ascii_only():
    with pytest.raises(ValueError):
        rc.canon({"name": "Timothée"})
    assert rc.canon({"b": 1, "a": [True, None, "x"]}) == b'{"a":[true,null,"x"],"b":1}'
