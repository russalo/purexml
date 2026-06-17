# Roadmap to purexml 1.0

> **Status: ratified 2026-06-16** (by Russell). Grounded by `/deep-research` run
> wf_5ea8ed7c-044 (findings: `scratch/research/2026-06-16_1.0-scope-research.md`,
> 25/25 claims confirmed vs primary sources). This is the living plan from the
> shipped v0.1.1 to the 1.0 contract freeze.

## What 1.0 means
Per the russalo version philosophy, **1.0 = a governance declaration on a
*validated* codebase**: public contract frozen, backward-compat policy on, no new
features at the freeze. Road to 1.0 = scope → build it → validate (incl. real
adoption) → freeze.

## 1.0 identity & scope (ratified)
**purexml 1.0 = the complete, maintained, zero-dependency safe replacement for
`defusedxml.ElementTree`** — and, beyond defusedxml, one that *tracks current
CPython/libexpat mitigations* (defusedxml froze in 2021 and is effectively
abandoned; OWASP/Python still point users to it — that gap is purexml's reason to
exist beyond file-observer).

- **In scope (the ElementTree family):** `fromstring` (done), `parse`,
  `iterparse`, `fromstringlist`, the hardened `XMLParser` class, `XML`/`tostring`
  aliases, `ParseError`.
- **Out of 1.0 (deferred, not excluded):** `minidom`, `sax`, `pulldom`,
  `expatreader`/`expatbuilder`, `xmlrpc`, deprecated `lxml`. Add post-1.0 only if
  demand appears. *(Caveat: real-world per-module usage was not measured — this is
  a reasoned line; deferring rather than excluding keeps it safe.)*

