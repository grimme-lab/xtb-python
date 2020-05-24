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
import numpy as np


class XTB(ase.Calculator):
    """Base calculator for xtb related methods."""

    implemented_properties = [
        "energy",
        "forces",
        "charges",
        "dipole",
        "stress",
    ]

    default_options = {
        "method": Param.GFN2xTB,
    }

    _res = None
    _xtb = None

    def __init__(
        self, atoms: Optional[Atoms] = None, **kwargs,
    ):
        """Construct the xtb base calculator object."""

        ase.Calculator.__init__(self, atoms=atoms, **kwargs)

        # loads the default parameters and updates with actual values
        self.parameters = self.get_default_parameters()
        # now set all parameters
        self.set(**kwargs)

    def set(self, **kwargs):
        """Set new parameters to xtb"""

        changed_parameters = ase.Calculator.set(self, **kwargs)

        # Always reset the xtb calculator for now
        if changed_parameters:
            self.reset()

        return changed_parameters

    def reset(self):
        """Clear all information from old calculation"""
        ase.Calculator.reset(self)

        self._res = None

    def calculate(
        self,
        atoms: Optional[Atoms] = None,
        properties: List[str] = None,
        system_changes: List[str] = ase.all_changes,
    ):
        """Perform actual calculation with by calling the xtb API"""

        if not properties:
            properties = ["energy"]
        ase.Calculator.calculate(self, atoms, properties, system_changes)

        try:
            _cell = self.atoms.cell
            _periodic = self.atoms.pbc
            _charge = self.atoms.get_initial_charges().sum()
            _uhf = int(self.atoms.get_initial_magnetic_moments().sum().round())

            self._xtb = Calculator(
                self.parameters.method,
                self.atoms.numbers,
                self.atoms.positions / Bohr,
                _charge,
                _uhf,
                _cell / Bohr,
                _periodic,
            )

        except XTBException:
            raise ase.InputError("Cannot construct calculator for xtb")

        try:
            self._res = self._xtb.singlepoint(self._res)
        except XTBException:
            self._xtb.show("Single point calculation failed")
            raise ase.CalculationFailed("xtb could not evaluate input")

        # These properties are garanteed to exist for all implemented calculators
        self.results["energy"] = self._res.get_energy() * Hartree
        self.results["free_energy"] = self.results["energy"]
        self.results["forces"] = -self._res.get_gradient() * Hartree / Bohr
        self.results["dipole"] = self._res.get_dipole() * Bohr
        # stress tensor is only returned for periodic systems
        if self.atoms.pbc.any():
            _stress = self._res.get_virial() * Hartree / self.atoms.get_volume()
            self.results["stress"] = _stress.flat[[0, 4, 8, 5, 2, 1]]
        # Not all xtb calculators provide access to partial charges yet,
        # this is mainly an issue for the GFN-FF calculator
        try:
            self.results["charges"] = self._res.get_charges()
        except XTBException:
            self._xtb.show("Charges not provided by calculator")
