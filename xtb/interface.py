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
    raise ImportError("xtb C extension unimportable, cannot use C-API")


class XTBException(Exception): ...


class Param(Enum):
    """Possible parametrisations for the Calculator class"""

    GFN2xTB = auto()
    """Self-consistent extended tight binding Hamiltonian with
    anisotropic second order electrostatic contributions,
    third order on-site contributions and self-consistent D4 dispersion.

    Geometry, frequency and non-covalent interactions parametrisation for
    elements up to Z=86.

    Cite as:
    C. Bannwarth, S. Ehlert and S. Grimme.,
    J. Chem. Theory Comput., 2019, 15, 1652-1671.
    DOI: `10.1021/acs.jctc.8b01176 <https://dx.doi.org/10.1021/acs.jctc.8b01176>`_
    """

    GFN1xTB = auto()
    """Self-consistent extended tight binding Hamiltonian with
    isotropic second order electrostatic contributions and
    third order on-site contributions.

    Geometry, frequency and non-covalent interactions parametrisation for
    elements up to Z=86.

    Cite as:
    S. Grimme, C. Bannwarth, P. Shushkov,
    *J. Chem. Theory Comput.*, 2017, 13, 1989-2009.
    DOI: `10.1021/acs.jctc.7b00118 <https://dx.doi.org/10.1021/acs.jctc.7b00118>`_
    """

    GFN0xTB = auto()
    """Experimental non-self-consistent extended tight binding Hamiltonian
    using classical electronegativity equilibration electrostatics and
    extended Hückel Hamiltonian.

    Geometry, frequency and non-covalent interactions parametrisation for
    elements up to Z=86.

    Requires the param_gfn0-xtb.txt parameter file in the ``XTBPATH``
    environment variable to load!

    See:
    P. Pracht, E. Caldeweyher, S. Ehlert, S. Grimme,
    ChemRxiv, 2019, preprint.
    DOI: `10.26434/chemrxiv.8326202.v1 <https://dx.doi.org/10.26434/chemrxiv.8326202.v1>`_
    """

    GFNFF = auto()
    """General force field parametrized for geometry, frequency and non-covalent
    interactions up to Z=86

    ``xtb`` API support is currently experimental.

    Cite as:
    S. Spicher and S. Grimme,
    Angew. Chem. Int. Ed., 2020, accepted article.
    DOI: `10.1002/anie.202004239 <https://dx.doi.org/10.1002/anie.202004239>`_
    """


VERBOSITY_FULL = 2
VERBOSITY_MINIMAL = 1
VERBOSITY_MUTED = 0


def _delete_environment(env):
    """Delete a xtb calculation environment object"""
    ptr = _ffi.new("xtb_TEnvironment *")
    ptr[0] = env
    _lib.xtb_delEnvironment(ptr)


def _new_environment():
    """Create new xtb calculation environment object"""
    return _ffi.gc(_lib.xtb_newEnvironment(), _delete_environment)


def _delete_molecule(mol):
    """Delete molecular structure data"""
    ptr = _ffi.new("xtb_TMolecule *")
    ptr[0] = mol
    _lib.xtb_delMolecule(ptr)


def _new_molecule(env, natoms, numbers, positions, charge, uhf, lattice, periodic):
    """Create new molecular structure data"""
    return _ffi.gc(
        _lib.xtb_newMolecule(
            env,
            natoms,
            numbers,
            positions,
            charge,
            uhf,
            lattice,
            periodic,
        ),
        _delete_molecule,
    )


def _delete_results(res):
    """Delete singlepoint results object"""
    ptr = _ffi.new("xtb_TResults *")
    ptr[0] = res
    _lib.xtb_delResults(ptr)


def _new_results():
    """Create new singlepoint results object"""
    return _ffi.gc(_lib.xtb_newResults(), _delete_results)


def _delete_calculator(calc):
    """Delete calculator object"""
    ptr = _ffi.new("xtb_TCalculator *")
    ptr[0] = calc
    _lib.xtb_delCalculator(ptr)


def _new_calculator():
    """Create new calculator object"""
    return _ffi.gc(_lib.xtb_newCalculator(), _delete_calculator)


