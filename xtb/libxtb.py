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
"""Thin wrapper around the CFFI extension. This module mainly acts as a guard
for importing the libxtb extension and also provides some FFI based wappers for
memory handling.

To check for API compatibility use the provided wrapper around the API version
getter.

Example
-------
>>> from xtb.libxtb import get_api_version
>>> get_api_version()
"1.0.0"
"""

try:
    from ._libxtb import ffi, lib
except ImportError:
    raise ImportError("xtb C extension unimportable, cannot use C-API")


VERBOSITY_FULL = 2
VERBOSITY_MINIMAL = 1
VERBOSITY_MUTED = 0


def get_api_version() -> str:
    """Return the current API version from xtb, for easy usage in C
    the API version is provided as

    10000 * major + 100 * minor + patch

    For Python we want something that looks like a semantic version again.
    """
    api_version = lib.xtb_getAPIVersion()
    return "{}.{}.{}".format(
        int(api_version / 10000),
        int(api_version % 10000 / 100),
        int(api_version % 100),
    )


def _delete_environment(env):
    """Delete a xtb calculation environment object"""
    ptr = ffi.new("xtb_TEnvironment *")
    ptr[0] = env
    lib.xtb_delEnvironment(ptr)


def new_environment():
    """Create new xtb calculation environment object"""
    return ffi.gc(lib.xtb_newEnvironment(), _delete_environment)


def _delete_molecule(mol):
    """Delete molecular structure data"""
    ptr = ffi.new("xtb_TMolecule *")
    ptr[0] = mol
    lib.xtb_delMolecule(ptr)


def new_molecule(env, natoms, numbers, positions, charge, uhf, lattice, periodic):
    """Create new molecular structure data"""
    return ffi.gc(
        lib.xtb_newMolecule(
            env, natoms, numbers, positions, charge, uhf, lattice, periodic,
        ),
        _delete_molecule,
    )


def _delete_results(res):
    """Delete singlepoint results object"""
    ptr = ffi.new("xtb_TResults *")
    ptr[0] = res
    lib.xtb_delResults(ptr)


def new_results():
    """Create new singlepoint results object"""
    return ffi.gc(lib.xtb_newResults(), _delete_results)


def copy_results(res):
    """Create new singlepoint results object from existing results"""
    return ffi.gc(lib.xtb_copyResults(res), _delete_results)


def _delete_calculator(calc):
    """Delete calculator object"""
    ptr = ffi.new("xtb_TCalculator *")
    ptr[0] = calc
    lib.xtb_delCalculator(ptr)


def new_calculator():
    """Create new calculator object"""
    return ffi.gc(lib.xtb_newCalculator(), _delete_calculator)
