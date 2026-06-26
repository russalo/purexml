# COMPLIANCE — purexml v0.13.0

Audit of v0.13.0 against the approved spec
[`v0.13.0_RFC_Specification.md`](v0.13.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#34](https://github.com/russalo/purexml/pull/34), branch `v0.13.0-xmlrpc`. Suite:
**266 passed, 1 gated-skip.**

## Theme
`purexml.xmlrpc` — the last non-negligible measured module (`defusedxml.xmlrpc`, 343 sites), a
**different shape**: a monkeypatch of the stdlib `xmlrpc`, not a parse fn. **Option C** (lazy
imports) keeps the network-capable import out of `import purexml`. Completes the measured breadth
surface.

## §2/§3 scope + design (resolved to option C)

| Req | Implementation | Status |
|---|---|---|
| `monkey_patch()`/`unmonkey_patch()` patch/restore `xmlrpc.client.FastParser`/`GzipDecodedResponse`/`gzip_decode` (+ server gzip) | `xmlrpc.py` | ✅ |
| Defused `xmlrpc.client.ExpatParser` subclass with purexml's forbid_* handlers (arg-mapped) | lazy class factory | ✅ |
| Gzip-bomb defense (`MAX_DATA`=30 MB; `defused_gzip_decode`; `DefusedGzipDecodedResponse`) | `xmlrpc.py` | ✅ |
| **Option C — lazy imports** (no `xmlrpc`/`gzip` at module top; classes built lazily) | all imports inside functions/factories | ✅ |
| Restore captured originals on undo (incl. `FastParser`, PR-bot fix) | `_orig_*` caches | ✅ |
| `defuse_stdlib()` out of scope | not implemented | ✅ |

## §4 no-I/O guard (the load-bearing part)

| Req | Evidence | Status |
|---|---|---|
| **Import-time no-I/O preserved** — `import purexml.xmlrpc` pulls no transport | `test_import_is_lazy_no_network` (subprocess: `xmlrpc.client` absent at import, present only after `monkey_patch()`) | ✅ |
| Static guard: `XMLRPC_EXTRA` carve-out for the lazy `xmlrpc`/`gzip` only | `test_no_io.py` | ✅ |
| `socket`/`http`/`urllib` stay FORBIDDEN even for `xmlrpc.py` (purexml never imports the transport) | `test_src_imports_no_io_or_exec_modules` (no carve-out) | ✅ |

## §6 acceptance bar

| Req | Evidence | Status |
|---|---|---|
| defused parser blocks entity/DTD/external with purexml's exceptions + backstops | `test_defused_xmlrpc_parser_blocks` / `_forbid_dtd` / `_backstops` | ✅ |
| gzip-bomb: payload past `MAX_DATA` raises; normal round-trips; **`read(-1)` bounded** | `test_gzip_decode_bomb_blocked`, `test_gzip_response_read_default_negative_n_is_bounded` | ✅ |
| malformed gzip → `ValueError` (not `BadGzipFile`) — server 400 path | `test_gzip_decode_invalid_data_raises_valueerror` | ✅ |
| `monkey_patch`/`unmonkey_patch` round-trip; **prior FastParser restored** | `test_unmonkey_*`, `test_unmonkey_restores_prior_fast_parser` | ✅ |
| static guard passes; mypy `--strict` + ruff clean; coverage ≥90% | CI; xmlrpc **97%** | ✅ |
| Docs sweep; HISTORY row; four-leg; this compliance | done (incl. SECURITY supported-versions, PUBLIC_CONTRACT version) | ✅ |

## Identity note
xmlrpc fit purexml's "pure no-I/O parse surface" identity LEAST (network-capable import + global
monkeypatch + a non-XML gzip defense). Option C (ratified) contains it: the network-capable import
is opt-in (only `monkey_patch()`), proven by the subprocess test — so `import purexml` stays
network-free. Recorded in the RFC §2/§4 + `scratch/v0.13.0_RFC_DRAFT.md` (the identity analysis).

## Four-leg review — ALL FOUR RUN (feature minor, security-load-bearing)

| Leg | Result |
|---|---|
| 1 — in-house (inline grounded probes + battery) | ✅ no findings. Lazy guarantee proven (subprocess); defused parser + backstops; gzip-bomb cap; patch round-trip (fixture restores global state). |
| 2 — Gemini cross-model (`gem.sh`) | ⚠️ UNAVAILABLE (daily free-tier quota, 429). Covered by leg-1 probes + leg-4. |
| 3 — empirical sweep | ✅ ElementTree mirror **0 disagreements** — untouched. |
| 4 — PR bots (Codex + Gemini Code Assist) | ✅ **4 findings, all real, all fixed** — see below. |

### Findings dispositions — all grounded + fixed (commit `34855f2`)
- **gzip-bomb via `read(-1)`** (Gemini security-high / Codex P2): the default `n=-1` decompressed
  the whole stream before the cap check → bomb could allocate past `MAX_DATA`. Capped negative `n`
  to `left+1`. Test added.
- **malformed gzip** (Codex P2): restored defusedxml's `OSError → ValueError("invalid data")` (else
  `BadGzipFile` escapes `xmlrpc.server`'s 400 handler). Test added.
- **FastParser reversibility** (Codex P2 / Gemini): `unmonkey_patch` clobbered to `None`; now
  captures + restores the original. (Gemini's "ExpatParser default" premise is wrong — it's `None`
  — fixed for Codex's reversibility reason.) Test added.
- **subprocess test PYTHONPATH** (Codex P2): pass `PYTHONPATH=src` so the lazy test works in a
  checkout + installed.

## Verdict
**Compliant.** `purexml.xmlrpc` implemented per the approved RFC (option C lazy imports); the
no-I/O-at-import guarantee proven behaviorally; gzip-bomb defense holds (incl. the `read(-1)`
hole the bots caught); four-leg run with all four PR-bot findings grounded + fixed. **This
completes the measured breadth surface.** CI green 3.10–3.13. Ready to merge.
