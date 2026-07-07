"""05 — purexml.sax: hardened event-driven parsing (a defusedxml.sax drop-in).

`make_parser`/`parse`/`parseString` drive your own `ContentHandler`, with the same
blocking hardening installed on the reader. One thing to know: `parseString` is
BYTES-only — it mirrors defusedxml.sax exactly (a str raises TypeError on both).

Run:  python examples/05_sax.py
"""
from xml.sax.handler import ContentHandler

from purexml.common import DefusedXmlException
from purexml.sax import parseString


class Collector(ContentHandler):
    def __init__(self) -> None:
        self.elements = 0

    def startElement(self, name: str, attrs) -> None:
        self.elements += 1
        print("  start:", name, dict(attrs))


def main() -> None:
    handler = Collector()
    # parseString takes BYTES (so the parser can read the encoding declaration).
    parseString(b"<doc><a x='1'/><b>text</b></doc>", handler)
    print("elements seen:", handler.elements)

    # Same hardening — an entity declaration is refused as a purexml exception.
    try:
        parseString(b'<!DOCTYPE d [ <!ENTITY e "x"> ]><d>&e;</d>', Collector())
        print("!! entity was not blocked")
    except DefusedXmlException as ex:
        print("blocked entity bomb:", type(ex).__name__)


if __name__ == "__main__":
    main()
