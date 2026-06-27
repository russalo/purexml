# COMPLIANCE — purexml v0.14.0

Audit of v0.14.0 against the approved spec
[`v0.14.0_RFC_Specification.md`](v0.14.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#37](https://github.com/russalo/purexml/pull/37), branch `v0.14.0-limits-breadth`.
Suite: **317 passed, 1 gated-skip.**

## Theme
Extend the v0.4 opt-in `Limits` structural-DoS caps (`max_depth`/`max_attributes`/`max_bytes`)
to the breadth surfaces — `purexml.minidom` + `purexml.sax` — via a keyword-only `*, limits=None`.
Opt-in, default-off (mirror-plus): with `limits=None` these surfaces stay byte-identical to
defusedxml. A shared `_LimitCounter` in `limits.py` keeps accounting identical to the ElementTree
path. Closes the last of three post-breadth gaps (A=fuzz-all-surfaces v0.13.1; B=multi-surface
re-soak #36; **C=Limits breadth**).

## §2/§3 scope + mechanism (grounded)

| Req | Implementation | Status |
|---|---|---|
| Shared accounting reused across surfaces (`_LimitCounter` enter/leave/reset, `_counter_for`, `_check_max_bytes`) | `limits.py` | ✅ |
| `minidom.parse`/`parseString` + `_builder` gain keyword-only `limits=` | `minidom.py` | ✅ |
| minidom: override element handlers on `_DefusedExpatBuilderNS` (Namespaces owns them in MRO); `_counter` set BEFORE `super().__init__` (ExpatBuilder.__init__ calls reset()); attrs = ordered list → `len//2` | `minidom.py` | ✅ |
| `sax.make_parser`/`parse`/`parseString` + `expatreader.DefusedExpatParser`/`create_parser` gain `limits=` | `sax.py`, `expatreader.py` | ✅ |
| sax: override `start_element`/`end_element` + NS-on `start_element_ns(name, attrs)`/`end_element_ns(name)` (grounded signatures); attrs = dict → `len` | `expatreader.py` | ✅ |
| `max_bytes` enforced on `parseString` only (stream length unknown without `os`); depth/attrs on `parse(file/stream)` too | both | ✅ |
| Same exceptions as ElementTree (`DepthExceeded`/`AttributesExceeded`/`SizeExceeded`); `RECOMMENDED_LIMITS` preset | `errors.py`/`limits.py` | ✅ |
| xmlrpc deferred (no `limits=` call site; gzip-bomb `MAX_DATA` is its cap) | pinned by `test_xmlrpc_has_no_limits_param` | ✅ |

## §6 acceptance bar (binding)

| # | Req | Evidence | Status |
|---|---|---|---|
| 1 | `limits=None` → minidom/sax byte-identical (mirror untouched); differential fuzz 0-divergence | `test_default_limits_none_is_byte_identical`; fuzz gate (all 4 surfaces); sweep **372/0** | ✅ |
| 2 | depth/attrs/bytes raise the SAME exceptions on minidom AND sax | `test_minidom_max_*`, `test_sax_max_*` | ✅ |
| 3 | no false positives below the cap; NS-on + NS-off sax paths both counted | `test_*_under_limit_ok`, `test_sax_namespace_aware_path_counts`, boundary test | ✅ |
| 4 | no-I/O guard holds; mypy `--strict` + ruff clean; coverage ≥90% on new paths | CI; limits/minidom/sax/expatreader **100%** | ✅ |
| 5 | docs freshness sweep; HISTORY row; full four-leg; this compliance; bestiary re-soak relay | done (see below) | ✅ |

## Four-leg review — ALL FOUR RUN (feature minor, security-load-bearing)

| Leg | Result |
|---|---|
| 1 — in-house (inline grounded probes + battery) | ✅ no findings. Default path proven untouched (fuzz + sweep + focused identity test); caps fire + balance (boundary test pins the off-by-one and exercises `leave()`); grounded MRO / attr-shape / NS signatures / init ordering. |
| 2 — Gemini cross-model (`gem.sh`) | ⚠️ UNAVAILABLE (daily free-tier quota, 429). Covered by leg-1 probes + leg-4. |
| 3 — empirical sweep | ✅ ElementTree mirror **372/0** — default path untouched. |
| 4 — PR bots (Codex + Gemini Code Assist) | ✅ 1 finding (Gemini), grounded + applied — see below. |

### Findings dispositions
- **expatreader init ordering** (Gemini Code Assist, medium): flagged `_counter`/`forbid_*`
  set AFTER `super().__init__()`, "risky if the base ctor calls `self.reset()`". **Grounded:**
  stdlib `xml.sax.expatreader.ExpatParser.__init__` does **not** call `reset()` (confirmed from
  source; `reset()` runs at parse time) — so it is **not a live bug** (317 tests at 100% cov
  already passed). **Applied anyway** as zero-risk latent-robustness + parity with minidom (where
  `ExpatBuilder.__init__` *does* call reset(), making the pre-super ordering mandatory). Gates
  re-run green; expatreader still 100% cov. Recorded in `scratch/review/v0.14.0_findings.md`.

## §5 axes
RELEASE 0.13.1 → **0.14.0**. SCHEMA **n/a** (no wire shape — stdlib `Document` / SAX events / `Element`).
LOGIC **extended** — the structural-cap mitigation now applies on minidom + sax (new opt-in
block paths on new surfaces); the default mirror is unchanged.

## Bestiary re-soak
Per §6.5, a structural specimen (deep-nesting / attribute-flood) run knob-ON against
`purexml.minidom` + `purexml.sax` is now meaningful (these surfaces enforce `Limits` as of v0.14).
A re-soak relay covering the new knob-ON surfaces is drafted for Russell to relay
(`scratch/draft_to_bestiary_2026-06-27.md`); the standing default-OFF multi-surface soak stays
GREEN vs v0.13.1.

## Verdict
**Compliant.** Opt-in `Limits` extended to minidom + sax per the approved RFC; default path
provably byte-identical (fuzz + sweep 372/0 + focused identity test); caps fire with the same
exceptions as the ElementTree path; xmlrpc deferred as specified; four-leg run with the one
PR-bot finding grounded + applied. CI green 3.10–3.13. Ready to merge.
