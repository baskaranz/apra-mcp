"""Tests for the white-box / code-aware analyzer."""

import pytest

from src.code_auditor.analyzer import analyze_fixture, analyze_scope, FIXTURES


def _by_id(report, fid):
    return next((f for f in report["findings"] if f["id"] == fid), None)


def test_wild_banking_is_critical_with_hardcoded_pii():
    r = analyze_fixture("wild-banking")
    assert r["code_posture"] == "CRITICAL"
    pii = _by_id(r, "hardcoded_pii")
    assert pii["status"] == "EXPOSURE"
    assert pii["evidence"], "should cite a file:line for the hardcoded PII"
    assert pii["evidence"][0]["line"] > 0
    # unauthorised commitment path with no gate
    assert _by_id(r, "delegation_killswitch")["status"] == "CONTROL_MISSING"


def test_hardened_banking_has_no_exposures():
    r = analyze_fixture("hardened-banking")
    assert r["summary"]["exposures"] == 0
    # its "controls" are refusal text, not verified enforcement
    assert _by_id(r, "hardcoded_pii")["status"] != "EXPOSURE"


def test_runtime_guardrail_verifies_audit_wiring():
    r = analyze_fixture("runtime-guardrail")
    audit = _by_id(r, "audit_logging")
    assert audit["status"] == "CONTROL_VERIFIED"
    assert audit["evidence"]


def test_missing_vs_unverifiable_distinction():
    # hardened bot has no audit call -> UNVERIFIABLE_LOCALLY, not a hard MISSING
    r = analyze_fixture("hardened-banking")
    assert _by_id(r, "audit_logging")["status"] == "UNVERIFIABLE_LOCALLY"


def test_unknown_fixture_raises():
    with pytest.raises(ValueError):
        analyze_fixture("nope")


def test_scope_not_found_raises():
    with pytest.raises(ValueError):
        analyze_scope("src/tools/blackbox_prober.py", "NoSuchClass")


def test_every_fixture_returns_wellformed_report():
    for name in FIXTURES:
        r = analyze_fixture(name)
        assert set(["target", "code_posture", "summary", "findings"]) <= r.keys()
        for f in r["findings"]:
            assert f["standard"] in ("CPS 230", "CPS 234")
            assert f["status"] in (
                "EXPOSURE", "CONTROL_VERIFIED", "CONTROL_INDICATOR",
                "CONTROL_MISSING", "UNVERIFIABLE_LOCALLY",
            )
