"""Shared fixtures + the no-fetch/no-read proof harness (RFC v0.1.0 §4.3).

`defusedxml` is the dev/test ORACLE (never a runtime dependency). If it is not
installed, the equivalence tests are skipped with a clear message rather than
silently passing.
"""
import builtins
import contextlib
import socket

import pytest

try:
    import defusedxml.ElementTree as _DET  # noqa: F401
    HAVE_ORACLE = True
except ImportError:  # pragma: no cover
    HAVE_ORACLE = False

requires_oracle = pytest.mark.skipif(
    not HAVE_ORACLE, reason="defusedxml oracle not installed (pip install -e '.[dev]')"
)

SENTINEL_CONTENT = "PUREXML-SENTINEL-DO-NOT-LEAK-7f3a"

# ---- ALLOW-path corpus: must parse, byte-identical to the oracle (C14N) ----
ALLOW_CASES = {
    "benign_no_dtd": "<r><a>x</a><b k='v'>y</b></r>",
    "benign_internal_dtd_no_entities":
        '<?xml version="1.0"?><!DOCTYPE r [ <!ELEMENT r (#PCDATA)> ]><r>ok</r>',
    "namespaced": '<root xmlns:n="urn:x" xmlns="urn:d"><n:c a="1">v</n:c><d/></root>',
    "cdata": "<r><![CDATA[<not><xml> & stuff]]></r>",
    "comment_pi": "<?xml version='1.0'?><!-- c --><?pi go?><r>t</r>",
    "predefined_entities": "<r>a &lt; b &amp; c &gt; d &quot;e&quot; &apos;f&apos;</r>",
    "str_with_encoding_decl": "<?xml version='1.0' encoding='utf-8'?><r>x</r>",
    "nested_attrs_order": "<r><a z='1' a='2' m='3'>x</a><a>y</a></r>",
    # F2: an unresolved external-DTD declaration parses and triggers NO fetch.
    "unresolved_external_dtd":
        '<?xml version="1.0"?><!DOCTYPE r SYSTEM "http://127.0.0.1:1/x.dtd"><r/>',
}

# ---- BLOCK-path corpus: must raise (purexml) exactly as the oracle raises ----
def _attack_cases(sentinel_path):
    return {
        "internal_general_entity":
            '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x "expanded"> ]><r>&x;</r>',
        "internal_param_entity":
            '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY % p "<!ENTITY q \'v\'>"> %p; ]><r/>',
        "billion_laughs":
            '<?xml version="1.0"?><!DOCTYPE lolz [ <!ENTITY lol "lol">'
            '<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
            '<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">'
            ' ]><lolz>&lol3;</lolz>',
        "xxe_local_file":
            f'<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "file://{sentinel_path}"> ]>'
            f'<r>&x;</r>',
        "xxe_network":
            '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "http://127.0.0.1:1/x"> ]>'
            '<r>&x;</r>',
        "xxe_param_external_dtd":
            f'<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY % e SYSTEM "file://{sentinel_path}"> %e; ]>'
            f'<r/>',
    }


@pytest.fixture
def sentinel_file(tmp_path):
    p = tmp_path / "secret.txt"
    p.write_text(SENTINEL_CONTENT)
    return str(p)


@pytest.fixture
def attack_cases(sentinel_file):
    return _attack_cases(sentinel_file)


class IOTouched(AssertionError):
    """Raised if a parse attempts any socket / file-open during the attack battery."""


@contextlib.contextmanager
def assert_no_io():
    """Trip-wire: replace socket + builtins.open + urllib opener with stubs that
    raise IOTouched. A hardened parse blocks before any I/O, so these are never
    hit; if one fires, IOTouched surfaces the breach (and is distinguishable from
    the expected block exception)."""
    import urllib.request

    real_socket, real_open, real_urlopen = socket.socket, builtins.open, urllib.request.urlopen

    def boom(*a, **k):
        raise IOTouched("parse attempted real I/O")

    socket.socket = boom
    builtins.open = boom
    urllib.request.urlopen = boom
    try:
        yield
    finally:
        socket.socket = real_socket
        builtins.open = real_open
        urllib.request.urlopen = real_urlopen
