# COMPLIANCE — purexml v0.12.0

Audit of v0.12.0 against the approved spec
[`v0.12.0_RFC_Specification.md`](v0.12.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#32](https://github.com/russalo/purexml/pull/32), branch `v0.12.0-sax`. Suite:
**250 passed, 1 gated-skip.**

## Theme
`purexml.sax` (the #3 consumer surface, 375 sites) + `purexml.expatreader` (its engine, promoted
deferred→done). Event-driven drop-in for `defusedxml.sax`. New parse surface; security-load-bearing.

## §2 scope + §3 design (resolved to the approved leans)

| Req | Implementation | Status |
|---|---|---|
| `purexml.expatreader` — `DefusedExpatParser` + `create_parser`; handlers installed in `reset()` | `expatreader.py` | ✅ |
| `DefusedExpatParser` **public** (drop-in parity; PR-bot fix) | exported in `__all__` | ✅ |
| `purexml.sax` — `make_parser`/`parse`/`parseString`, defusedxml signature + defaults | `sax.py` | ✅ |
| `parseString` **bytes-only** (mirror; str→TypeError on both) | `BytesIO(string)` | ✅ |
| `errorHandler` default = defusedxml's; `parseString` None-guard | `sax.py` | ✅ |
| Malformed → stdlib `SAXParseException` (not `PureXMLError`) | via `ErrorHandler` | ✅ |
| Reference-cycle hygiene (refined — see below) | `parse()` edge-clear + no-leak | ✅ |

## §5 acceptance bar

| Req | Evidence | Status |
|---|---|---|
| match `defusedxml.sax`: signatures + defaults; allow-path **event streams equal**; attacks block with same exception types; malformed → `SAXParseException` | oracle parity tests (8 ALLOW equal + external-DTD both-block; 6 attacks block on both); `test_malformed_*` | ✅ |
| **No I/O on untrusted input** on the sax `parseString` path | `test_attacks_..._no_io`, `test_external_dtd_blocked_no_fetch`, backstops; decorrelated no-fetch probe across SAX vectors | ✅ |
| `forbid_dtd=True` → DTDForbidden; unparsed-entity + external-ref backstops fire | dedicated tests | ✅ |
| Reader **no-leak** after parse/error (edge cleared + gc-collected) | `test_sax_reader_no_leak_on_error` | ✅ |
| no-I/O structural guard passes; mypy `--strict` + ruff clean; coverage ≥90% | `io` allowlisted w/ justification; sax+expatreader **100%** | ✅ |
| Docs freshness sweep; HISTORY row; four-leg; this compliance | done (incl. SECURITY supported-versions, PUBLIC_CONTRACT version) | ✅ |

## §3.4 refinement (grounded, recorded)
The RFC's "reader refcount-reclaimable after parse/error" goal assumed SAX = minidom. Grounding
showed it is NOT: even clearing handlers/reset, the SAX reader retains a residual cycle in
**pyexpat's exception retention** (a C-level cycle unreachable from Python; **defusedxml.sax has it
too**). Refined to **no-leak parity with the oracle** — purexml clears the reader→parser edge on
every path AND the reader is reclaimed by cyclic GC (test asserts `_parser is None` + `gc.collect()`
reclaims it). An honest refinement of an approved RFC item, not a silent regression.

## Four-leg review — ALL FOUR RUN (feature minor, security-load-bearing)

| Leg | Result |
|---|---|
| 1 — in-house (inline grounded probes) | ✅ no findings. Event-stream parity; no fetch on any SAX path; backstops; bytes-only parity; no-leak. sax+expatreader 100% cov. |
| 2 — Gemini cross-model (`gem.sh`) | ⚠️ UNAVAILABLE (daily free-tier quota, 429). Covered by leg-1 decorrelated probes + leg-4. |
| 3 — empirical sweep | ✅ ElementTree mirror **372/0** — untouched. |
| 4 — PR bots (Codex + Gemini Code Assist) | ✅ Codex: clean. Gemini: 1 real point (`DefusedExpatParser` should be public) — **fixed**. |

### Findings dispositions
- **Gemini (leg 4) — `DefusedExpatParser` public:** `defusedxml.expatreader.DefusedExpatParser` is
  public; a `purexml.expatreader` consumer's `import` would break. Grounded + fixed (public name +
  `__all__`). minidom builders stay private (not a mirrored module). 
- Codex: no comments.

## Freeze note
The sax + expatreader surface is **STABLE-track** at 1.0 (mirrors a frozen reference). The
no-leak (vs refcount-reclaimable) behavior is an inherent pyexpat property shared with the oracle.

## Verdict
**Compliant.** `purexml.sax` + `purexml.expatreader` implemented per the approved RFC (with the
grounded §3.4 no-leak refinement and the public-class drop-in fix); event-stream parity + no-fetch
proven; mirror untouched (372/0); four-leg run with the one PR-bot finding fixed. CI green
3.10–3.13. Ready to merge.
