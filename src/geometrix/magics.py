"""IPython cell magic for the DSL."""

from __future__ import annotations

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

from geometrix.api import geom


@magics_class
class GeomMagics(Magics):
    @magic_arguments()
    @argument("--height", type=int, default=420, help="Viewer height in pixels")
    @cell_magic
    def geom(self, line: str, cell: str) -> None:
        args = parse_argstring(self.geom, line)
        program = geom(cell)
        program.show(height=args.height)


def load_ipython_extension(ipython) -> None:
    ipython.register_magics(GeomMagics)
