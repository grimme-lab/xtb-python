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

from xtb.interface import Param, Solvent
from xtb.utils import get_method, get_solvent
from pytest import raises


def test_solvents():
    """Check conversion from strings to solvent enumerators"""

    assert get_solvent("water") == Solvent.h2o
    assert get_solvent("Water") == Solvent.h2o
    assert get_solvent("h2o") == Solvent.h2o
    assert get_solvent("H2O") == Solvent.h2o

    assert get_solvent("acetone") == Solvent.acetone
    assert get_solvent("Acetone") == Solvent.acetone

    assert get_solvent("acetonitrile") == Solvent.acetonitrile
    assert get_solvent("Acetonitrile") == Solvent.acetonitrile

    assert get_solvent("benzene") == Solvent.benzene
    assert get_solvent("Benzene") == Solvent.benzene

    assert get_solvent("ch2cl2") == Solvent.ch2cl2
    assert get_solvent("CH2Cl2") == Solvent.ch2cl2

    assert get_solvent("chcl3") == Solvent.chcl3
    assert get_solvent("CHCl3") == Solvent.chcl3
    assert get_solvent("chloroform") == Solvent.chcl3

    assert get_solvent("cs2") == Solvent.cs2
    assert get_solvent("CS2") == Solvent.cs2

    assert get_solvent("dmf") == Solvent.dmf
    assert get_solvent("DMF") == Solvent.dmf

    assert get_solvent("dmso") == Solvent.dmso
    assert get_solvent("DMSO") == Solvent.dmso

    assert get_solvent("ether") == Solvent.ether

    assert get_solvent("Methanol") == Solvent.methanol
    assert get_solvent("methanol") == Solvent.methanol

    assert get_solvent("nhexane") == Solvent.nhexane
    assert get_solvent("n-hexane") == Solvent.nhexane

    assert get_solvent("thf") == Solvent.thf
    assert get_solvent("THF") == Solvent.thf

    assert get_solvent("toluene") == Solvent.toluene
    assert get_solvent("Toluene") == Solvent.toluene

    assert get_solvent("unknown") is None


def test_methods():
    """Check conversion from strings to parameter enumerators"""

    assert get_method("GFN2-xTB") == Param.GFN2xTB
    assert get_method("gfn2-xtb") == Param.GFN2xTB
    assert get_method("GFN2XTB") == Param.GFN2xTB

    assert get_method("GFN1-xTB") == Param.GFN1xTB
    assert get_method("gfn1-xtb") == Param.GFN1xTB
    assert get_method("GFN1XTB") == Param.GFN1xTB

    assert get_method("GFN0-xTB") == Param.GFN0xTB
    assert get_method("gfn0-xtb") == Param.GFN0xTB
    assert get_method("GFN0XTB") == Param.GFN0xTB

    assert get_method("GFN-FF") == Param.GFNFF
    assert get_method("gfn-ff") == Param.GFNFF
    assert get_method("GFNFF") == Param.GFNFF

    assert get_method("unknown") is None
