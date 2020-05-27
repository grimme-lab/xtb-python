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

from typing import List, Optional, Union
from enum import Enum, auto
import numpy as np


from .libxtb import (
    ffi as _ffi,
    lib as _lib,
    new_environment,
    new_molecule,
    new_calculator,
    new_results,
    copy_results,
)


class XTBException(Exception):
    """Thrown if an error in the C-API is encountered"""

    pass


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


class Solvent(Enum):
    """Possible solvents for the GBSA model"""

    acetone = auto()
    acetonitrile = auto()
    benzene = auto()
    ch2cl2 = auto()
    chcl3 = auto()
    cs2 = auto()
    dmf = auto()
    dmso = auto()
    ether = auto()
    h2o = auto()
    methanol = auto()
    nhexane = auto()
    thf = auto()
    toluene = auto()


_solvents = {
    Solvent.acetone: "acetone",
    Solvent.acetonitrile: "acetonitrile",
    Solvent.benzene: "benzene",
    Solvent.ch2cl2: "ch2cl2",
    Solvent.chcl3: "chcl3",
    Solvent.cs2: "cs2",
    Solvent.dmf: "dmf",
    Solvent.dmso: "dmso",
    Solvent.ether: "ether",
    Solvent.h2o: "h2o",
    Solvent.methanol: "methanol",
    Solvent.nhexane: "nhexane",
    Solvent.thf: "thf",
    Solvent.toluene: "toluene",
}


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
    >>> from xtb.libxtb import VERBOSITY_FULL
    >>> from xtb.interface import Environment
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
        self._env = new_environment()

    def check(self) -> int:
        """Check current status of calculation environment

        Example
        -------
        >>> if env.check() != 0:
        ...     raise XTBException("Error occured in the API")
        """
        return _lib.xtb_checkEnvironment(self._env)

    def get_error(self, message: Optional[str] = None) -> str:
        """Check for error messages

        Example
        -------
        >>> if env.check() != 0:
        ...     raise XTBException(env.get_error())
        """
        _message = _ffi.new("char[]", 512)
        _lib.xtb_getError(self._env, _message, _ref("int", 512))
        if message is not None:
            return "{}:\n{}".format(message, _ffi.string(_message).decode())
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
    >>> mol.update(np.zeros((len(mol), 3)))  # will fail nuclear fusion check
    xtb.interface.XTBException: Update of molecular structure failed:
    -1- xtb_api_updateMolecule: Could not update molecular structure
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

        self._mol = new_molecule(
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
            raise XTBException(self.get_error("Setup of molecular structure failed"))

    def __len__(self):
        return self._natoms

    def update(
        self, positions: np.ndarray, lattice: Optional[np.ndarray] = None,
    ) -> None:
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
            raise XTBException(self.get_error("Update of molecular structure failed"))


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
    >>> from xtb.libxtb import VERBOSITY_MINIMAL
    >>> from xtb.interface import Calculator, Param
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

    def __init__(self, res: Union[Molecule, "Results"]):
        """Create new singlepoint results object"""
        Environment.__init__(self)
        if isinstance(res, Results):
            self._res = copy_results(res._res)
        else:
            self._res = new_results()
        self._natoms = len(res)

    def __len__(self):
        return self._natoms

    def get_energy(self) -> float:
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

    def get_gradient(self) -> np.ndarray:
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

    def get_virial(self) -> np.ndarray:
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

    def get_dipole(self) -> np.ndarray:
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

    def get_charges(self) -> np.ndarray:
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

    def get_bond_orders(self) -> np.ndarray:
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

    def get_number_of_orbitals(self) -> int:
        """Query singlepoint results object for the number of basis functions

        Example
        -------
        >>> res.get_number_of_orbitals()
        6
        """
        _nao = _ffi.new("int *")
        _lib.xtb_getNao(self._env, self._res, _nao)
        return _nao[0]

    def get_orbital_eigenvalues(self) -> np.ndarray:
        """Query singlepoint results object for orbital energies in Hartree"""
        _nao = self.get_number_of_orbitals()
        _eigenvalues = np.zeros(_nao)
        _lib.xtb_getOrbitalEigenvalues(
            self._env, self._res, _cast("double*", _eigenvalues)
        )
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _eigenvalues

    def get_orbital_occupations(self) -> np.ndarray:
        """Query singlepoint results object for occupation numbers"""
        _nao = self.get_number_of_orbitals()
        _occupations = np.zeros(_nao)
        _lib.xtb_getOrbitalOccupations(
            self._env, self._res, _cast("double*", _occupations)
        )
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _occupations

    def get_orbital_coefficients(self) -> np.ndarray:
        """Query singlepoint results object for orbital coefficients"""
        _nao = self.get_number_of_orbitals()
        _coefficients = np.zeros((_nao, _nao), order="F")
        _lib.xtb_getOrbitalCoefficients(
            self._env, self._res, _cast("double*", _coefficients)
        )
        if self.check() != 0:
            raise XTBException(self.get_error())
        return _coefficients


class Calculator(Molecule):
    """Singlepoint calculator

    Examples
    --------
    >>> from xtb.libxtb import VERBOSITY_MINIMAL
    >>> from xtb.interface import Calculator, Param
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
        self._calc = new_calculator()
        self._load(param)

    def _load(self, param: Param):
        """Load parametrisation data into calculator"""

        self._loader[param](
            self._env, self._mol, self._calc, _ffi.NULL,
        )

        if self.check() != 0:
            raise XTBException(self.get_error("Could not load parametrisation data"))

    def set_solvent(self, solvent: Optional[Solvent] = None) -> None:
        """Add/Remove a solvation model to/from calculator"""
        if solvent is not None:
            _solvent = _ffi.new("char[]", _solvents.get(solvent, "none").encode())
            _lib.xtb_setSolvent(
                self._env, self._calc, _solvent, _ffi.NULL, _ffi.NULL, _ffi.NULL
            )
        else:
            _lib.xtb_releaseSolvent(self._env, self._calc)
        if self.check() != 0:
            raise XTBException(self.get_error("Failed to set solvent model"))

    def set_accuracy(self, accuracy: float) -> None:
        """Set numerical accuracy for calculation"""

        _lib.xtb_setAccuracy(self._env, self._calc, accuracy)

        if self.check() != 0:
            raise XTBException(self.get_error())

    def set_max_iterations(self, maxiter: int) -> None:
        """Set maximum number of iterations for self-consistent charge methods"""

        _lib.xtb_setMaxIter(self._env, self._calc, maxiter)

        if self.check() != 0:
            raise XTBException(self.get_error())

    def set_electronic_temperature(self, etemp: int) -> None:
        """Set electronic temperature for tight binding Hamiltonians"""

        _lib.xtb_setElectronicTemp(self._env, self._calc, etemp)

        if self.check() != 0:
            raise XTBException(self.get_error())

    def singlepoint(self, res: Optional[Results] = None, copy: bool = False) -> Results:
        """Perform singlepoint calculation,
        note that the a previous result is overwritten by this action"""

        if res is not None:
            if copy:
                _res = Results(res)
            else:
                _res = res
        else:
            _res = Results(self)

        _lib.xtb_singlepoint(
            self._env, self._mol, self._calc, _res._res,
        )

        if self.check() != 0:
            raise XTBException(self.get_error("Single point calculation failed"))

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
