"""Opt-in structural-DoS limits (v0.4 mirror-plus).

defusedxml (and libexpat's amplification cap) defend *entity-based* DoS, but
nothing bounds **structural** DoS — pathological-but-legal inputs with no entities
(deep nesting, attribute floods, giant documents). purexml offers opt-in caps for
these. **Off by default** (`limits=None` → no cap → strict defusedxml mirror); a
caller opts in by passing a `Limits` to any entry point's `limits=` parameter.
"""
from collections import namedtuple

__all__ = ["Limits", "RECOMMENDED_LIMITS"]

#: Structural caps. ``None`` for any field means "no cap" on that axis.
#:
#:   max_depth      — max element nesting depth (guards deep-tree RecursionError +
#:                    memory on the consumer's traversal).
#:   max_attributes — max attributes on a single element (guards attribute floods).
#:   max_bytes      — max total input fed (guards giant-document memory).
Limits = namedtuple("Limits", ["max_depth", "max_attributes", "max_bytes"],
                    defaults=[None, None, None])

#: A vetted preset with generous headroom over real-world maxima (measured
#: 2026-06-16 across 584 real OOXML/tika parts: depth 24, attrs 18, ~580 KB), so it
#: rejects no legitimate document while catching structural pathology. PROVISIONAL —
#: the values may evolve (see the v0.4 RFC); opt in explicitly, don't rely on the
#: exact numbers. `max_depth=1000` also sits near CPython's default recursion limit,
#: above which a consumer's recursive traversal/serialization would fail anyway.
RECOMMENDED_LIMITS = Limits(max_depth=1000, max_attributes=256,
                            max_bytes=100 * 1024 * 1024)
