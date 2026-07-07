"""02 — Migrating off defusedxml: it's a literal `s/defusedxml/purexml/`.

purexml mirrors defusedxml's public surface AND its defaults, so migration is a
find-and-replace of the import path — no logic change. This script shows the two
import lines that change and proves your existing try/except transfers verbatim.

Run:  python examples/02_migrate_from_defusedxml.py
"""
# BEFORE:  from defusedxml.ElementTree import fromstring
# AFTER:   from purexml.ElementTree  import fromstring
from purexml.ElementTree import fromstring

# BEFORE:  from defusedxml.common import DefusedXmlException
# AFTER:   from purexml.common  import DefusedXmlException
from purexml.common import DefusedXmlException

# An external-entity (XXE) probe — e.g. an SSRF at a cloud metadata endpoint.
XXE = ('<?xml version="1.0"?>'
       '<!DOCTYPE r [ <!ENTITY x SYSTEM "http://169.254.169.254/latest/meta-data/"> ]>'
       '<r>&x;</r>')


def load(xml: str):
    """Your existing defusedxml handler — unchanged. `DefusedXmlException` is the
    base class purexml.common re-exports (aliased to purexml's own base), and every
    block exception keeps defusedxml's name and its ValueError MRO position."""
    try:
        return fromstring(xml)
    except DefusedXmlException as e:
        print(f"  refused ({type(e).__name__}) — degrade gracefully")
        return None


def main() -> None:
    print("benign:")
    print("  text =", load("<greeting>hi</greeting>").text)
    print("hostile:")
    load(XXE)
    # Defaults match defusedxml exactly: forbid_entities=True, forbid_external=True,
    # forbid_dtd=False. Nothing about your call sites changes — only the import path.
    print("done — the only edit was the import path.")


if __name__ == "__main__":
    main()
