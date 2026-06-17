# purexml ⇄ defusedxml — equivalence report

> **Generated artifact — do not hand-edit.** Regenerate with
> `./.venv/bin/python scratch/review/gen_equivalence_report.py <date>`
> (v0.5 RFC §3B). Drop-in equivalence is a *published fact per release*,
> proven by oracle-gating against `defusedxml`, not asserted.

- **purexml version:** 0.5.0
- **Generated:** 2026-06-17
- **Runtime:** Python 3.12.3, libexpat 2.6.1
- **Result:** ✅ EQUIVALENT — **0 disagreements**

Equivalence = **C14N-equal-or-both-raise**: for every input, purexml and
defusedxml either both raise, or both parse to an identical canonical
(C14N) tree. Exception *types* differ by design (purexml has its own
hierarchy); only the parse-vs-raise *kind* and the canonical tree are compared.

## 1. Real-corpus empirical sweep (review leg 3)

Real OOXML/tika inputs, exercised exactly as file-observer parses them
(see `scratch/review/corpus_sweep.py`). The corpus **bytes are never
committed**; the set is pinned by the committed manifest's hash below.

- **corpus_manifest.json sha256:** `7f2239593cd4f3bab4f1e7712f090c42610f898567f814446e3b28e59c01143e`
- **inputs swept:** 372
  - parse + C14N-equal: 364
  - both-raise: 8
  - **disagreements: 0**

## 2. Seeded differential fuzz (always-run, CI gate)

Deterministic generator over allow-path + attack constructs
(`tests/test_fuzz_equivalence.py`), str **and** bytes per document. The
0-disagreements result here is **gate-guaranteed**: a single disagreement
fails the build (the test asserts C14N-equal-or-both-raise), so a report can
only be published when this gate is green — it is not re-measured by this
generator the way §1's corpus counts are.

- seeds × per-seed: 12 × 80 = **960 documents** (× 2 for str+bytes = 1920 comparisons), 0 disagreements.
- Coverage-guided counterpart (Atheris, on-demand): `fuzz/fuzz_equivalence.py`.

## 3. Curated case battery

- allow-path (must parse, C14N-equal to oracle): **9** cases
- block-path (must raise as oracle raises): **6** cases
- plus the version-gated 7-class attack corpus (`tests/test_durability.py`).

## Reproduce

```sh
pip install -e '.[dev]'
python -m pytest                      # seeded fuzz + curated battery + durability
python scratch/review/corpus_sweep.py # real-corpus empirical sweep (needs the corpus)
```