## Posture: behavioral mirror + bounded defense-in-depth
Stay a behavioral mirror of defusedxml's **defaults** (`forbid_dtd=False,
forbid_entities=True, forbid_external=True`), and accept defusedxml's
**parameterized signature** (the `forbid_*` knobs — re-opened 2026-06-16, in v0.2).
On top, add bounded opt-in defense-in-depth defusedxml never had:
- **Runtime libexpat-version assertion** (`pyexpat.EXPAT_VERSION`) — protection is
  entirely libexpat-version-dependent (Expat <2.7.2 still vulnerable to several
  classes); unique to purexml.
- **Reparse-deferral awareness** (CVE-2023-52425 "large tokens"; Expat 2.6.0;
  CPython 3.13 `Get/SetReparseDeferralEnabled`, reachable via our expat parser).
- **Amplification-limit awareness** (libexpat 2.4.0 billion-laughs cap).
- **Optional `forbid_dtd=True` strict mode** (OWASP's strongest: one control for
  XXE *and* billion-laughs).

## Gates to 1.0
- **G1 — file-observer trial-adopts purexml** (import swap). The validation 1.0
  requires. *Critical path, scanner-side.* ⬜ — now appropriate (the ElementTree
  family is complete; adoption would be the full surface, not a partial swap).
- **G2 — adoption surfaces real scope** (likely small; equivalence already proven). ⬜
- **G3 — build the ElementTree family — ✅ COMPLETE (2026-06-16).**
  - **v0.2** ✅ (PR #4) — `parse` + `fromstringlist` + `XML`/`tostring` + `XMLParser`
    + the `forbid_*` knobs.
  - **v0.3** ✅ (PR #5) — `iterparse` (Option A: `_setevents` + reuse stdlib
    iterparse). Event-stream equivalence proven on real data; all PR-bot findings
    grounded-declined. **The build axis to 1.0 is done.**
- **G4 — durability hardening — ✅ COMPLETE (v0.1.2, PR #3):** differential
  fuzzing vs defusedxml across the Python/expat matrix + committed curated corpus
  of **7 classes** (5 baseline: billion-laughs, quadratic blowup, external-entity
  remote, external-entity local, DTD retrieval; + 2 newer: CVE-2023-52425
  large-tokens/reparse, disproportionate dynamic memory on old expat),
  **version-gated on `pyexpat.EXPAT_VERSION`.** Also ships the version assertion.
- **G5 — decide deferred items.** Adoption-model **direction is decided: publish
  first-party** (ratified 2026-06-16; `docs/v1.0_TARGET.md`). Remaining specifics to
  land by 1.0: PyPI timing, claiming the name, the license, the optional vendorable
  single-file form.
- **G6 — 1.0 freeze:** see the pre-freeze checklist below.

## Pre-freeze checklist (the 1.0 freeze gate — expands G6)

**1.0 is a one-way door:** once the contract binds, anything in the frozen surface
costs a 2.0 to change. This is *everything expensive-or-impossible to reverse after
the freeze*, ordered by cost-of-getting-it-wrong.

**A. Lock the contract surface (truly irreversible):**
- [ ] **Import path / module layout** — `purexml.fromstring` (flat) vs
  **`purexml.ElementTree.fromstring`** (mirrors defusedxml → swap is a pure
  `s/defusedxml/purexml/`). The import path *is* contract. *Lean: mirror.*
- [ ] **Final signatures byte-matching defusedxml** — incl. the `forbid_*` params
  (names, order, defaults). A wrong default/param name is permanent.
- [ ] **Complete + final exception hierarchy** — `PureXMLError(ValueError)` ←
  `EntitiesForbidden`/`ExternalReferenceForbidden`, **+ `DTDForbidden` once
  `forbid_dtd=True` mode lands** (reachable). Set must be complete before freeze.
- [ ] **Version-assertion policy** — hard-fail vs warn on Expat < floor; freeze the
  *policy*, not a hardcoded number (safe floor moves: 2.4.0 → 2.6.0 → 2.7.2 …).

**B. Build AND verify the whole frozen surface:**
- [x] v0.2 oracle-gated complete (PR #4) · [x] v0.3 (`iterparse`) oracle-gated
  complete (PR #5). **The frozen surface is built + verified.**

**C. Validate by real adoption ("validated codebase"):**
- [ ] file-observer has adopted + run purexml in production before the freeze.

**D. Durability guarantee in place:**
- [ ] differential-fuzzing gate · [ ] version-gated 7-class corpus · [ ] version
  assertion shipped.

**E. Deferred decisions that touch the frozen surface:**
- [ ] adoption model → frozen import name/package shape · [ ] license · [ ] PyPI name.

**F. Binding docs:**
- [ ] `PUBLIC_CONTRACT.md` filled + binding · [ ] backward-compat + deprecation
  policy on · [ ] `SECURITY.md` supported-versions.

**Freeze strategy (CONVENTIONS §3.1 stability ladder):**
- **STABLE at 1.0:** the defusedxml-mirror surface (ElementTree family + exceptions
  + defaults) — its reference (defusedxml) is itself frozen, safe to lock hard.
- **PROVISIONAL at 1.0:** the novel defense-in-depth (exact version-assertion
  behavior, reparse-deferral knob surface) — depends on the moving libexpat
  landscape; "may change in a MINOR" lets it settle without a 2.0.

**Non-obvious traps:** A1 (import path) and A3 (exception-set completeness) silently
become 2.0-class mistakes if frozen without an explicit decision.

## Distance estimate
**~85% — the build axis is DONE (v0.3 complete the ElementTree family).** Built &
proven: the full hardened ElementTree surface, C14N + event-stream oracle-gating,
falsify-first battery + differential fuzz, corpus sweep, durability + version
awareness, four-leg apparatus. **No build work remains.** What's left for 1.0:
- **G1/G2** — file-observer adoption validation (the "validated codebase" gate).
- **G5** — the deferred adoption-model / license / packaging decisions.
- **G6** — the freeze ceremony (lock the contract surface, fill `PUBLIC_CONTRACT.md`,
  backward-compat policy). The pre-freeze checklist above is the gate.

## Open questions (revisit, don't block)
1. Real-world per-module usage distribution (validates deferring minidom/sax).
2. Maintainer intent / is defusedxml 0.8.0 ever shipping (successor positioning).
3. Precise safe libexpat floor + hard-fail vs warn (the version-assertion policy).
