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
"""Wrapper around the C-API of the xtb shared library."""

from typing import List, Optional
from enum import Enum, auto
import numpy as np

try:
    from ._libxtb import ffi as _ffi, lib as _lib
except ImportError:
    raise Exception("xtb C extension unimportable, cannot use C-API")


class Param(Enum):
    """Possible parametrisations for the Calculator class"""

    GFN2xTB = auto()
    GFN1xTB = auto()
    GFN0xTB = auto()
    GFNFF = auto()


class Environment:
    """Calculation environment"""

    _env = _ffi.NULL

    def __init__(self):
        """Create new xtb calculation environment object"""
        self._env = _lib.xtb_newEnvironment()

    def __del__(self):
        """Delete a xtb calculation environment object"""
        ptr = _ffi.new("xtb_TEnvironment *")
        ptr[0], self._env = self._env, _ffi.NULL
        _lib.xtb_delEnvironment(ptr)

    def check(self) -> int:
        """Check current status of calculation environment"""
        return _lib.xtb_checkEnvironment(self._env)

    def show(self, message: str) -> None:
        """Show and empty error stack"""
        _message = _ffi.new("char[]", message)
        _lib.xtb_showEnvironment(self._env, _message)

    def set_output(self, filename: str) -> None:
        """Bind output from this environment"""
        _filename = _ffi.new("char[]", filename)
        _lib.xtb_setOutput(self._env, _filename)

    def release_output(self) -> None:
        """Release output unit from this environment"""
        _lib.xtb_releaseOutput(self._env)

    def set_verbosity(self, verbosity: int) -> None:
        """Set verbosity of calculation output"""
        _lib.xtb_setVerbosity(self._env, verbosity)


class Molecule(Environment):
    """Molecular structure data"""

    _mol = _ffi.NULL

    def __init__(
        self,
        numbers: np.ndarray,
        positions: np.ndarray,
        charge: Optional[float] = None,
        uhf: Optional[int] = None,
        lattice: Optional[List[float]] = None,
        periodic: Optional[List[bool]] = None,
    ):
        """Create new molecular structure data"""
        Environment.__init__(self)
        if positions.size % 3 != 0:
            raise ValueError("Expected tripels of cartesian coordinates")

        if 3 * numbers.size != positions.size:
            raise ValueError("Dimension missmatch between numbers and postions")

        self._natoms = len(numbers)
        _numbers = np.array(numbers, dtype="i4")
        _positions = np.array(positions, dtype=float)

        _charge = _ref("double", charge)
        _uhf = _ref("int", uhf)

        if lattice is not None:
            if len(lattice) != 9:
                raise ValueError("Invalid lattice provided")
            _lattice = np.array(lattice, dtype="float")
        else:
            _lattice = None

        if periodic is not None:
            if len(periodic) != 3:
                raise ValueError("Invalid periodicity provided")
            _periodic = np.array(periodic, dtype="bool")
        else:
            _periodic = None

        self._mol = _lib.xtb_newMolecule(
            self._env,
            _ref("int", self._natoms),
            _cast("int*", _numbers),
            _cast("double*", _positions),
            _charge,
            _uhf,
            _cast("double*", _lattice),
            _cast("bool*", _periodic),
        )

        if self.check() != 0:
            raise ValueError("Could not initialize molecular structure data")

    def __del__(self):
        """Delete molecular structure data"""
        Environment.__del__(self)
        ptr = _ffi.new("xtb_TMolecule *")
        ptr[0], self._mol = self._mol, _ffi.NULL
        _lib.xtb_delMolecule(ptr)

    def __len__(self):
        return self._natoms

    def update(
        self, positions: List[float], lattice: Optional[List[float]] = None,
    ):
        """Update coordinates and lattice parameters"""

        if 3 * len(self) != len(positions):
            raise ValueError("Dimension missmatch for postions")
        _positions = np.array(positions, dtype="float")

        if lattice is not None:
            if len(lattice) != 9:
                raise ValueError("Invalid lattice provided")
            _lattice = np.array(lattice, dtype="float")
        else:
            _lattice = _ffi.NULL

        _lib.xtb_updateMolecule(
            self._env,
            self._mol,
            _cast("double*", _positions),
            _cast("double*", _lattice),
        )

        if self.check() != 0:
            raise ValueError("Could not update molecular structure data")


