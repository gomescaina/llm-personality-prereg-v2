import parser as P
import scoring as S


def test_parse_ipip_basic():
    text = "1 = 3\n2 = 4\n3 = 5\n"
    parsed, dropped, oor, n = P.parse_ipip(text, [1, 2, 3])
    assert parsed == {1: 3, 2: 4, 3: 5}
    assert dropped == []
    assert oor == []


def test_parse_out_of_range():
    text = "1 = 9\n2 = 2\n"
    parsed, dropped, oor, n = P.parse_ipip(text, [1, 2])
    assert 1 not in parsed
    assert parsed[2] == 2
    assert len(oor) == 1


def test_parse_dropped_items():
    text = "1 = 2\n"
    parsed, dropped, oor, n = P.parse_pid5(text, [1, 2, 3])
    assert dropped == [2, 3]


def test_looks_like_list_drift():
    assert not P.looks_like_list("Hello world", 10)
    text = "\n".join(f"{i} = 2" for i in range(1, 11))
    assert P.looks_like_list(text, 10)


def test_score_ipip_domain():
    from instruments import ipip_key
    responses = {r["num"]: 3 for r in ipip_key.ITEMS}
    scored = S.score_ipip(responses)
    assert scored["domains"]["N"]["computable"]


def test_score_pid5_validity_keys():
    responses = {i: 1 for i in range(1, 221)}
    scored = S.score_pid5(responses)
    assert "VRIN" in scored["validity"]
    assert "PRD" in scored["validity"]


def test_score_csiv_metrics():
    from instruments import csiv_key
    responses = {n: 2 for n in csiv_key.ITEMS}
    scored = S.score_csiv(responses)
    assert scored["metrics"]["R2"] is not None
    assert "AGENTIC" in scored["metrics"]
