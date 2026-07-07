# purexml — file-observer Required Compatibility (the 1.0 consumer floor)

> **Status: Consumer floor (binding).** Authored by the file-observer (FO) instance as
> *the minimum FO requires to adopt purexml* — the compatibility purexml must always
> satisfy for its anchor consumer. This is the **floor, not the ceiling**: FO's required
> capabilities + the bar they clear, not how to build them, and not the whole of what
> purexml is. (Originally "Target Specification"; renamed 2026-06-16 — it was always FO's
> required-compat contract, and purexml's own 1.0 aspiration is a strict superset.)

> **Where the wider 1.0 lives.** purexml has grown well past this floor — it is now the
> complete `defusedxml.ElementTree` drop-in **plus the measured breadth surface**
> (`minidom`/`common` v0.10, `sax`/`expatreader` v0.12, `xmlrpc` v0.13) and opt-in
> defense-in-depth (`Limits` caps v0.4, extended to minidom + sax in v0.14; the
> `security_report()` posture API v0.5, its map current through v0.11). FO's floor
> below remains the non-negotiable compatibility guarantee; purexml's
> own steward vision for a healthy 1.0 is in [`v1.0_TARGET.md`](v1.0_TARGET.md), and the
> execution plan is [`ROADMAP-to-1.0.md`](ROADMAP-to-1.0.md). This doc is the originating
> contract — the promise FO holds purexml to.

## 1. Purpose

Provide a **pure-Python, zero-runtime-dependency** capability to **safely parse untrusted
XML**, so that downstream consumers can drop the third-party `defusedxml` dependency **with
zero functionality loss** — same parses succeed, same attacks are blocked.

This is the cleanest kind of replacement: `defusedxml` is not an open-ended parser — it is
a **closed set of hardening behaviors** layered on the standard library's own XML parser.
The capability here is to deliver those same protections on the stdlib, directly.

The anchor consumer is **file-observer** (it parses OOXML `docProps/*.xml`, spreadsheet
XML, and arbitrary `.xml` files through a hardened parse).

## 1a. FO's explicit adoption requirements (relayed 2026-06-26) — the stable-swap contract

FO uses **exactly one symbol** — `from purexml.ElementTree import fromstring` — then walks the
result with `.iter(tag)` / `.text` / `.get(attr)` / namespace-qualified tags. Its inputs for keeping
the swap safe + trivial (folded in here as durable scoping; **all true today**):

1. **Name + module-path stability.** `purexml.ElementTree.fromstring` (import name AND path) must stay
   stable once FO pins — a later rename/restructure breaks FO's installs *and* its
   `ScanContext.dependencies` determinism fingerprint. **→ Any package/module rename must land
   BEFORE FO pins** (a G5 packaging / G6 freeze input — the name/package decision is still deferred;
   lock it before adoption, not after). Cross-ref the pre-freeze A1 (import path) item.
2. **Narrow symbol contract.** Keep `fromstring`'s signature + the returned object's shape stable.
   FO never touches minidom/sax/iterparse/parse — `fromstring` is the only surface that reaches it.
3. **Element-walk output-equivalence (the load-bearing one).** `fromstring` must keep returning a
   tree **byte-identical to stdlib `xml.etree.ElementTree`** on the shape FO reads — `.iter(tag)`
   order, `.text`, attributes, namespace-qualified tags — not only C14N-string-equal. A silent
   divergence would shift FO's manifest VALUES. **→ the oracle must keep covering element-WALK
   equivalence specifically** (added as a test guard, not only C14N).
4. **Mirror defaults.** `fromstring()` with no args must keep defusedxml's defaults
   (`forbid_entities=True`, `forbid_external=True`, `forbid_dtd=False`) — FO never sets the knobs.
5. **Plain-string `__version__`.** Top-level `purexml.__version__` must stay a stable plain `str`
   (FO reads it into `ScanContext` + a manifest checksum; a non-string/odd-repr broke determinism
   before). **→ guarded by a test.**
6. **Stays pure-stdlib, zero-IO, ≤3.10.** Zero runtime deps, the no-network/no-filesystem-on-parse
   guarantee (`test_no_io.py`), and Python floor ≤3.10 — the three reasons FO swaps at all.

These are the floor for the G1 adoption; #3 and #5 are now backed by dedicated test guards
(element-walk equivalence + `__version__`-is-str). #1 is an explicit input to the freeze/packaging
decision: **decide the published name before FO pins.**

**All six FO-relayed contract points are now a single executable CI gate**
([`tests/test_fo_contract.py`](../tests/test_fo_contract.py), added 2026-07 after FO's steward
re-affirmed the contract): one `test_fo_<n>_*` per point — bytes/str encoding parity, hostile-input
default-safety + opt-in `RECOMMENDED_LIMITS` typed caps (with a **bounded-*time*** never-hang
tripwire), the `purexml.common` exception mirror, determinism, the flat read surface + the pinned
`>=3.10` floor, and `__version__`-is-`str` — plus a guard on FO's exact `purexml.ElementTree.fromstring`
import path. Any change that breaks an FO guarantee now fails purexml's CI **as a named FO regression**,
so the contract cannot silently drift between now and when FO pins. FO's usage is a first-class fixture
keeping the surface honest to 1.0, not a promise to remember.

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
