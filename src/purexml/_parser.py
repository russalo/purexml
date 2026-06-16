"""Hardened XML parse, stdlib-only.

Built directly on ``xml.parsers.expat`` + ``xml.etree.ElementTree.TreeBuilder``
(measure-first F5: the CPython C-accelerated ``ElementTree.XMLParser`` does not
expose its underlying expat parser, so the blocking handlers cannot be installed
on it — and defusedxml's workaround imports the *pure-Python* parser via fragile
module surgery, which this avoids).

The expat→tree glue (namespace separator ``"}"``, ordered attributes, buffered
text, Clark-notation name fixup, undefined-entity handling) mirrors the stdlib
``XMLParser`` so the resulting ``Element`` tree is identical to the stdlib's /
defusedxml's. On top of that glue, three blocking handlers reproduce defusedxml's
default configuration (``forbid_dtd=False, forbid_entities=True,
forbid_external=True``):

  * ``EntityDeclHandler`` / ``UnparsedEntityDeclHandler`` -> EntitiesForbidden
    (any entity declaration, general or parameter — blocked before expansion).
  * ``ExternalEntityRefHandler`` -> ExternalReferenceForbidden (external
    resolution actually attempted by expat).
  * no ``StartDoctypeDeclHandler`` -> an entity-free DOCTYPE / internal DTD is
    allowed (forbid_dtd is False). An *unresolved* external-DTD declaration
    therefore parses and triggers no fetch (measure-first F2).
"""

import xml.parsers.expat as _expat
from xml.etree.ElementTree import ParseError, TreeBuilder

from .errors import EntitiesForbidden, ExternalReferenceForbidden

__all__ = ["fromstring"]


class _HardenedParser:
    def __init__(self):
        parser = _expat.ParserCreate(None, "}")
        target = TreeBuilder()
        self.parser = parser
        self.target = target
        self._error = _expat.error
        self._names = {}  # qname memo, as in the stdlib
        self.entity = {}  # always empty: every entity *declaration* is blocked

        # --- tree-building glue (mirrors stdlib xml.etree XMLParser) ---
        parser.DefaultHandlerExpand = self._default
        parser.StartElementHandler = self._start
        parser.EndElementHandler = self._end
        parser.CharacterDataHandler = target.data
        parser.CommentHandler = target.comment
        parser.ProcessingInstructionHandler = target.pi
        parser.buffer_text = 1
        parser.ordered_attributes = 1

        # --- security handlers (defusedxml-default equivalents) ---
        parser.EntityDeclHandler = self._forbid_entity_decl
        parser.UnparsedEntityDeclHandler = self._forbid_unparsed_entity_decl
        parser.ExternalEntityRefHandler = self._forbid_external_ref
        # forbid_dtd is False by contract -> no StartDoctypeDeclHandler installed.

    # ---- blocking handlers ----
    def _forbid_entity_decl(self, name, is_parameter_entity, value, base,
                            sysid, pubid, notation_name):
        raise EntitiesForbidden(name, sysid, pubid)

    def _forbid_unparsed_entity_decl(self, name, base, sysid, pubid, notation_name):
        raise EntitiesForbidden(name, sysid, pubid)

    def _forbid_external_ref(self, context, base, sysid, pubid):
        raise ExternalReferenceForbidden(sysid, pubid)

    # ---- tree-building glue ----
    def _fixname(self, key):
        try:
            return self._names[key]
        except KeyError:
            name = key
            if "}" in name:
                name = "{" + name
            self._names[key] = name
            return name

    def _start(self, tag, attr_list):
        fixname = self._fixname
        tag = fixname(tag)
        attrib = {}
        if attr_list:
            for i in range(0, len(attr_list), 2):
                attrib[fixname(attr_list[i])] = attr_list[i + 1]
        return self.target.start(tag, attrib)

    def _end(self, tag):
        return self.target.end(self._fixname(tag))

    def _default(self, text):
        # Mirrors the stdlib: a reference to an entity that was never defined
        # raises an undefined-entity error (surfaced as ParseError by feed_close).
        # Since every declaration is blocked above, self.entity is always empty,
        # so any non-predefined entity reference lands here and raises — matching
        # defusedxml's pure-parser behavior. Predefined entities (&amp; etc.) are
        # resolved by expat directly and never reach this handler. DOCTYPE text
        # and other default content are ignored (TreeBuilder has no doctype hook).
        if text[:1] == "&":
            try:
                self.target.data(self.entity[text[1:-1]])
            except KeyError:
                err = self._error(
                    "undefined entity %s: line %d, column %d"
                    % (text, self.parser.ErrorLineNumber,
                       self.parser.ErrorColumnNumber)
                )
                err.code = 11  # XML_ERROR_UNDEFINED_ENTITY
                err.lineno = self.parser.ErrorLineNumber
                err.offset = self.parser.ErrorColumnNumber
                raise err

    def _raiseerror(self, value):
        err = ParseError(value)
        err.code = value.code
        err.position = (value.lineno, value.offset)
        raise err

    def feed_close(self, text):
        try:
            try:
                self.parser.Parse(text, True)
            except self._error as v:
                # Only genuine expat parse errors become ParseError. Blocking
                # exceptions (EntitiesForbidden / ExternalReferenceForbidden) are
                # not expat.error, so they propagate to the caller unchanged.
                self._raiseerror(v)
            return self.target.close()
        finally:
            # Break the reference cycle: the expat parser holds our bound-method
            # handlers (-> self) and we hold the parser (self.parser). Without this
            # the instance is reclaimable only by cyclic GC, not refcounting — under
            # high-volume parsing that defers cleanup. Mirrors stdlib XMLParser.close.
            self.parser = None
            self.target = None


def fromstring(text):
    """Parse XML *text* into an ``xml.etree.ElementTree.Element``, safely.

    Behaviorally equivalent to ``defusedxml.ElementTree.fromstring`` at its
    default configuration:

    * entity declarations are blocked at declaration time
      (``EntitiesForbidden``) — billion-laughs / quadratic / declared-XXE;
    * external reference *resolution* is blocked (``ExternalReferenceForbidden``)
      with no fetch and no file read;
    * an entity-free DOCTYPE / internal DTD is allowed, as is an unresolved
      external-DTD declaration (no fetch occurs);
    * malformed input raises ``xml.etree.ElementTree.ParseError``.

    Both refusal types subclass ``ValueError``. Standard library only; no runtime
    dependency on defusedxml.
    """
    return _HardenedParser().feed_close(text)
