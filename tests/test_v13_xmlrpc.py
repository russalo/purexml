"""v0.13 — `purexml.xmlrpc` (a lazy-import monkeypatch shim for the stdlib xmlrpc).

Different shape from the parse modules: `monkey_patch()` makes `xmlrpc.client` safe (defused
expat parser + bounded gzip). The load-bearing guarantees: (1) the defused parser blocks
entity/DTD/external attacks with purexml's exceptions; (2) the gzip-bomb cap (`MAX_DATA`) holds;
(3) **option C** — `import purexml.xmlrpc` performs NO network-capable import until `monkey_patch()`
is called (proven in a subprocess); (4) `monkey_patch`/`unmonkey_patch` round-trips cleanly.
"""
import os
import pathlib
import subprocess
import sys

import gzip
import io

import pytest

import purexml
import purexml.xmlrpc as PX


@pytest.fixture
def patched():
    """monkey_patch for the test, then ALWAYS restore — the patch mutates global xmlrpc state."""
    PX.monkey_patch()
    try:
        yield
    finally:
        PX.unmonkey_patch()


def test_monkey_patch_installs_and_restores(patched):
    import xmlrpc.client as C
    assert C.FastParser is not None  # defused parser installed
    assert C.gzip_decode is PX.defused_gzip_decode
    # idempotent re-patch is fine
    PX.monkey_patch()
    assert C.FastParser is not None


def test_unmonkey_patch_restores_default():
    PX.monkey_patch()
    PX.unmonkey_patch()
    import xmlrpc.client as C
    assert C.FastParser is None  # stdlib default


def test_unmonkey_restores_prior_fast_parser():
    # PR#34: a faithful undo restores whatever FastParser was there before (not None) —
    # so a co-installed patcher's parser survives a purexml patch/unpatch cycle.
    import xmlrpc.client as C

    PX.unmonkey_patch()  # clean baseline (_patched -> False so the next patch captures fresh)

    class _PriorParser:
        pass
    C.FastParser = _PriorParser
    try:
        PX.monkey_patch()
        assert C.FastParser is not _PriorParser  # ours installed
        PX.unmonkey_patch()
        assert C.FastParser is _PriorParser       # prior restored, NOT clobbered to None
    finally:
        C.FastParser = None  # restore stdlib default for other tests


def _defused_parser():
    # the class monkey_patch builds + installs as xmlrpc.client.FastParser
    cls = PX._build_defused_parser_cls()

    class _Target:
        def __getattr__(self, n):
            return lambda *a, **k: None
    return cls(_Target())


@pytest.mark.parametrize("xml,exc", [
    ('<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x "v"> ]><r>&x;</r>',
     purexml.EntitiesForbidden),
    ('<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/hostname"> ]><r>&x;</r>',
     purexml.EntitiesForbidden),
])
def test_defused_xmlrpc_parser_blocks(xml, exc):
    p = _defused_parser()
    with pytest.raises(exc):
        p.feed(xml)
        p.close()


def test_defused_xmlrpc_parser_forbid_dtd():
    cls = PX._build_defused_parser_cls()

    class _T:
        def __getattr__(self, n):
            return lambda *a, **k: None
    p = cls(_T(), forbid_dtd=True)
    with pytest.raises(purexml.DTDForbidden):
        p.feed('<?xml version="1.0"?><!DOCTYPE r [ <!ELEMENT r (#PCDATA)> ]><r>ok</r>')
        p.close()


def test_defused_xmlrpc_parser_backstops():
    cls = PX._build_defused_parser_cls()

    class _T:
        def __getattr__(self, n):
            return lambda *a, **k: None

    # NDATA unparsed entity -> UnparsedEntityDeclHandler backstop.
    p = cls(_T())
    with pytest.raises(purexml.EntitiesForbidden):
        p.feed('<?xml version="1.0"?><!DOCTYPE r [ <!NOTATION g SYSTEM "g">'
               '<!ENTITY pic SYSTEM "file:///etc/hostname" NDATA g> ]><r/>')
        p.close()
    # forbid_entities=False -> the external-ref handler is the backstop on resolution.
    p2 = cls(_T(), forbid_entities=False)
    with pytest.raises(purexml.ExternalReferenceForbidden):
        p2.feed('<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/hostname"> ]>'
                '<r>&x;</r>')
        p2.close()


