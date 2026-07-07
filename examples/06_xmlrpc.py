"""06 — purexml.xmlrpc: harden the stdlib xmlrpc (a defusedxml.xmlrpc drop-in).

Unlike the parse-function modules, this one is a MONKEYPATCH (mirroring
defusedxml.xmlrpc): `monkey_patch()` swaps a defused expat parser + a bounded-gzip
decode onto `xmlrpc.client`/`server`; `unmonkey_patch()` restores the originals.
The gzip bound (`MAX_DATA`) is an anti-decompression-bomb cap.

Importing purexml does NOT pull the network transport — the xmlrpc/gzip imports are
lazy, inside monkey_patch(). Run:  python examples/06_xmlrpc.py
"""
import xmlrpc.client

from purexml.xmlrpc import MAX_DATA, monkey_patch, unmonkey_patch

RESPONSE = ("<?xml version='1.0'?><methodResponse><params><param>"
            "<value><int>7</int></value></param></params></methodResponse>")


def main() -> None:
    print("gzip decompression-bomb cap (MAX_DATA):", MAX_DATA, "bytes")

    monkey_patch()  # install the defused parser + bounded gzip onto stdlib xmlrpc
    try:
        # xmlrpc.client now parses responses with purexml's hardened parser, and
        # bounds a gzip-encoded response to MAX_DATA instead of expanding it.
        (value,), method = xmlrpc.client.loads(RESPONSE)
        print("parsed xmlrpc response value:", value, "method:", method)
        assert value == 7
    finally:
        unmonkey_patch()  # ALWAYS restore — leaves the stdlib exactly as found
    print("restored stdlib xmlrpc (unpatched)")


if __name__ == "__main__":
    main()