class Environment:
    """Calculation environment

    Wraps an API object representing a TEnvironment class in ``xtb``.
    The API object is constructed automatically and deconstructed on garbage
    collection, it stores the IO configuration and the error log of the API.

    All API calls require an environment object, usually this is done
    automatically as all other classes inherent from the calculation
    environment.

    Example
    -------
    >>> from xtb.interface import Environment, VERBOSITY_FULL
    >>> env = Environment()
    >>> env.set_output("error.log")
    >>> env.set_verbosity(VERBOSITY_FULL)
    >>> if env.check != 0:
    ...     env.show("Error message")
    ...
    >>> env.release_output()
    """

    _env = _ffi.NULL

    def __init__(self):
        """Create new xtb calculation environment object"""
        self._env = _new_environment()

    def check(self) -> int:
        """Check current status of calculation environment

        Example
        -------
        >>> if env.check() != 0:
        ...     raise XTBException("Error occured in the API")
        """
        return _lib.xtb_checkEnvironment(self._env)

    def get_error(self) -> str:
        """Check for error messages

        Example
        -------
        >>> if env.check() != 0:
        ...     raise XTBException(env.get_error())
        """
        _message = _ffi.new("char[]", 512)
        _lib.xtb_getError(self._env, _message, _ref("int", 512))
        return _ffi.string(_message).decode()

    def show(self, message: str) -> None:
        """Show and empty error stack"""
        _message = _ffi.new("char[]", message.encode())
        _lib.xtb_showEnvironment(self._env, _message)

    def set_output(self, filename: str) -> None:
        """Bind output from this environment"""
        _filename = _ffi.new("char[]", filename.encode())
        _lib.xtb_setOutput(self._env, _filename)

    def release_output(self) -> None:
        """Release output unit from this environment"""
        _lib.xtb_releaseOutput(self._env)

    def set_verbosity(self, verbosity: int) -> None:
        """Set verbosity of calculation output"""
        _lib.xtb_setVerbosity(self._env, verbosity)


