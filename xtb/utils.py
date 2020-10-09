# This file is part of xtb.
#
# Copyright (C) 2020 Sebastian Ehlert
#
# xtb is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xtb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with xtb.  If not, see <https://www.gnu.org/licenses/>.
"""Helper functions to deal with xtb API objects"""

from typing import Optional
from .interface import Solvent, Param


_methods = {
    "gfn2-xtb": Param.GFN2xTB,
    "gfn2xtb": Param.GFN2xTB,
    "gfn1-xtb": Param.GFN1xTB,
    "gfn1xtb": Param.GFN1xTB,
    "ipea-xtb": Param.IPEAxTB,
    "ipeaxtb": Param.IPEAxTB,
    "gfn0-xtb": Param.GFN0xTB,
    "gfn0xtb": Param.GFN0xTB,
    "gfn-ff": Param.GFNFF,
    "gfnff": Param.GFNFF,
}


def get_method(method: str) -> Optional[Param]:
    """Return the correct parameter enumerator for a string input.

    Example
    -------
    >>> get_method('GFN2-xTB')
    <Param.GFN2xTB: 1>
    >>> get_method('gfn2xtb')
    <Param.GFN2xTB: 1>
    >>> get_method('GFN-xTB') is None
    True
    >>> get_method('GFN1-xTB') is None
    False
    """

    return _methods.get(method.lower())


_solvents = {
    "acetone": Solvent.acetone,
    "acetonitrile": Solvent.acetonitrile,
    "benzene": Solvent.benzene,
    "ch2cl2": Solvent.ch2cl2,
    "chcl3": Solvent.chcl3,
    "chloroform": Solvent.chcl3,
    "cs2": Solvent.cs2,
    "dmf": Solvent.dmf,
    "dmso": Solvent.dmso,
    "ether": Solvent.ether,
    "h2o": Solvent.h2o,
    "water": Solvent.h2o,
    "methanol": Solvent.methanol,
    "nhexane": Solvent.nhexane,
    "n-hexane": Solvent.nhexane,
    "thf": Solvent.thf,
    "toluene": Solvent.toluene,
}


def get_solvent(solvent: str) -> Optional[Solvent]:
    """Return the correct solvent enumerator for a string input."""

    return _solvents.get(solvent.lower())
