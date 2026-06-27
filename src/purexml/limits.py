"""Opt-in structural-DoS limits (v0.4 mirror-plus).

defusedxml (and libexpat's amplification cap) defend *entity-based* DoS, but
nothing bounds **structural** DoS — pathological-but-legal inputs with no entities
(deep nesting, attribute floods, giant documents). purexml offers opt-in caps for
these. **Off by default** (`limits=None` → no cap → strict defusedxml mirror); a
caller opts in by passing a `Limits` to any entry point's `limits=` parameter.
"""
from __future__ import annotations

from collections import namedtuple

from .errors import AttributesExceeded, DepthExceeded, SizeExceeded

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


# -- shared runtime accounting (v0.14: reused by minidom + sax so the cap semantics
#    are identical to the ElementTree path's _parser.py accounting) ----------------

class _LimitCounter:
    """Per-parse depth + attribute accounting. ``enter`` is called at each element start
    (with the element's attribute count), ``leave`` at each end — raising the same
    `DepthExceeded` / `AttributesExceeded` the ElementTree path raises. `None` caps = no check."""

    __slots__ = ("max_depth", "max_attributes", "depth")

    def __init__(self, limits: Limits) -> None:
        self.max_depth = limits.max_depth
        self.max_attributes = limits.max_attributes
        self.depth = 0

    def enter(self, tag: str, n_attrs: int) -> None:
        if self.max_attributes is not None and n_attrs > self.max_attributes:
            raise AttributesExceeded(tag, n_attrs, self.max_attributes)
        if self.max_depth is not None:
            self.depth += 1
            if self.depth > self.max_depth:
                raise DepthExceeded(self.depth, self.max_depth)

    def leave(self) -> None:
        if self.max_depth is not None:
            self.depth -= 1

    def reset(self) -> None:
        self.depth = 0


def _counter_for(limits: Limits | None) -> _LimitCounter | None:
    """A counter iff a depth/attr cap is actually set (else None → zero overhead)."""
    if limits is not None and (limits.max_depth is not None
                               or limits.max_attributes is not None):
        return _LimitCounter(limits)
    return None


def _check_max_bytes(data: str | bytes, limits: Limits | None) -> None:
    """Enforce ``max_bytes`` on a known-length input (parseString path), raising
    `SizeExceeded`. Counts UTF-8 bytes for str, matching the ElementTree `feed` accounting."""
    if limits is not None and limits.max_bytes is not None:
        n = len(data) if isinstance(data, bytes) else len(data.encode("utf-8"))
        if n > limits.max_bytes:
            raise SizeExceeded(n, limits.max_bytes)