class Results(Environment):
    """Calculation results"""

    _res = _ffi.NULL

    def __init__(self, mol: Molecule):
        """Create new singlepoint results object"""
        Environment.__init__(self)
        self._res = _lib.xtb_newResults()
        self._natoms = len(mol)

    def __del__(self):
        """Delete singlepoint results object"""
        Environment.__del__(self)
        ptr = _ffi.new("xtb_TResults *")
        ptr[0], self._res = self._res, _ffi.NULL
        _lib.xtb_delResults(ptr)

    def __len__(self):
        return self._natoms

    def get_energy(self):
        """Query singlepoint results object for energy"""
        _energy = _ffi.new("double *")
        _lib.xtb_getEnergy(self._env, self._res, _energy)
        if self.check() != 0:
            raise ValueError("Energy is not available")
        return _energy[0]

    def get_gradient(self):
        """Query singlepoint results object for gradient"""
        _gradient = np.zeros((len(self), 3))
        _lib.xtb_getGradient(self._env, self._res, _cast("double*", _gradient))
        if self.check() != 0:
            raise ValueError("Gradient is not available")
        return _gradient

    def get_virial(self):
        """Query singlepoint results object for virial"""
        _virial = np.zeros((3, 3))
        _lib.xtb_getVirial(self._env, self._res, _cast("double*", _virial))
        if self.check() != 0:
            raise ValueError("Virial is not available")
        return _virial

    def get_dipole(self):
        """Query singlepoint results object for dipole"""
        _dipole = np.zeros(3)
        _lib.xtb_getDipole(self._env, self._res, _cast("double*", _dipole))
        if self.check() != 0:
            raise ValueError("Dipole is not available")
        return _dipole

    def get_charges(self):
        """Query singlepoint results object for partial charges"""
        _charges = np.zeros(len(self))
        _lib.xtb_getCharges(self._env, self._res, _cast("double*", _charges))
        if self.check() != 0:
            raise ValueError("Charges are not available")
        return _charges

    def get_bond_orders(self):
        """Query singlepoint results object for bond orders"""
        _bond_orders = np.zeros((len(self), len(self)))
        _lib.xtb_getBondOrders(self._env, self._res, _cast("double*", _bond_orders))
        if self.check() != 0:
            raise ValueError("Bond orders are not available")
        return _bond_orders


class Calculator(Molecule):
    """Singlepoint calculator"""

    _calc = _ffi.NULL

    _loader = {
        Param.GFN2xTB: _lib.xtb_loadGFN2xTB,
        Param.GFN1xTB: _lib.xtb_loadGFN1xTB,
        Param.GFN0xTB: _lib.xtb_loadGFN0xTB,
        Param.GFNFF: _lib.xtb_loadGFNFF,
    }

    def __init__(
        self,
        param: Param,
        numbers: List[int],
        positions: List[float],
        charge: Optional[float] = None,
        uhf: Optional[int] = None,
        lattice: Optional[List[float]] = None,
        periodic: Optional[List[bool]] = None,
    ):
        """Create new calculator object"""
        Molecule.__init__(
            self, numbers, positions, charge, uhf, lattice, periodic,
        )
        self._calc = _lib.xtb_newCalculator()
        self._load(param)

    def __del__(self):
        """Delete calculator object"""
        Molecule.__del__(self)
        ptr = _ffi.new("xtb_TCalculator *")
        ptr[0], self._calc = self._calc, _ffi.NULL
        _lib.xtb_delCalculator(ptr)

    def _load(self, param: Param):
        """Load parametrisation data into calculator"""

        self._loader[param](
            self._env, self._mol, self._calc, _ffi.NULL,
        )

        if self.check() != 0:
            raise ValueError("Could not load parametrisation data")

    def singlepoint(self, res: Optional[Results] = None) -> Results:
        """Perform singlepoint calculation"""

        _res = Results(self) if res is None else res
        _lib.xtb_singlepoint(
            self._env, self._mol, self._calc, _res._res,
        )

        if self.check() != 0:
            raise ValueError("Single point calculation failed")

        return _res


def _cast(ctype, array):
    """Cast a numpy array to a FFI pointer"""
    return _ffi.NULL if array is None else _ffi.cast(ctype, array.ctypes.data)


def _ref(ctype, value):
    """Create a reference to a value"""
    if value is None:
        return _ffi.NULL
    ref = _ffi.new(ctype + "*")
    ref[0] = value
    return ref
