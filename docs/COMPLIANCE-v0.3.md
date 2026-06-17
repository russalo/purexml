# COMPLIANCE — purexml v0.3.0

Audit of v0.3.0 against the approved spec
[`v0.3.0_RFC_Specification.md`](v0.3.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#5](https://github.com/russalo/purexml/pull/5), branch `v0.3.0`. Suite: **101 passed,
1 gated-skip.**

## §2–§3 Capability + design

| Req | Implementation | Status |
|---|---|---|
| `iterparse(source, events=None, parser=None, forbid_*)` under `purexml.ElementTree` | `_parser.iterparse` → `_stdlib_iterparse` driving the hardened `XMLParser` | ✅ |
| Design = Option A (`_setevents` + reuse stdlib iterparse) | `XMLParser._setevents` mirrors stdlib verbatim; Option B marked spinoff (`scratch/spinoff_ideas.md`) | ✅ |
| Namespace mirror now complete (iterparse present) | `ElementTree.py` (`__all__` + import); v0.2 honesty note resolved | ✅ |

## §4–§5 Streaming-security bar + acceptance

| Req | Evidence | Status |
|---|---|---|
| Event-stream equivalence vs `defusedxml.iterparse` (all event modes) | `test_v03_iterparse` + sweep: **0 disagreements over 612 real event-streams** (204 docs × 3 modes) | ✅ |
| Same raise-point under streaming | `test_iterparse_raise_parity` / `test_iterparse_blocks_are_purexml_errors` | ✅ |
| No-fetch/no-read **under streaming** (trip-wire while consuming) | `test_no_io_under_streaming` + leg-1 chunked-feed probe (token split across 3-char feeds → blocked, no I/O) | ✅ |
| `forbid_*` knob matrix for iterparse (all 8) | `test_iterparse_knob_matrix` | ✅ |
| Reparse-deferral / large-token equivalence (version-gated) | leg-1 probe: 2 MB-token iterparse equivalent to oracle (expat 2.6.1) | ✅ |
| Cleanup-on-error through the iterator | `test_iterparse_releases_heavy_state_on_error` (parser/target nulled) | ✅ |
| No regression in fromstring/parse | sweep unchanged: 372/0 | ✅ |

## §6–§8

| Req | Status |
|---|---|
| §6 measure-first — `_setevents` contract read + mirrored (verbatim, 3.12) | ✅ |
| §7 out of scope — minidom/sax/pulldom/etc. → post-1.0 | ✅ |
| §8 DoD — iterparse done; namespace complete; ROADMAP G3 complete | ✅ |

## Four-leg review — ALL FOUR RUN

| Leg | Result |
|---|---|
| 1 — in-house (inline grounded probes) | ✅ clean (chunked-feed XXE blocked no-I/O; large-token; cleanup-on-error) |
| 2 — Gemini cross-model (read-only inline) | ✅ one LOW note (`_setevents` private API) — accepted Option-A tradeoff |
| 3 — empirical sweep | ✅ iterparse 612 streams / 0 disagreements; fromstring+parse 372/0 |
| 4 — PR bots (Gemini Code Assist + Codex) | ✅ 3 findings, **all grounded + declined** (see below) |

### Findings dispositions (PR#5) — grounded-and-declined
- **Gemini, start-ns/end-ns payload (high)** — false positive. `_setevents` is a
  verbatim stdlib mirror; with a `start_ns` target, purexml ≡ defusedxml (both yield
  the target's return). The suggested fix would diverge.
- **Gemini, guard comment/pi in `_setevents` (high)** — false positive. Stdlib doesn't
  guard there; comment-events with a no-`.comment` target raise `AttributeError` in
  both purexml and defusedxml. Guarding would silently drop comments (diverge).
- **Codex, early-break retains parser state (P2)** — real but **stdlib-universal**
  (defusedxml retains identically via the same stdlib iterator); freed at next GC; no
  equivalence-preserving prompt fix (preserving `.root`). Documented in the docstring;
  recorded as a mirror-plus candidate.
- **Gemini cross-model LOW** — `_setevents` private-API coupling: the accepted,
  documented Option-A tradeoff; mitigated by the CI matrix + the 612-stream sweep.

## Verdict
**Compliant.** iterparse completes the `defusedxml.ElementTree` family; event-stream +
raise-point equivalence proven on real data (612 streams, 0 disagreements), hardened
under streaming (chunked-feed XXE blocked, no I/O), four-leg review run with all bot
findings grounded. CI green 3.10–3.13. Ready to merge. **Build axis 1.0-ready** — what
remains for 1.0 is adoption validation (G1) + the deferred decisions (G5) + the freeze.
