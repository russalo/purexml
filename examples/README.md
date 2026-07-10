# purexml examples

Runnable, self-contained scripts — each is a single `python examples/NN_*.py` you
can copy, run, and adapt. They use only the standard library plus purexml (zero
third-party dependencies), and every one exits 0.

## Running them

```bash
pip install purexml
python examples/01_hardened_parse.py

# Or, from a clone (to run against your local checkout):
pip install -e .
python examples/01_hardened_parse.py
```

Or run the whole set:

```bash
for f in examples/0*.py; do echo "== $f =="; python "$f"; done
```

## The examples

| # | File | What it shows |
|---|------|---------------|
| 01 | [`01_hardened_parse.py`](01_hardened_parse.py) | The one call — `fromstring` parses benign XML to a standard `Element`, blocks a billion-laughs bomb and an XXE (catchable `ValueError`), and passes malformed input through as the stdlib `ParseError`. |
| 02 | [`02_migrate_from_defusedxml.py`](02_migrate_from_defusedxml.py) | Migration is a literal `s/defusedxml/purexml/` — the two import lines that change, and proof your existing `except DefusedXmlException` handler transfers unchanged. |
| 03 | [`03_elementtree_family.py`](03_elementtree_family.py) | The full `ElementTree` surface: `fromstring`, `fromstringlist`, `parse` (file), `iterparse` (streaming), and the re-exported `tostring`. |
| 04 | [`04_minidom.py`](04_minidom.py) | `purexml.minidom` — hardened DOM returning a standard `xml.dom.minidom.Document`. |
| 05 | [`05_sax.py`](05_sax.py) | `purexml.sax` — event-driven parsing with your own `ContentHandler`; note `parseString` is **bytes-only** (mirrors defusedxml). |
| 06 | [`06_xmlrpc.py`](06_xmlrpc.py) | `purexml.xmlrpc` — the monkeypatch shim: `monkey_patch()`/`unmonkey_patch()` install a defused parser + a bounded-gzip (anti-decompression-bomb) decode onto the stdlib `xmlrpc`. |
| 07 | [`07_limits.py`](07_limits.py) | Opt-in structural-DoS caps (`Limits` / `RECOMMENDED_LIMITS`) — **default-off**, so the strict mirror is unchanged until you pass `limits=`. |
| 08 | [`08_security_posture.py`](08_security_posture.py) | `security_report()` — a read-only map of what each XML attack class is protected by **on this runtime** (purexml's handlers, your libexpat version, or an opt-in cap). Also `python -m purexml`. |

## The two things to take away

1. **Default = strict `defusedxml` mirror.** Every default-path call blocks the same
   attacks defusedxml blocks (entity bombs, XXE, external-DTD retrieval) and returns
   the same standard stdlib objects. Migration changes only the import path.
2. **Everything beyond the mirror is opt-in.** `Limits` (structural-DoS caps) and
   `security_report()` (posture visibility) are off/read-only by default — you get a
   clean drop-in until you deliberately ask for more.

For the module-by-module migration reference, see
[`../docs/MIGRATING.md`](../docs/MIGRATING.md).