# -- gzip-bomb defense ----------------------------------------------------------------

def test_gzip_decode_roundtrips_normal():
    payload = b"hello world" * 10
    assert PX.defused_gzip_decode(gzip.compress(payload)) == payload


def test_gzip_decode_bomb_blocked():
    # a tiny gzip that decompresses past the limit must raise (decompression-bomb cap).
    bomb = gzip.compress(b"A" * 5000)
    with pytest.raises(ValueError, match="max gzipped payload length exceeded"):
        PX.defused_gzip_decode(bomb, limit=1000)
    # negative limit = unbounded (explicit opt-out)
    assert PX.defused_gzip_decode(bomb, limit=-1) == b"A" * 5000


def test_gzip_decode_invalid_data_raises_valueerror():
    # PR#34 Codex: malformed gzip must surface as ValueError (not gzip.BadGzipFile), so
    # xmlrpc.server's request handler returns 400 instead of letting it escape.
    with pytest.raises(ValueError, match="invalid data"):
        PX.defused_gzip_decode(b"not gzip at all")


def test_gzip_response_read_default_negative_n_is_bounded():
    # PR#34 (Gemini security-high / Codex): `read()` with the file-like default n=-1 must NOT
    # decompress the whole stream — it caps to the limit. Within the cap it returns; past it,
    # it raises having read at most left+1 (never the full bomb).
    cls = PX._build_gzip_response_cls()
    gzipped = gzip.compress(b"A" * 5000)
    r = cls(io.BytesIO(gzipped), limit=10_000)
    assert r.read(-1) == b"A" * 5000          # within cap: default read works
    r.close()
    r2 = cls(io.BytesIO(gzipped), limit=100)  # over cap: default read raises, bounded
    with pytest.raises(ValueError, match="max payload length exceeded"):
        r2.read(-1)
    r2.close()


def test_gzip_decoded_response_bounds_payload():
    cls = PX._build_gzip_response_cls()
    gzipped = gzip.compress(b"A" * 5000)
    # the response wrapper rejects at construction when the compressed length exceeds the cap
    with pytest.raises(ValueError, match="max payload length exceeded"):
        cls(io.BytesIO(gzipped), limit=10)
    # within the cap it reads back the data
    r = cls(io.BytesIO(gzipped), limit=100_000)
    assert r.read(5000) == b"A" * 5000
    r.close()


# -- option C: the lazy-import guarantee (the crux) -----------------------------------

def test_import_is_lazy_no_network():
    # In a FRESH interpreter: importing purexml.xmlrpc must NOT pull the network-capable
    # transport (xmlrpc.client) into sys.modules; only an explicit monkey_patch() does.
    code = (
        "import sys, purexml.xmlrpc as PX\n"
        "assert 'xmlrpc.client' not in sys.modules, 'transport imported at import time!'\n"
        "PX.monkey_patch()\n"
        "assert 'xmlrpc.client' in sys.modules, 'monkey_patch did not import the transport'\n"
        "print('LAZY-OK')\n"
    )
    # the fresh subprocess doesn't inherit pytest's `pythonpath = src`, so pass the src dir
    # explicitly — works in a source checkout AND an installed package (PR#34 Codex).
    src = str(pathlib.Path(purexml.__file__).resolve().parent.parent)
    env = {**os.environ, "PYTHONPATH": src + os.pathsep + os.environ.get("PYTHONPATH", "")}
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr
    assert "LAZY-OK" in out.stdout


# -- oracle parity --------------------------------------------------------------------

@pytest.mark.parametrize("xml", [
    '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x "v"> ]><r>&x;</r>',
])
def test_block_parity_with_oracle(xml):
    defusedxml = pytest.importorskip("defusedxml.xmlrpc")
    from defusedxml.common import DefusedXmlException

    class _T:
        def __getattr__(self, n):
            return lambda *a, **k: None

    # purexml refuses with a PureXMLError; defusedxml with a DefusedXmlException — same block.
    pp = PX._build_defused_parser_cls()(_T())
    with pytest.raises(purexml.PureXMLError):
        pp.feed(xml)
        pp.close()
    dp = defusedxml.DefusedExpatParser(_T())
    with pytest.raises(DefusedXmlException):
        dp.feed(xml)
        dp.close()
