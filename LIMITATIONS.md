# Limitations

purexml does one thing — safely parse untrusted XML, behaviorally equivalent to
`defusedxml.ElementTree`. This document states plainly what it does **not** do.

## It is the `ElementTree` family — not all of defusedxml, not a writer

As of v0.3, purexml mirrors `defusedxml.ElementTree`'s full surface (`fromstring`,
`parse`, `iterparse`, `fromstringlist`, `XML`, `XMLParser`, `tostring`, the
`forbid_*` knobs). It does **not** provide:
- the **other defusedxml submodules** — `minidom`, `sax`, `pulldom`,
  `expatreader`/`expatbuilder`, `xmlrpc`, the deprecated `lxml` shim. Deferred,
  not excluded — added post-1.0 only if a consumer needs them (`docs/ROADMAP-to-1.0.md`);
- any XML **writing** / serialization beyond re-exporting stdlib `tostring` — it
  is a hardened *reader*;
- a non-pyexpat code path — see *Threat model* (IronPython/Jython out of scope).

(The `forbid_*` knobs were re-opened for the general-replacement scope at v0.2 —
defaults match defusedxml; `forbid_dtd=True` is OWASP's stricter DTD-disable mode.)

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
