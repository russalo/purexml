"""04 — purexml.minidom: hardened DOM (a defusedxml.minidom drop-in).

`parse`/`parseString` return a standard `xml.dom.minidom.Document`, with the same
hardening as the ElementTree path. Migration is `s/defusedxml.minidom/purexml.minidom/`.

Run:  python examples/04_minidom.py
"""
from purexml.common import DefusedXmlException
from purexml.minidom import parseString

DOC = "<people><person name='Ada'/><person name='Alan'/></people>"


def main() -> None:
    doc = parseString(DOC)  # -> xml.dom.minidom.Document (standard stdlib object)
    for person in doc.getElementsByTagName("person"):
        print("person:", person.getAttribute("name"))

    # Same hardening as ElementTree — an entity declaration is refused.
    try:
        parseString('<!DOCTYPE d [ <!ENTITY e "x"> ]><d>&e;</d>')
        raise AssertionError("entity was not blocked")  # regression tripwire
    except DefusedXmlException as ex:
        print("blocked entity bomb:", type(ex).__name__)

    # Note: purexml.minidom is STRICTER than defusedxml on one point — passing your
    # own `parser=` raises NotSupportedError (a foreign parser would bypass the
    # hardening), rather than silently patching it. Don't pass parser=.


if __name__ == "__main__":
    main()
