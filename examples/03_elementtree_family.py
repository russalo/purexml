"""03 — The full defusedxml.ElementTree family, hardened.

purexml.ElementTree covers the whole surface, not just fromstring:
`fromstring`, `fromstringlist`, `parse` (from a file), `iterparse` (streaming),
`XMLParser`, and the stdlib `tostring` (re-exported for drop-in convenience).

Run:  python examples/03_elementtree_family.py
"""
import os
import tempfile

from purexml.ElementTree import (
    fromstring,
    fromstringlist,
    iterparse,
    parse,
    tostring,
)

DOC = "<catalog><book id='1'>Widgets</book><book id='2'>Gadgets</book></catalog>"


def main() -> None:
    # fromstringlist — parse from a sequence of chunks (e.g. streamed bytes).
    root = fromstringlist(["<cat", "alog><book id='9'>x", "</book></catalog>"])
    print("fromstringlist:", root.tag, [b.get("id") for b in root.iter("book")])

    # parse() + iterparse() work on files — write a temp one to demo them.
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(DOC)
        path = f.name
    try:
        tree = parse(path)  # hardened ElementTree
        print("parse:", [b.get("id") for b in tree.getroot().iter("book")])

        # iterparse — hardened streaming for large documents.
        for _event, elem in iterparse(path):
            if elem.tag == "book":
                print("  iterparse book:", elem.get("id"), "->", elem.text)
    finally:
        os.unlink(path)

    # tostring is the stdlib serializer, re-exported so `s/defusedxml/purexml/`
    # covers it too (purexml is parse-only; this is just the stdlib function).
    print("tostring:", tostring(fromstring("<x a='1'/>"), encoding="unicode"))


if __name__ == "__main__":
    main()
