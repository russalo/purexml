"""v0.7 — the `python -m purexml` posture CLI.

Read-only over security_report(): informs by default (exit 0); --check is an opt-in
gate. Tests the flag matrix, the JSON shape, and the exit-code gating (monkeypatching
the module-global EXPAT_VERSION, which both the CLI and security_report() read at call
time, so they stay consistent).
"""
import json

import pytest

import purexml
from purexml import _expat_security as S
from purexml.__main__ import main


def test_as_dict_is_json_safe_and_complete():
    d = purexml.security_report().as_dict()
    s = json.dumps(d)  # must not raise
    back = json.loads(s)
    assert set(back) == {"expat_version", "expat_meets_safe_floor",
                         "expat_meets_recommended", "recommended_limits",
                         "mitigations", "notes"}
    assert isinstance(back["expat_version"], str)          # tuple → "x.y.z"
    assert isinstance(back["mitigations"], dict)           # mappingproxy → dict
    assert isinstance(back["notes"], list)                 # tuple → list
    assert set(back["recommended_limits"]) == {"max_depth", "max_attributes", "max_bytes"}
    # round-trips the live data
    assert back["expat_version"] == ".".join(map(str, purexml.EXPAT_VERSION))


def test_default_prints_report_exit_zero(capsys):
    rc = main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "purexml security posture" in out


def test_json_flag_emits_valid_json_with_version(capsys):
    rc = main(["--json"])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["purexml_version"] == purexml.__version__
    assert "mitigations" in payload and "expat_version" in payload


def test_version_flag(capsys):
    rc = main(["--version"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "purexml %s" % purexml.__version__ in out
    assert "libexpat" in out


def test_check_default_floor_passes_when_at_or_above(monkeypatch, capsys):
    monkeypatch.setattr(S, "EXPAT_VERSION", S.RECOMMENDED_EXPAT_VERSION)
    assert main(["--check"]) == 0
    # still prints the report (so the user sees why), to stdout
    assert "purexml security posture" in capsys.readouterr().out


def test_check_default_floor_fails_when_below(monkeypatch, capsys):
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 6, 0))  # below recommended 2.8.1
    assert main(["--check"]) == 1
    err = capsys.readouterr().err
    assert "FAIL" in err and "below the required floor" in err


def test_check_min_expat_pins_floor(monkeypatch):
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 7, 0))
    # below recommended (2.8.1) — but the caller pins a lower explicit floor → passes
    assert main(["--check", "--min-expat", "2.6.0"]) == 0
    # and a higher explicit pin → fails
    assert main(["--check", "--min-expat", "2.9.0"]) == 1


def test_check_json_combo_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 6, 0))
    rc = main(["--check", "--json"])
    assert rc == 1
    out = capsys.readouterr().out
    json.loads(out)  # the JSON still emits on stdout regardless of the gate result


def test_malformed_min_expat_errors(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--check", "--min-expat", "not-a-version"])
    assert exc.value.code != 0  # argparse error exit (2)


def test_min_expat_without_check_errors(capsys):
    # --min-expat without --check would silently no-op (exit 0); for a security gate
    # that's a footgun — must fail loudly instead (PR#15 Gemini).
    with pytest.raises(SystemExit) as exc:
        main(["--min-expat", "2.8.1"])
    assert exc.value.code != 0
