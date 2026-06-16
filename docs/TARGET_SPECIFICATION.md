# purexml — Target Specification

> **Status: TARGET (capability spec).** Authored by the file-observer instance as the
> consumer-side contract + north star. It states the **capabilities** this project must
> deliver and the bar they must clear — **not how to build them.** Implementation (which
> stdlib mechanism, how the hardening is configured) belongs to this project's own
> instance. The name `purexml` is provisional — rename freely.

## 1. Purpose

Provide a **pure-Python, zero-runtime-dependency** capability to **safely parse untrusted
XML**, so that downstream consumers can drop the third-party `defusedxml` dependency **with
zero functionality loss** — same parses succeed, same attacks are blocked.

This is the cleanest kind of replacement: `defusedxml` is not an open-ended parser — it is
a **closed set of hardening behaviors** layered on the standard library's own XML parser.
The capability here is to deliver those same protections on the stdlib, directly.

The anchor consumer is **file-observer** (it parses OOXML `docProps/*.xml`, spreadsheet
XML, and arbitrary `.xml` files through a hardened parse).

## 2. Capabilities required (WHAT, not HOW)

- **C1 — Safe parse.** Given an XML document (untrusted), parse it using only the standard
  library and return the **same parse result a consumer would get from the stdlib parser**
  (an `xml.etree.ElementTree.Element`, so existing `.iter()`/`.find()` consumer code is
  unchanged), **while blocking the known XML attack classes** (§3) by default.
- **C2 — Safe failure.** When input triggers a blocked attack class (or is malformed),
  **raise a clear, catchable error** — never expand a bomb, fetch an external resource, or
  hang. The consumer catches and degrades, exactly as it does today.

The capability is *behavioral equivalence to `defusedxml`'s safe parse*, on the stdlib.
Which stdlib hooks deliver it is this project's to choose.

## 3. Attack classes that MUST be blocked (the closed set)

These are the threats `defusedxml` exists to stop; purexml must stop the same:

- **Entity-expansion bombs** ("billion laughs" / quadratic blowup).
- **External entity resolution (XXE)** — no fetching `SYSTEM`/`PUBLIC` external entities,
  local files, or network resources.
- **External DTD retrieval.**
- (Any other mitigation `defusedxml` applies on the path the consumer uses — enumerate and
  match it; this is a *finite, knowable* list, which is what makes this a clean kill.)

## 4. Quality bar (binding)

- **Zero runtime dependencies** — standard library only. (`defusedxml` may be a *dev/test*
  oracle.)
- **Deterministic** — identical input → identical parse result / identical error class.
- **Never-crash / bounded for the consumer** — a blocked or malformed input yields a
  **catchable exception**, never an unhandled crash of the host process, never unbounded
  CPU/memory, never an outbound fetch.
- **Runtime: CPython, floor as low as practical.** Match the anchor consumer's Python floor
  but stay permissive (≥3.8 is feasible); PyPy-portable. Must **never become the binding
  Python floor** for a consumer. **Implementation caveat:** the hardening assumes CPython's
  stdlib `expat` (`pyexpat`, what `xml.etree`/`defusedxml` build on). On a runtime *without*
  pyexpat (IronPython's .NET parser, some restricted builds) this capability would need a
  separate code path — **IronPython/Jython are out of scope** (no .NET/JVM consumer exists),
  but record the pyexpat assumption explicitly.

## 5. Consumer contract — what file-observer needs (the adoption test)

file-observer's entire surface is **one call**: a `fromstring(text) -> Element` that is
hardened, replacing `defusedxml.ElementTree.fromstring`. It then uses the returned standard
`Element` via `.iter(tag)`. So the consumer contract is:

| Need | Capability |
|---|---|
| "Parse this (untrusted) XML text safely into a standard Element." | C1 |
| "If it's an entity bomb / has external entities / is malformed, raise — don't expand, fetch, or hang." | C2 / §3 |
| The returned object must behave as `xml.etree.ElementTree.Element` (`.iter`, `.find`, namespaced tags). | C1 |

file-observer adopts when this one hardened-`fromstring` capability passes §6.

## 6. Acceptance bar — oracle-gated equivalence

Validate against the incumbent (`defusedxml`) as an oracle:

- **Same successful parses** — across a corpus of real XML (file-observer can supply OOXML
  parts + assorted `.xml`), purexml's parse result MUST match `defusedxml`'s for every
  document that parses, on the consumer surface (the resulting element tree).
- **Same attacks blocked** — a falsify-first battery of the §3 attack classes (entity
  bombs, XXE with local-file + network targets, external DTDs) MUST be **blocked by
  purexml exactly as `defusedxml` blocks them** (raises, no expansion, no fetch). Prove it
  with adversarial inputs, not assertions.
- The oracle is a **dev/test aid only**, never shipped.

## 7. Adoption model (informs packaging)

Produce a **self-contained, vendorable** unit. Either path stays open:
- **Vendor** into file-observer → its core gains hardened XML with zero runtime deps
  (file-observer's leaning).
- **First-party dependency** — pure-Python, no native build.

## 8. Note on owning a security capability

Unlike a format reader, this capability **is a security control.** Reimplementing
hardening means *owning* it — the audit/maintenance burden `defusedxml` otherwise absorbs.
That is an accepted, deliberate cost of removing the dependency; it raises the bar on the
§6 adversarial battery (it must be thorough and kept current with new XML attack research),
and it is the reason this capability is worth doing carefully rather than quickly.

## 9. Roadmap framing

Delivered via minor releases, measure-first and oracle-gated. The first slice is in
`docs/v0.1.0_RFC_Specification.md`. file-observer adopts once the §5 contract passes §6.
