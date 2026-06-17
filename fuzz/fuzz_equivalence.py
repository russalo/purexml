"""Coverage-guided differential fuzz harness — purexml vs the defusedxml oracle.

DEV-ONLY, opt-in (v0.5 RFC §3/§4). Atheris (libFuzzer) drives input mutation
*by coverage*, reaching parser states the seeded generator
(`tests/test_fuzz_equivalence.py`) never enumerates. Same invariant as the seeded
gate — **C14N-equal-or-both-raise** vs defusedxml — but explored adversarially.

Atheris is NEVER a runtime dependency and is never imported under ``src/``; this
file lives outside the package. Install the extra and run on demand::

    pip install -e '.[fuzz]'
    python fuzz/fuzz_equivalence.py -atheris_runs=2000000        # bounded run
    python fuzz/fuzz_equivalence.py corpus/                      # replay a corpus

A divergence (different parse-vs-raise kind, or different canonical tree) aborts
with the offending input — that is a real equivalence break to triage against the
code (grounding rule), not a fuzzer artifact.
"""
import sys

import atheris

# Import everything under test INSIDE the instrumentation block so Atheris gets
# coverage feedback from purexml's parser logic AND the xml.etree TreeBuilder /
# canonicalize path used in the diff below. Importing any of these at module top
# would cache it in sys.modules uninstrumented, blinding the fuzzer to that code.
with atheris.instrument_imports():
    import xml.etree.ElementTree as ET
    import purexml
    import defusedxml.ElementTree as DET


def _kind(fn, data):
    """('parse', canonical-C14N) on success, ('raise', None) on any exception.

    Only the parse-vs-raise *kind* and the canonical tree are compared — exception
    *types* differ by design (purexml has its own hierarchy)."""
    try:
        return ("parse", ET.canonicalize(ET.tostring(fn(data), encoding="unicode")))
    except Exception:  # noqa: BLE001 — kind, not type, is the contract
        return ("raise", None)


def _one_input(data):
    pk = _kind(purexml.fromstring, data)
    dk = _kind(DET.fromstring, data)
    if pk[0] != dk[0]:
        raise AssertionError(
            "parse/raise divergence: purexml=%s defusedxml=%s input=%r"
            % (pk[0], dk[0], data))
    if pk[0] == "parse" and pk[1] != dk[1]:
        raise AssertionError("C14N divergence on input=%r" % (data,))


def TestOneInput(raw):
    # Feed both the raw bytes and a decoded str — purexml accepts both, and the
    # str path exercises the encoding-declaration handling the bytes path skips.
    _one_input(raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return
    _one_input(text)


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
