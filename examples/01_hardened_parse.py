"""01 — Hardened parse: the one call that replaces defusedxml.

`purexml.ElementTree.fromstring` parses untrusted XML into a *standard*
`xml.etree.ElementTree.Element` (so your existing `.iter`/`.find`/`.get` code is
unchanged), while blocking the known XML attack classes by default — exactly as
`defusedxml` does.

Run:  python examples/01_hardened_parse.py
"""
from xml.etree.ElementTree import ParseError

from purexml.ElementTree import fromstring

BENIGN = "<order id='42'><item>widget</item><qty>3</qty></order>"

# A "billion laughs" entity-expansion bomb — would blow up memory if expanded.
BILLION_LAUGHS = (
    '<?xml version="1.0"?><!DOCTYPE lolz [ <!ENTITY lol "lol">'
    '<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
    '<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">'
    ' ]><lolz>&lol3;</lolz>'
)
# XXE — an external entity trying to read a local file.
XXE = ('<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/passwd"> ]>'
       '<r>&x;</r>')


def main() -> None:
    # 1. Benign XML parses to a standard Element — same result as the stdlib parser.
    root = fromstring(BENIGN)
    print("parsed:", root.tag, "id=", root.get("id"),
          "item=", root.findtext("item"), "qty=", root.findtext("qty"))
    assert root.tag == "order" and root.findtext("item") == "widget"

    # 2. Attacks raise a catchable exception — no expansion, no fetch, no hang.
    #    The block exceptions subclass ValueError (like defusedxml's), so
    #    `except ValueError` also catches them.
    for label, payload in [("billion-laughs", BILLION_LAUGHS), ("XXE", XXE)]:
        try:
            fromstring(payload)
            raise AssertionError(f"{label} was NOT blocked")  # regression tripwire
        except ValueError as e:
            print(f"blocked {label}: {type(e).__name__}")

    # 3. Malformed input raises the stdlib ParseError (NOT a purexml exception),
    #    unchanged — so `except ParseError` still means "bad XML", not "attack".
    try:
        fromstring("<oops>")
    except ParseError as e:
        print("malformed -> stdlib ParseError:", e)


if __name__ == "__main__":
    main()
