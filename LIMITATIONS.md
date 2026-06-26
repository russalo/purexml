# Limitations

purexml does one thing — safely parse untrusted XML, behaviorally equivalent to
`defusedxml.ElementTree`. This document states plainly what it does **not** do.

## It is the `ElementTree` family + `minidom` + `sax` — not yet all of defusedxml, not a writer

purexml mirrors `defusedxml.ElementTree`'s full surface (`fromstring`, `parse`, `iterparse`,
`fromstringlist`, `XML`, `XMLParser`, `tostring`, the `forbid_*` knobs) and, by measured demand
(`docs/ROADMAP-to-1.0.md`), **`defusedxml.minidom`** (v0.10), **`defusedxml.sax`** +
**`.expatreader`** (v0.12), and `defusedxml.common` (the `DefusedXmlException` catch alias). It
does **not** (yet) provide:
- the **remaining defusedxml submodules** — `xmlrpc` (a distinct monkeypatch-the-stdlib shape,
  TBD), `pulldom` (deferred, measured-negligible). The deprecated **`lxml`** shim is **excluded**
  — it wraps the third-party `lxml` library, which would break purexml's zero-dependency,
  stdlib-only contract;
- any XML **writing** / serialization beyond re-exporting stdlib `tostring` — it
  is a hardened *reader*;
- a non-pyexpat code path — see *Threat model* (IronPython/Jython out of scope).

(The `forbid_*` knobs were re-opened for the general-replacement scope at v0.2 —
defaults match defusedxml; `forbid_dtd=True` is OWASP's stricter DTD-disable mode.)

Beyond the mirror it adds two **opt-in, default-off** capabilities `defusedxml`
lacks: structural-DoS caps (`Limits`, v0.4) and a read-only posture report
(`security_report()`, v0.5). Neither changes default parse behavior — see the next
section. The posture report is **informational only**: it does not parse, fetch, or
hard-fail, and the enforce-vs-warn policy for the libexpat-version floor is deferred
to 1.0 (it currently *informs*, never enforces).

## It is equivalence, not "maximum strictness"

The contract is *behavioral equivalence to `defusedxml.ElementTree.fromstring` at
its defaults* — **matching the oracle's allow behavior is as much the contract as
matching its block behavior.** Specifically, purexml deliberately **allows**:
- an entity-free DOCTYPE / internal DTD;
- an **unresolved** external-DTD declaration (it parses and triggers *no fetch* —
  only *attempted* external resolution is blocked).

"purexml allows X" is only a defect if `defusedxml` *blocks* X on the same path.
Do not "harden" purexml past the oracle — over-blocking breaks the equivalence
contract and the consumer's parses.

The **one sanctioned divergence** is opt-in: passing `Limits` (v0.4) makes purexml
reject pathological-but-legal structural input (`LimitExceeded`) that `defusedxml`
would accept. This is *by design* and only when the caller asks — with the default
`limits=None`, purexml stays byte-equivalent to the oracle. The equivalence sweep
runs at the default (no limits), so it measures the mirror, not the opt-in mode.

## Threat model

- **Input is fully untrusted** — arbitrary XML text/bytes of unknown origin. The
  **caller is trusted**; the XML is the attacker-controlled surface. There is no
  network or auth dimension — it is a library call, not a service.
- **Blocked (raising a catchable error, no expansion/fetch/read/hang/crash):**
  entity-expansion bombs (billion-laughs / quadratic), XXE via external entities
  (local file + network), external reference resolution. Blocking is **proactive
  at the entity declaration**, independent of the system libexpat version.
- **Out of scope:** runtimes without CPython's `pyexpat` (IronPython/Jython —
  the .NET/JVM XML parsers would need a separate code path); supply-chain attacks
  (there are no runtime dependencies to attack); side-channel/timing attacks;
  OS-level exploits.
- **Never crashes the host:** a malicious or malformed input yields a *catchable
  exception* (`PureXMLError` subclass, or stdlib `ParseError` for malformed),
  never an aborted process, unbounded CPU/memory, or an outbound fetch.

## Accepted limitations

- **Owning a security control.** Reimplementing `defusedxml`'s hardening means
  *owning* the audit/maintenance burden it otherwise absorbs (target spec §8).
  Accepted deliberately as the cost of removing the dependency; mitigated by the
  falsify-first battery + oracle-gated equivalence sweep, which must be kept
  current with new XML-attack research.
- **`ExternalReferenceForbidden` is an untriggered backstop.** With entity
  declarations blocked, external references are caught at the declaration before
  resolution is attempted, so this exception is essentially unreachable under the
  fixed config. Kept as defense-in-depth, mirroring defusedxml's handler. Revisit
  if a parse mode is added that can reach external resolution directly.
- **Runtime floor is 3.10, though ≥3.8 is technically feasible.** Lower floors
  are untested here (only 3.10–3.13 are CI-grounded). Revisit if a consumer needs
  a lower floor *and* it can be added to the CI matrix.
