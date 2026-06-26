# Roadmap to purexml 1.0

> **Status: ratified 2026-06-16** (by Russell). Grounded by `/deep-research` run
> wf_5ea8ed7c-044 (findings: `scratch/research/2026-06-16_1.0-scope-research.md`,
> 25/25 claims confirmed vs primary sources). This is the living plan from the
> shipped v0.10.0 to the 1.0 contract freeze.

## What 1.0 means
Per the russalo version philosophy, **1.0 = a governance declaration on a
*validated* codebase**: public contract frozen, backward-compat policy on, no new
features at the freeze. Road to 1.0 = scope → build it → validate (incl. real
adoption) → freeze.

## 1.0 identity & scope — REFRAMED 2026-06-19 (ratified)
**purexml 1.0 = the maintained, zero-dependency safe replacement for `defusedxml` across the
surface the ecosystem actually imports** — not just the `ElementTree` slice one adopter needs.
Beyond defusedxml, one that *tracks current CPython/libexpat mitigations* (defusedxml froze in
2021 and is effectively abandoned; OWASP/Python still point users to it — that gap is purexml's
reason to exist beyond file-observer).

> **Reframe (2026-06-19, Russell):** the prior scope ("complete drop-in for
> `defusedxml.ElementTree`") was the slice file-observer needs — a one-adopter ceiling, not a
> publishable 1.0. *"You'll never get more if you stop there. Earn a reason to go 1.0."* The
> earned reason = breadth (cover what the ecosystem imports → a stranger *can* adopt) + depth
> (the maintained tracking → *why* purexml beats staying on abandoned defusedxml). Scope is now
> **measured, not guessed** (`scratch/research/2026-06-19_defusedxml-usage-measurement.md`).

- **In scope — ElementTree family (done, v0.1–v0.3):** `fromstring`, `parse`, `iterparse`,
  `fromstringlist`, `XMLParser`, `XML`/`tostring`, `ParseError`.
- **In scope — breadth (promoted from "deferred" 2026-06-19, by measured demand):**
  **`minidom` ✅ (v0.10, 457 sites)** + `purexml.common` compat shim; **`sax` — next (375 sites)**.
- **TBD as its own slice:** `xmlrpc` (343 sites, but a distinct *monkeypatch-the-stdlib* shape,
  not a parser wrapper) — decide after sax.
- **Deferred (measured-negligible):** `pulldom` (48), `expatreader` (14); `expatbuilder` is the
  internal minidom engine, not exposed.
- **Excluded (zero-dep identity, not demand):** `lxml` (390 sites) — wraps third-party `lxml`,
  breaks stdlib-only/zero-dep; deprecated upstream. A principled exclusion.

## Posture: behavioral mirror + bounded defense-in-depth
Stay a behavioral mirror of defusedxml's **defaults** (`forbid_dtd=False,
forbid_entities=True, forbid_external=True`), and accept defusedxml's
**parameterized signature** (the `forbid_*` knobs — re-opened 2026-06-16, in v0.2).
On top, add bounded opt-in defense-in-depth defusedxml never had (all **shipped**,
default-off):
- **Runtime libexpat-version assertion** (`pyexpat.EXPAT_VERSION`) — protection is
  entirely libexpat-version-dependent (the recommended-latest floor is **2.8.2** as
  of 2026-06, after the 2.7.4–2.8.2 DoS / memory-safety release train; older expat is
  still vulnerable to several classes); unique to purexml. (v0.1.2; surfaced for adopters by
  `security_report()` in v0.5; floor refreshed to 2.8.1 in v0.5.1, to 2.8.2 in v0.10.1.)
- **Reparse-deferral awareness** (CVE-2023-52425 "large tokens"; Expat 2.6.0;
  CPython 3.13 `Get/SetReparseDeferralEnabled`, reachable via our expat parser).
- **Amplification-limit awareness** (libexpat 2.4.0 billion-laughs cap).
- **Optional `forbid_dtd=True` strict mode** (OWASP's strongest: one control for
  XXE *and* billion-laughs). (v0.2.)
- **Opt-in structural-DoS caps** (`Limits` — `max_depth`/`max_attributes`/`max_bytes`;
  v0.4) — bound the pathological-but-legal inputs neither defusedxml nor the expat cap cover.
- **Trust surface** (`security_report()`; v0.5, posture map completed v0.6, **all reachable
  classes mapped v0.9**) — a read-only report mapping each attack class to where it's handled
  on the runtime, with per-class libexpat fix-version gating (incl. the 2026 DoS classes). The
  maintained-successor promise made legible: the living library tells you your posture, and
  **demonstrably tracks the moving target** (v0.5.1 + v0.6 folded the 2026 libexpat 2.7.4–2.8.1
  train in within days; v0.9 grounded + mapped the last reachable class, CVE-2026-41080, with a
  non-overstating `EXPAT_PARTIAL` status); the frozen incumbent couldn't.

> **Reframe (2026-06-17) — the gate is the ecosystem debut, not one consumer.**
> Stress-tested by removing file-observer entirely: purexml's reason to exist
> *survives the loss of any single consumer* — it is the maintained, zero-dep
> successor to the OWASP-recommended-but-abandoned `defusedxml` (0.7.1 / 2021;
> 0.8.0 stalled at rc2), one that tracks the moving libexpat threat the incumbent
> no longer does. So the **1.0 gate is now: a publish-worthy debut + first real
> adoption** — measured by *an evaluator who wasn't recruited choosing it*, not by
> any one captive consumer. **file-observer is the anchor consumer + first
> validation track (G1/G2, alive), not the definition of done** — and FO-in-production
> is itself a credibility signal *for* the debut, so the two compose. Publishing
> stays deferred for **strategic timing + first-impression quality** (Russell's call),
> not for lack of readiness. Build target: what a cold security engineer needs in the
> first 60 seconds on publish day.

## Gates to 1.0
- **G1 — file-observer adopts purexml** (import swap) — the **first** real-adoption
  proof, not the only one. 🟡 **in progress (scanner-side, 2026-06-17).** FO has
  **verified v0.5 consumer-side** (literal `purexml.ElementTree.fromstring` swap, default
  mirrors defusedxml) and confirmed it would take purexml as a **dependency**;
  `security_report()` accepted as the trust surface (to be recorded in `ScanContext`
  dep-provenance at adoption). FO uses only `fromstring`, so it's fully covered by the
  current surface — it does not constrain the public scope.
- **G2 — ecosystem readiness (the publish-worthy debut)** — the broadened gate: the
  first-impression layer a stranger evaluates (public README/story, the trust signals,
  a one-line posture demo) + first *external* adoption signal (a non-russalo dependent,
  a stranger's issue, download/awareness). FO's two scanner-side validation items
  (adversarial soak + 2nd consumer) feed this but don't bound it. *Equivalence already
  proven; the gap is presentation + reach, not capability.*
  - **Adversarial soak — ✅ GREEN, confirmed vs current 0.8.1 (bestiary M2 + re-soak,
    2026-06-19).** bestiary Claude's XML attack battery (FO's defusedxml→purexml adoption
    gate, M2): all 7 specimens clear — billion-laughs / param-entity-bomb /
    quadratic-blowup BOUNDED (rejected cleanly, no OOM/hang); xxe / external-param-entity /
    external-dtd / xinclude-system NO-ESCAPE (`escaped=False`). First run vs 0.7.0,
    **re-soak vs 0.8.1 GREEN** (identical), **independently grounded here** (own repro
    matches exactly). **bestiary is now purexml's STANDING per-release adversarial battery**
    — re-run each cycle; any non-survival is a real new finding.
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
  *policy*, not a hardcoded number (safe floor moves: 2.4.0 → 2.6.0 → 2.7.2 → 2.8.1 …
  — already bumped once in v0.5.1, which is exactly why the *number* must not freeze).

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
**~90% — the build axis is DONE (v0.3 completed the ElementTree family) and the
opt-in defense-in-depth has shipped (v0.4 `Limits`, v0.5 `security_report()`).**
Built & proven: the full hardened ElementTree surface, C14N + event-stream
oracle-gating, falsify-first battery + (960-doc) differential fuzz + committed
equivalence report, corpus sweep, durability + version awareness + the posture API,
four-leg apparatus. **No build work remains.** What's left for 1.0:
- **G1/G2** — file-observer adoption validation (the "validated codebase" gate).
- **G5** — the deferred adoption-model / license / packaging decisions.
- **G6** — the freeze ceremony (lock the contract surface, fill `PUBLIC_CONTRACT.md`,
  backward-compat policy). The pre-freeze checklist above is the gate.

## Open questions (revisit, don't block)
1. Real-world per-module usage distribution (validates deferring minidom/sax).
2. Maintainer intent / is defusedxml 0.8.0 ever shipping (successor positioning).
3. Precise safe libexpat floor + hard-fail vs warn (the version-assertion policy).
