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
"""ASE Calculator implementation for the xtb program."""

from typing import List, Optional

from ..interface import Calculator, Param, XTBException
import ase.calculators.calculator as ase
from ase.atoms import Atoms
from ase.units import Hartree, Bohr


class XTB(ase.Calculator):
    """Base calculator for xtb related methods."""

    implemented_properties = [
        "energy",
        "forces",
        "charges",
    ]

    default_options = {
        "method": Param.GFN2xTB,
    }

    _res = None
    _xtb = None

    def __init__(
        self,
        atoms: Optional[Atoms] = None,
        **kwargs,
    ):
        """Construct the XTB base calculator object."""

        ase.Calculator.__init__(
            self, atoms=atoms, **kwargs
        )

        # loads the default parameters and updates with actual values
        self.parameters = self.get_default_parameters()
        # now set all parameters
        self.set(**kwargs)

    def set(self, **kwargs):
        """"""

        changed_parameters = ase.Calculator.set(self, **kwargs)

        return changed_parameters

    def calculate(
        self,
        atoms: Optional[Atoms] = None,
        properties: List[str] = None,
        system_changes: List[str] = ase.all_changes,
    ):
        """"""

        if not properties:
            properties = ['energy']
        ase.Calculator.calculate(self, atoms, properties, system_changes)

        try:
            if self.atoms.cell.size == 9:
                _cell = self.atoms.cell
            elif self.atoms.cell.size == 3:
                _cell = np.diag(self.atoms.cell)
            else:
                _cell = None

            self._xtb = Calculator(
                self.parameters.method,
                self.atoms.numbers,
                self.atoms.positions / Bohr,
                lattice=_cell / Bohr,
                periodic=self.atoms.pbc,
            )
        except XTBException as ee:
            raise ase.InputError("Cannot construct calculator for xtb")
        except ValueError:
            raise ase.InputError("Invalid geometry input for xtb calculator")

        try:
            self._res = self._xtb.singlepoint(self._res)
        except XTBException as ee:
            self._xtb.show(ee.value)
            raise ase.CalculationFailed("xtb could not evaluate input")

        self.results["energy"] = self._res.get_energy() * Hartree
        self.results["forces"] = -self._res.get_gradient() * Hartree/Bohr
        self.results["charges"] = self._res.get_charges()
