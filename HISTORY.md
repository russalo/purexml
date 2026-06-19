# purexml Version History

This is the running index of all versions, their specifications, and their
compliance reports. Use this as the **entry point** when orienting on the
project — it's the one document where every release leaves a row.

**Current version:** see the project's version source-of-truth (e.g.
`pyproject.toml`, the `VERSION` constant, or `go.mod`) and the latest entry
below.

**How to read this index:**
- Active versions have specs and compliance reports in `docs/`.
- Archived versions have specs and compliance reports under `docs/archive/`
  (convention: at the first major bump, the previous major's RFCs and
  compliance reports move into `docs/archive/{previous_major}.x/`).
- Pre-1.0 versions use **looser formatting** — narrative entries, no
  compliance report requirement, RFCs optional. Once the project ships 1.0
  the row shape below becomes mandatory; the public contract binds at the
  same time.

---

## Versions

| Version | Schema | Date | Notable | Spec | Compliance |
|---|---|---|---|---|---|
| 0.10.0 | n/a | 2026-06-19 (PR #28) | **`purexml.minidom` drop-in + `purexml.common` shim** — first breadth beyond ElementTree, scoped by measured defusedxml usage (minidom = 457 sites, the #2 consumer surface). `parse`/`parseString` return a stdlib `xml.dom.minidom.Document` with defusedxml's `forbid_*` signature + defaults; hardening mirrors defusedxml (subclass stdlib `xml.dom.expatbuilder`, install blocking handlers raising purexml's exceptions). A caller-supplied `parser` → `NotSupportedError` (a foreign parser would bypass hardening — stricter than defusedxml). `purexml.common` aliases `DefusedXmlException = PureXMLError` so `except DefusedXmlException` survives `s/defusedxml/purexml/` across every module. New parse surface → **LOGIC extended** (minidom path); SCHEMA n/a (stdlib `Document`); zero runtime dep intact. Oracle-gated parity (9 ALLOW `toxml`-equal, 6 attacks block on both); no-fetch proven on the DOM external-DTD edge. Full four-leg (security-load-bearing); minidom+common 100% cov. | [v0.10.0_RFC_Specification.md](docs/v0.10.0_RFC_Specification.md) _(approved 2026-06-19)_ | [COMPLIANCE-v0.10.md](docs/COMPLIANCE-v0.10.md) |
| 0.9.0 | n/a | 2026-06-19 (PR #27) | **Map CVE-2026-41080 (hash-flooding)** — closes the class v0.6 deferred "until grounded". Grounded as insufficient SipHash salt entropy (CWE-331, expat 2.8.0, LOW) reachable via normal name-interning; added to `security_report().mitigations` as `hash_flooding_cve_2026_41080`. Because it's a **hardening** of an existing defense (not a present/absent hole), introduces a 5th status **`EXPAT_PARTIAL`** — **never `LIVE`**, and (refined per PR-bot review, CVE-2026-7210) reported **conservatively PARTIAL on every runtime**: full 16-byte-salt mitigation needs BOTH expat ≥2.8.0 AND CPython's `pyexpat` fix, which purexml can't verify at runtime, so it never claims `MITIGATED` on the expat version alone. Also **retires `_HIGHEST_UNMAPPED_FIX`** + the generic untracked-gap advisory (every *reachable* expat fix is now individually tracked; the two NULL-deref classes purexml doesn't reach stay unmapped). Report-only — no parse-behavior change; LOGIC unchanged (reported, not blocked), SCHEMA n/a. Status vocabulary PROVISIONAL. | [v0.9.0_RFC_Specification.md](docs/v0.9.0_RFC_Specification.md) _(approved 2026-06-19)_ | [COMPLIANCE-v0.9.md](docs/COMPLIANCE-v0.9.md) |
| 0.8.0 | n/a | 2026-06-18 (PR #21) | **Ship types** — annotate the public surface + a PEP 561 `py.typed` marker so a consumer's type-checker uses purexml's own types instead of `Any`. `mypy`-clean, gated by a CI typecheck job; honest `types: mypy` badge. The verbatim-mirror `_setevents` redefinitions + the structural-stdlib-drop-in friction are resolved with documented `# type: ignore`s (mirror preserved). No runtime/parse change — but `py.typed` is a new consumer-facing guarantee. SCHEMA n/a; LOGIC unchanged. | [v0.8.0_RFC_Specification.md](docs/v0.8.0_RFC_Specification.md) _(approved 2026-06-18)_ | [COMPLIANCE-v0.8.md](docs/COMPLIANCE-v0.8.md) |
| 0.8.1 | n/a | 2026-06-18 | **Patch** — tighten mypy to `--strict` (no behavior/API change): annotated all internal `_parser.py` methods, resolved the `Any` leaks (`cast` on the pluggable-target `close()`), and kept the verbatim `_setevents` mirror byte-for-byte via documented `# type: ignore[misc, no-untyped-def]`. The dynamically-used expat handle + pluggable target are typed `Any` (honest). CI `mypy` job now runs strict. Rigor within the approved v0.8 typed design. SCHEMA n/a; LOGIC unchanged. _(HISTORY only, no RFC — part of v0.8.)_ | _(no RFC — patch)_ | _(part of v0.8)_ |
| 0.7.0 | n/a | 2026-06-17 (PR #15) | **Posture CLI** — `python -m purexml` over `security_report()`: default human report (informs, exit 0), `--json` (machine-readable, PROVISIONAL, for provenance), `--check [--min-expat X.Y.Z]` (opt-in CI gate, exit code; pin-your-floor), `--version`; plus `SecurityReport.as_dict()`. First build of the publish-worthy-debut push (the 10-second demo a cold evaluator runs). `__main__.py` is the one I/O boundary (no-I/O guard carve-out: CLI-output stdlib only, still under FORBIDDEN). Report-only — no parse-behavior change; LOGIC unchanged, SCHEMA n/a. | [v0.7.0_RFC_Specification.md](docs/v0.7.0_RFC_Specification.md) _(approved 2026-06-17)_ | [COMPLIANCE-v0.7.md](docs/COMPLIANCE-v0.7.md) |
| 0.6.0 | n/a | 2026-06-17 (PR #11) | **Complete the posture map** — adds the two newer expat-layer DoS classes (reachable via normal parse paths) as first-class `security_report().mitigations` entries with per-class fix-version gating: `content_token_overflow_cve_2026_25210` (expat 2.7.4) and `attribute_collision_dos_cve_2026_45186` (expat 2.8.1; opt-in `max_attributes` partially bounds it). Report-only — **no parse-behavior change**; LOGIC unchanged (reported, not blocked), SCHEMA n/a. CVE-2026-41080 left unmapped (ungrounded) under the generic floor advisory. | [v0.6.0_RFC_Specification.md](docs/v0.6.0_RFC_Specification.md) _(approved 2026-06-17)_ | [COMPLIANCE-v0.6.md](docs/COMPLIANCE-v0.6.md) |
| 0.5.1 | n/a | 2026-06-17 | **Patch** — adversarial soak + expat-floor currency (no parse-behavior change): a 17-vector red-team soak module (`test_hardening_soak.py` — distinct DoS classes, the unparsed-entity/NDATA path, sub-cap nested bomb, and **encoding-vector** attacks proving the block is encoding-independent), backed by a 60k-comparison heavy differential soak (0 divergences). **Refreshed `RECOMMENDED_EXPAT_VERSION` 2.7.2 → 2.8.1** after the 2026 libexpat 2.7.4–2.8.1 DoS release train (CVE-2026-25210/41080/45186 reach normal parse paths; 24515/32776 don't), and **decoupled** `disproportionate_memory` onto its own 2.7.2 fix version so the moving floor can't mis-gate it. `security_report()`/`assert_expat_secure()` now recommend latest-stable (fail-safe; opt-in surface, PROVISIONAL). Adding the two newly-reachable DoS classes to the mitigation map is **deferred** (a mitigation-set change). LOGIC unchanged (no parse-or-block change), SCHEMA n/a. _(HISTORY only, no RFC — part of v0.5.)_ | _(no RFC — patch)_ | _(part of v0.5)_ |
| 0.5.0 | n/a | 2026-06-17 | **Trust surface** — a read-only `security_report()` posture API (libexpat version + per-class mitigation map + recommended limits, genuinely immutable) and the audit story as shipped evidence (richer differential fuzz — 960 docs — + optional Atheris `[fuzz]` extra + a committed `docs/EQUIVALENCE.md`). First minor under the maintained-successor mandate; no parse-behavior change. PR #8; four-leg review complete (5 PR-bot findings all real + fixed). SCHEMA n/a; LOGIC unchanged. | [v0.5.0_RFC_Specification.md](docs/v0.5.0_RFC_Specification.md) | [COMPLIANCE-v0.5.md](docs/COMPLIANCE-v0.5.md) |
| 0.4.0 | n/a | 2026-06-16 | **Mirror-plus** — opt-in structural-DoS caps (`max_depth`/`max_attributes`/`max_bytes`, default OFF so the strict-mirror default is preserved) raising `LimitExceeded`. First deliberate divergence beyond defusedxml (opt-in only). Merged via PR #7; four-leg review complete (all 4 PR-bot findings real + fixed). SCHEMA n/a; LOGIC extended (structural caps). | [v0.4.0_RFC_Specification.md](docs/v0.4.0_RFC_Specification.md) | [COMPLIANCE-v0.4.md](docs/COMPLIANCE-v0.4.md) |
| 0.3.1 | n/a | 2026-06-16 | **Patch** — Tier-1 hardening (within-mirror, no behavior change): structural **no-I/O import guard** (src imports only stdlib `xml`; no network/exec/os modules — the no-fetch guarantee made structural, not just behavioral) + **broadened differential fuzz** (char-ref floods, conditional sections, XML 1.1, declared encodings, adjacent CDATA). LOGIC unchanged, SCHEMA n/a. _(HISTORY only, no RFC — part of v0.3.)_ | _(no RFC — patch)_ | _(part of v0.3)_ |
| 0.3.0 | n/a | 2026-06-16 | Hardened `iterparse` — **completes the `defusedxml.ElementTree` family** (the streaming slice). Reuses stdlib `iterparse` via `_setevents` on `purexml.XMLParser` (Option A). Merged via PR #5; four-leg review complete (all 3 PR-bot findings grounded-declined). SCHEMA n/a; LOGIC unchanged (default behavior; adds the streaming entry point). | [v0.3.0_RFC_Specification.md](docs/v0.3.0_RFC_Specification.md) | [COMPLIANCE-v0.3.md](docs/COMPLIANCE-v0.3.md) |
| 0.2.0 | n/a | 2026-06-16 | Complete the non-streaming `defusedxml.ElementTree` surface: `parse`, `fromstringlist`, `XML`/`tostring`, exposed `XMLParser`, the `forbid_*` knobs (+ new `DTDForbidden`), under a canonical `purexml.ElementTree` namespace. Merged via PR #4; four-leg review complete. SCHEMA n/a; LOGIC mitigation set extended (`forbid_dtd` path), default behavior unchanged. | [v0.2.0_RFC_Specification.md](docs/v0.2.0_RFC_Specification.md) | [COMPLIANCE-v0.2.md](docs/COMPLIANCE-v0.2.md) |
| 0.1.2 | n/a | 2026-06-16 | **Patch** — durability hardening: differential fuzz gate vs the defusedxml oracle (seeded, C14N-equal-or-both-raise), the 2 newer expat-layer attack classes (CVE-2023-52425 large-tokens + disproportionate-memory, version-gated), and an opt-in libexpat version-awareness API (`EXPAT_VERSION` / `expat_is_secure` / `assert_expat_secure`). No parse-behavior change; LOGIC unchanged (v0.1), SCHEMA n/a. _(HISTORY only, no RFC — part of v0.1.)_ | _(no RFC — patch)_ | _(part of v0.1)_ |
| 0.1.1 | n/a | 2026-06-16 | **Patch** — lower runtime floor to Python **3.10** (was 3.12) so purexml never binds a consumer's Python floor (target spec §4); add a CI matrix (3.10–3.13) to test the declared floor rather than only 3.12. No logic/behavior change; SCHEMA n/a, LOGIC unchanged (v0.1). _(HISTORY only, no RFC — part of v0.1.)_ | _(no RFC — patch)_ | _(part of v0.1; see [COMPLIANCE-v0.1.md](docs/COMPLIANCE-v0.1.md))_ |
| 0.1.0 | n/a | 2026-06-16 | First slice: hardened `fromstring` — C1 safe-parse + C2 safe-failure, behaviorally equivalent to `defusedxml` defaults, stdlib-only. SCHEMA n/a (returns stdlib `Element`); LOGIC introduced (hardening mitigation set v0.1). Merged via PR #1; four-leg review complete. | [v0.1.0_RFC_Specification.md](docs/v0.1.0_RFC_Specification.md) | [COMPLIANCE-v0.1.md](docs/COMPLIANCE-v0.1.md) |
| 1.0.0 | 1.0 | YYYY-MM-DD | **Schema freeze.** Public contract binding. Backward compatibility policy in effect. No new features — governance declaration on a validated codebase. | [v1.0.0_RFC_Specification.md](docs/v1.0.0_RFC_Specification.md) | [COMPLIANCE-v1.0.md](docs/COMPLIANCE-v1.0.md) |
| 1.0.1 | 1.0 | YYYY-MM-DD | **Patch release** — example shape. Bug fix in {component}. SCHEMA unchanged. _(part of v1.0; HISTORY only, no RFC.)_ | _(no RFC — patch)_ | _(part of v1.0)_ |

---

## Drafts in Flight

List any RFCs currently in draft (`docs/v{X.Y.Z}_RFC_DRAFT.md`). When none are
open, state so explicitly rather than deleting the section — the empty-but-named
state is the signal:

> No drafts in flight. **v0.10.0 shipped** 2026-06-19 (PR #28) — current; first breadth
> beyond ElementTree (`purexml.minidom` + `purexml.common`). **Scope reframed 2026-06-19
> (Russell):** an ElementTree-only surface is the slice *one* adopter (file-observer) needs —
> not a publishable 1.0. The earned 1.0 = **the maintained, zero-dep successor that replaces
> defusedxml across the surface the ecosystem actually imports**, grounded by a usage
> measurement (`scratch/research/2026-06-19_defusedxml-usage-measurement.md`): ElementTree ✅,
> **minidom ✅ (v0.10)**, **sax next** (375 sites), xmlrpc TBD (distinct monkeypatch shape),
> pulldom/expatreader deferred (measured-negligible), **lxml excluded** (third-party dep →
> breaks zero-dep). Then a 1.0 freeze over a surface that genuinely replaces defusedxml. Other
> gates: G1 file-observer adoption + bestiary soak (✅ green, standing); G5 packaging/license/
> name (Russell's call); G6 freeze. **Next: the `sax` breadth minor.**
>
> (Shipped: v0.1.0 fromstring (PR #1); v0.1.1 floor→3.10 (PR #2); v0.1.2 durability +
> expat awareness (PR #3); v0.2.0 non-streaming ElementTree surface + forbid_* knobs
> (PR #4); v0.3.0 iterparse — family complete (PR #5); v0.4.0 opt-in structural-DoS
> caps (PR #7); v0.5.0 trust surface (PR #8); v0.5.1 soak + expat-floor currency (PR #10);
> v0.6.0 posture-map completion (PR #11); v0.7.0 posture CLI (PR #15); v0.8.0 typed +
> py.typed (PR #21); v0.8.1 mypy --strict (PR #22); v0.9.0 map CVE-2026-41080 (PR #27);
> v0.10.0 minidom + common (PR #28).
> Plus tooling/quality: lint+coverage gates (PR #19); typed surface in flight (v0.8).)

---

## Historical Drafts and Design Documents

These are working documents from earlier in the project. Kept for design
history; not specifications themselves. Pre-RFC scratch material (early
design notes, alternate drafts) lives here once promoted out of `scratch/`.

| File | Era | Purpose |
|---|---|---|
| TODO | Pre-vX.Y | TODO: short description of what this is |

---

## Compliance Report Gaps

TODO: Note any versions that did **not** get a compliance report and why
(usually patch releases — they're covered by HISTORY narrative + the
parent minor's compliance report). Default rule:

> Patches inherit their parent minor's compliance report; their narrative
> lives in this index, not in a separate report.