class Molecule(Environment):
    """Molecular structure data

    Represents a wrapped TMolecule API object in ``xtb``.
    The molecular structure data object has a fixed number of atoms and
    immutable atomic identifiers.

    Example
    -------
    >>> from xtb.interface import Molecule
    >>> import numpy as np
    >>> numbers = np.array([8, 1, 1])
    >>> positions = np.array([
    ... [ 0.00000000000000, 0.00000000000000,-0.73578586109551],
    ... [ 1.44183152868459, 0.00000000000000, 0.36789293054775],
    ... [-1.44183152868459, 0.00000000000000, 0.36789293054775]])
    ...
    >>> mol = Molecule(numbers, positions)
    >>> len(mol)
    3
    >>> mol.update(np.zeros(len(mol), 3))  # will fail nuclear fusion check
    xtb.interface.XTBException: Could not update molecular structure data
    >>> mol.show("API message log")  # API error log must be cleared!
    ########################################################################
    [ERROR] API message log
    -1- xtb_api_updateMolecule: Could not update molecular structure
    ########################################################################
    >>> mol.update(positions)

    Raises
    ------
    ValueError
        on invalid input on the Python side of the API

    XTBException
        on errors returned from the API
    """

    _mol = _ffi.NULL

    def __init__(
        self,
        numbers: np.ndarray,
        positions: np.ndarray,
        charge: Optional[float] = None,
        uhf: Optional[int] = None,
        lattice: Optional[np.ndarray] = None,
        periodic: Optional[np.ndarray] = None,
    ):
        """Create new molecular structure data"""
        Environment.__init__(self)
        if positions.size % 3 != 0:
            raise ValueError("Expected tripels of cartesian coordinates")

        if 3 * numbers.size != positions.size:
            raise ValueError("Dimension missmatch between numbers and positions")

        self._natoms = len(numbers)
        _numbers = np.array(numbers, dtype="i4")
        _positions = np.array(positions, dtype=float)

        _charge = _ref("double", charge)
        _uhf = _ref("int", uhf)

        if lattice is not None:
            if lattice.size != 9:
                raise ValueError("Invalid lattice provided")
            _lattice = np.array(lattice, dtype="float")
        else:
            _lattice = None

        if periodic is not None:
            if periodic.size != 3:
                raise ValueError("Invalid periodicity provided")
            _periodic = np.array(periodic, dtype="bool")
        else:
            _periodic = None

        self._mol = _new_molecule(
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
            raise XTBException(self.get_error())

    def __len__(self):
        return self._natoms

    def update(
        self, positions: np.ndarray, lattice: Optional[np.ndarray] = None,
    ):
        """Update coordinates and lattice parameters, both provided in
        atomic units (Bohr).
        The lattice update is optional also for periodic structures.

        Generally, only the cartesian coordinates and the lattice parameters
        can be updated, every other modification, regarding total charge,
        total spin, boundary condition, atomic types or number of atoms
        requires the complete reconstruction of the object.

        Raises
        ------
        ValueError
            on invalid input on the Python side of the API

        XTBException
            on errors returned from the API, usually from nuclear fusion check
        """

        if 3 * len(self) != positions.size:
            raise ValueError("Dimension missmatch for positions")
        _positions = np.array(positions, dtype="float")

        if lattice is not None:
            if lattice.size != 9:
                raise ValueError("Invalid lattice provided")
            _lattice = np.array(lattice, dtype="float")
        else:
            _lattice = None

        _lib.xtb_updateMolecule(
            self._env,
            self._mol,
            _cast("double*", _positions),
            _cast("double*", _lattice),
        )

        if self.check() != 0:
            raise XTBException(self.get_error())


class Results(Environment):
    """Calculation results

    Holds ``xtb`` API object containing results from a single point calculation.
    It can be queried for indiviual properties or used to restart calculations.
    Note that results from different methods are generally incompatible, the
    API tries to be as clever as possible about this and will usually
    automatically reallocate missmatched results objects as necessary.

    The results objects is connected to its own, independent environment,
    giving it its own error stack and IO infrastructure.

    Example
    -------
    >>> from xtb.interface import Calculator, Param, VERBOSITY_MINIMAL
    >>> import numpy as np
    >>> numbers = np.array([8, 1, 1])
    >>> positions = np.array([
    ... [ 0.00000000000000, 0.00000000000000,-0.73578586109551],
    ... [ 1.44183152868459, 0.00000000000000, 0.36789293054775],
    ... [-1.44183152868459, 0.00000000000000, 0.36789293054775]])
    ...
    >>> calc = Calculator(Param.GFN2xTB, numbers, positions)
    >>> calc.set_verbosity(VERBOSITY_MINIMAL)
    >>> res = calc.singlepoint()  # energy printed is only the electronic part
       1     -5.1027888 -0.510279E+01  0.421E+00   14.83       0.0  T
       2     -5.1040645 -0.127572E-02  0.242E+00   14.55       1.0  T
       3     -5.1042978 -0.233350E-03  0.381E-01   14.33       1.0  T
       4     -5.1043581 -0.602769E-04  0.885E-02   14.48       1.0  T
       5     -5.1043609 -0.280751E-05  0.566E-02   14.43       1.0  T
       6     -5.1043628 -0.188160E-05  0.131E-03   14.45      44.1  T
       7     -5.1043628 -0.455326E-09  0.978E-04   14.45      59.1  T
       8     -5.1043628 -0.572169E-09  0.192E-05   14.45    3009.1  T
         SCC iter.                  ...        0 min,  0.022 sec
         gradient                   ...        0 min,  0.000 sec
    >>> res.get_energy()
    -5.070451354836705
    >>> res.get_gradient()
    [[ 6.24500451e-17 -3.47909735e-17 -5.07156941e-03]
     [-1.24839222e-03  2.43536791e-17  2.53578470e-03]
     [ 1.24839222e-03  1.04372944e-17  2.53578470e-03]]
    >>> res = calc.singlepoint(res)
       1     -5.1043628 -0.510436E+01  0.898E-08   14.45       0.0  T
       2     -5.1043628 -0.266454E-14  0.436E-08   14.45  100000.0  T
       3     -5.1043628  0.177636E-14  0.137E-08   14.45  100000.0  T
         SCC iter.                  ...        0 min,  0.001 sec
         gradient                   ...        0 min,  0.000 sec
    >>> res.get_charges()
    [-0.56317912  0.28158956  0.28158956]

    Raises
    ------
    XTBException
        in case the requested property is not present in the results object
    """

    _res = _ffi.NULL

    def __init__(self, mol: Molecule):
        """Create new singlepoint results object"""
        Environment.__init__(self)
        self._res = _new_results()
        self._natoms = len(mol)

    def __len__(self):
        return self._natoms

    def get_energy(self):
        """Query singlepoint results object for energy in Hartree

        Example
        -------
        >>> res.get_energy()
        -5.070451354836705
        """
        _energy = _ffi.new("double *")
        _lib.xtb_getEnergy(self._env, self._res, _energy)
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _energy[0]

    def get_gradient(self):
        """Query singlepoint results object for gradient in Hartree/Bohr

        Example
        -------
        >>> res.get_gradient()
        [[ 6.24500451e-17 -3.47909735e-17 -5.07156941e-03]
         [-1.24839222e-03  2.43536791e-17  2.53578470e-03]
         [ 1.24839222e-03  1.04372944e-17  2.53578470e-03]]
        """
        _gradient = np.zeros((len(self), 3))
        _lib.xtb_getGradient(self._env, self._res, _cast("double*", _gradient))
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _gradient

    def get_virial(self):
        """Query singlepoint results object for virial given in Hartree

        Example
        -------
        >>> res.get_virial()
        [[ 1.43012837e-02  3.43893209e-17 -1.86809511e-16]
         [ 0.00000000e+00  0.00000000e+00  0.00000000e+00]
         [ 1.02348685e-16  1.46994821e-17  3.82414977e-02]]
        """
        _virial = np.zeros((3, 3))
        _lib.xtb_getVirial(self._env, self._res, _cast("double*", _virial))
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _virial

    def get_dipole(self):
        """Query singlepoint results object for dipole in e·Bohr

        Example
        -------
        >>> get_dipole()
        [-4.44089210e-16  1.44419023e-16  8.89047667e-01]
        """
        _dipole = np.zeros(3)
        _lib.xtb_getDipole(self._env, self._res, _cast("double*", _dipole))
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _dipole

    def get_charges(self):
        """Query singlepoint results object for partial charges in e

        Example
        -------
        >>> get_charges()
        [-0.56317913  0.28158957  0.28158957]
        """
        _charges = np.zeros(len(self))
        _lib.xtb_getCharges(self._env, self._res, _cast("double*", _charges))
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _charges

    def get_bond_orders(self):
        """Query singlepoint results object for bond orders

        Example
        -------
        >>> res.get_bond_orders()
        [[0.00000000e+00 9.20433501e-01 9.20433501e-01]
         [9.20433501e-01 0.00000000e+00 2.74039053e-04]
         [9.20433501e-01 2.74039053e-04 0.00000000e+00]]
        """
        _bond_orders = np.zeros((len(self), len(self)))
        _lib.xtb_getBondOrders(self._env, self._res, _cast("double*", _bond_orders))
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _bond_orders


class Calculator(Molecule):
    """Singlepoint calculator

    Examples
    --------
    >>> from xtb.interface import Calculator, Param, VERBOSITY_MINIMAL
    >>> import numpy as np
    >>> numbers = np.array([8, 1, 1])
    >>> positions = np.array([
    ... [ 0.00000000000000, 0.00000000000000,-0.73578586109551],
    ... [ 1.44183152868459, 0.00000000000000, 0.36789293054775],
    ... [-1.44183152868459, 0.00000000000000, 0.36789293054775]])
    ...
    >>> calc = Calculator(Param.GFN2xTB, numbers, positions)
    >>> calc.set_verbosity(VERBOSITY_MINIMAL)
    >>> res = calc.singlepoint()  # energy printed is only the electronic part
       1     -5.1027888 -0.510279E+01  0.421E+00   14.83       0.0  T
       2     -5.1040645 -0.127572E-02  0.242E+00   14.55       1.0  T
       3     -5.1042978 -0.233350E-03  0.381E-01   14.33       1.0  T
       4     -5.1043581 -0.602769E-04  0.885E-02   14.48       1.0  T
       5     -5.1043609 -0.280751E-05  0.566E-02   14.43       1.0  T
       6     -5.1043628 -0.188160E-05  0.131E-03   14.45      44.1  T
       7     -5.1043628 -0.455326E-09  0.978E-04   14.45      59.1  T
       8     -5.1043628 -0.572169E-09  0.192E-05   14.45    3009.1  T
         SCC iter.                  ...        0 min,  0.022 sec
         gradient                   ...        0 min,  0.000 sec
    >>> res.get_energy()
    -5.070451354836705
    >>> res.get_gradient()
    [[ 6.24500451e-17 -3.47909735e-17 -5.07156941e-03]
     [-1.24839222e-03  2.43536791e-17  2.53578470e-03]
     [ 1.24839222e-03  1.04372944e-17  2.53578470e-03]]

    Raises
    ------
    XTBException
        on errors encountered in API or while performing calculations
    """

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
        self._calc = _new_calculator()
        self._load(param)

    def _load(self, param: Param):
        """Load parametrisation data into calculator"""

        self._loader[param](
            self._env, self._mol, self._calc, _ffi.NULL,
        )

        if self.check() != 0:
            raise XTBException(self.get_error())

    def singlepoint(self, res: Optional[Results] = None) -> Results:
        """Perform singlepoint calculation,
        note that the a previous result is overwritten by this action"""

        _res = Results(self) if res is None else res
        _lib.xtb_singlepoint(
            self._env, self._mol, self._calc, _res._res,
        )

        if self.check() != 0:
            raise XTBException(self.get_error())

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
