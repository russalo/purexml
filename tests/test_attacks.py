"""Acceptance bar §4.2–§4.3 — falsify-first attack battery + no-I/O proof.

Each attack MUST be blocked by purexml exactly as defusedxml blocks it (both
raise), the refusal MUST be a ValueError subclass, and — proven, not asserted —
the parse MUST perform no socket / file-open / urlopen, and the sentinel file's
contents MUST never appear in any output.
"""
import pytest

import purexml
from conftest import (
    SENTINEL_CONTENT,
    IOTouched,
    assert_no_io,
    requires_oracle,
)


def test_blocks_raise_valueerror_subclass(attack_cases):
    for name, text in attack_cases.items():
        with pytest.raises(ValueError) as exc:  # PureXMLError is a ValueError
            purexml.fromstring(text)
        assert isinstance(exc.value, purexml.PureXMLError), name


@requires_oracle
def test_block_parity_with_oracle(attack_cases):
    """purexml raises iff defusedxml raises — for every attack input."""
    import defusedxml.ElementTree as DET
    from defusedxml.common import DefusedXmlException

    for name, text in attack_cases.items():
        with pytest.raises(DefusedXmlException):
            DET.fromstring(text)
        with pytest.raises(purexml.PureXMLError):
            purexml.fromstring(text)


def test_no_io_during_attacks(attack_cases):
    """Proof harness: blocked before any real I/O (RFC §4.3)."""
    for name, text in attack_cases.items():
        with assert_no_io():
            with pytest.raises(purexml.PureXMLError):
                purexml.fromstring(text)
            # If a stub had fired it would raise IOTouched, not PureXMLError.


def test_sentinel_never_leaks(attack_cases):
    """The local-file XXE target's contents never reach any parse output."""
    for name, text in attack_cases.items():
        try:
            elem = purexml.fromstring(text)
        except purexml.PureXMLError:
            continue
        import xml.etree.ElementTree as ET

        assert SENTINEL_CONTENT not in ET.tostring(elem, encoding="unicode"), name


def test_io_trip_wire_actually_fires():
    """Sanity-check the harness itself: a real open() under assert_no_io raises."""
    with pytest.raises(IOTouched):
        with assert_no_io():
            open("/dev/null")  # noqa: SIM115


def test_billion_laughs_blocked_at_declaration(attack_cases):
    """Blocked proactively (no expansion), independent of libexpat's cap."""
    with assert_no_io():
        with pytest.raises(purexml.EntitiesForbidden):
            purexml.fromstring(attack_cases["billion_laughs"])
