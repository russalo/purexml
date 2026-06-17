# COMPLIANCE — purexml v0.7.0

Audit of v0.7.0 against the approved spec
[`v0.7.0_RFC_Specification.md`](v0.7.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#15](https://github.com/russalo/purexml/pull/15), branch `v0.7.0`. Suite: **178 passed,
1 gated-skip.**

## Theme
The `python -m purexml` posture CLI over the read-only `security_report()` — the
10-second demo a cold evaluator runs. First build of the publish-worthy-debut push.
**Report/CLI-only — no parse-behavior change.**

## §2 Capability + §6 design (resolved to the approved leans)

| Req | Implementation | Status |
|---|---|---|
| `python -m purexml` → human report, **exit 0 (informs)** | `__main__.py` (prints `security_report()`) | ✅ |
| `--json` → `purexml_version` + `as_dict()` (machine-readable, PROVISIONAL) | `__main__.py` + `SecurityReport.as_dict()` | ✅ |
| `--check [--min-expat X.Y.Z]` → opt-in CI gate, exit code vs floor; pin-your-floor | `__main__.py` (default floor = `RECOMMENDED_EXPAT_VERSION`) | ✅ |
| `--version` | `__main__.py` | ✅ |
| `as_dict()` JSON-safe (tuples→str, mappingproxy→dict, Limits→dict/None, notes→list) | `_expat_security.py` | ✅ |
| `__main__.py` reads `EXPAT_VERSION` at call time (consistent w/ `security_report()`) | `_es.EXPAT_VERSION` references | ✅ |

## §4 No-I/O guard (the design wrinkle)
`__main__.py` is the package's **one I/O boundary**: the guard carve-out widens the
allowlist by `{argparse, json, sys}` **for that file only**, while it stays under the
**unconditional FORBIDDEN** check (no socket/urllib/subprocess/os/…), and every other
`src/` file keeps the strict `{xml, collections, types}` allowlist. Both halves asserted
by `test_no_io`. The guarantee is *sharper* (the I/O boundary is named + bounded), not weaker. ✅

## §7 Acceptance bar

| Req | Evidence | Status |
|---|---|---|
| No parse-behavior change; default mirror byte-equivalent | empirical sweep **372/0**; full suite green | ✅ |
| `python -m purexml` prints posture, **exits 0** | `test_default_prints_report_exit_zero` | ✅ |
| `--check` exit codes correct vs floor (below/at/above, monkeypatched) | `test_check_*` | ✅ |
| `--min-expat` pins correctly; malformed fails cleanly; **requires `--check`** | `test_check_min_expat_pins_floor`, `test_malformed_min_expat_errors`, `test_min_expat_without_check_errors` | ✅ |
| `--json` round-trips the data; shape PROVISIONAL | `test_json_flag_*`, `test_as_dict_is_json_safe_and_complete` | ✅ |
| No-I/O guard holds (parse strict; CLI bounded) | `test_no_io` (incl. `__main__.py` carve-out) | ✅ |
| Read-only/deterministic; safe to run repeatedly | reads only constants + report | ✅ |

## Four-leg review — ALL FOUR RUN (full tier per the rubric: new public surface)

| Leg | Result |
|---|---|
| 1 — in-house (1 decorrelated finder) | ✅ **clean, no findings** — carve-out scoped + still under FORBIDDEN, `--check` can't wrongly pass below floor, `as_dict` JSON-safe, call-time version read, parse path untouched, non-tautological tests. |
| 2 — Gemini cross-model (`gem.sh`) | ✅ "no defects… correct-by-design" on all four angles. |
| 3 — empirical sweep | ✅ **372/0** — mirror byte-identical. |
| 4 — PR bots | ✅ Codex no findings; Gemini 1 finding (high) — real, **fixed** (commit c9f2429). |

### Findings dispositions — grounded; nothing declined
- **Pre-open (legs 1–3):** clean; nothing to fix. (Also exercised the new libexpat-currency
  gate → IN-SYNC, and caught/fixed a stale v0.6.0 HISTORY shipped-date in the doc sweep.)
- **PR-bot (leg 4) — Gemini high/security:** `--min-expat` without `--check` silently
  no-op'd (exit 0) — a CI gate a user could think was active. Fixed: `parser.error(
  "--min-expat requires --check")` fails loudly (exit 2); regression test added.
- Codex: no findings.

## Freeze note
The CLI surface + `as_dict()` JSON shape are **PROVISIONAL at 1.0** (with the posture
report, per ROADMAP). The `python -m` entry stays; the `purexml` console-script name is a
publish-time decision. The CLI *informs* by default; enforcement is opt-in via `--check`.

## Verdict
**Compliant.** The posture CLI shipped per the approved RFC; report/CLI-only, mirror proven
byte-equivalent (372/0); four-leg review run with the one PR-bot finding grounded and fixed.
CI green 3.10–3.13. Ready to merge.
