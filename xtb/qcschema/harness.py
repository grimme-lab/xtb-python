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
"""Integration with the `QCArchive infrastructure <http://docs.qcarchive.molssi.org>`_.

This module provides a way to translate QCSchema or QCElemental Atomic Input
into a format understandable by the ``xtb`` API which in turn provides the
calculation results in a QCSchema compatible format.

The ``xtb`` model supports any method accepted by ``xtb.utils.get_method``.

Supported keywords are

======================== =========== ============================================
 Keyword                  Default     Description
======================== =========== ============================================
 accuracy                 1.0         Numerical accuracy of the calculation
 electronic_temperature   300.0       Electronic temperatur for TB methods
 max_iterations           250         Iterations for self-consistent evaluation
 solvent                  "none"      GBSA implicit solvent model
======================== =========== ============================================
"""

from typing import Union
from tempfile import NamedTemporaryFile
from ..libxtb import VERBOSITY_MUTED, get_api_version
from ..interface import Calculator, XTBException
from ..utils import get_method, get_solvent
import qcelemental as qcel


_keywords = [
    "accuracy",
    "electronic_temperature",
    "max_iterations",
    "solvent",
    "verbosity"
]


def run_qcschema(
    input_data: Union[dict, qcel.models.AtomicInput]
) -> qcel.models.AtomicResult:
    """Perform a calculation based on an atomic input model.

    Example
    -------
    >>> from xtb.qcschema.harness import run_qcschema
    >>> import qcelemental as qcel
    >>> atomic_input = qcel.models.AtomicInput(
    ...     molecule = qcel.models.Molecule(
    ...         symbols = ["O", "H", "H"],
    ...         geometry = [
    ...             0.00000000000000,  0.00000000000000, -0.73578586109551,
    ...             1.44183152868459,  0.00000000000000,  0.36789293054775,
    ...            -1.44183152868459,  0.00000000000000,  0.36789293054775
    ...         ],
    ...     ),
    ...     driver = "energy",
    ...     model = {
    ...         "method": "GFN2-xTB",
    ...     },
    ...     keywords = {
    ...         "accuracy": 1.0,
    ...         "max_iterations": 50,
    ...     },
    ... )
    ...
    >>> atomic_result = run_qcschema(atomic_input)
    >>> atomic_result.return_result
    -5.070451354848316
    """

    if not isinstance(input_data, qcel.models.AtomicInput):
        atomic_input = qcel.models.AtomicInput(**input_data)
    else:
        atomic_input = input_data
    ret_data = atomic_input.dict()

    provenance = {
        "creator": "xtb",
        "version": get_api_version(),
        "routine": "xtb.qcschema.run_qcschema",
    }

    _method = get_method(atomic_input.model.method)
    if _method is None:
        ret_data.update(
            success=False,
            return_result=0.0,
            provenance=provenance,
            properties={},
            error=qcel.models.ComputeError(
                error_type="input_error",
                error_message="Invalid method {} provided in model".format(
                    atomic_input.model.method
                ),
            ),
        )

        return qcel.models.AtomicResult(**ret_data)

    verbosity = atomic_input.keywords.get("verbosity", "full")
    fd = None
    output = None
    success = True
    try:
        calc = Calculator(
            _method,
            atomic_input.molecule.atomic_numbers,
            atomic_input.molecule.geometry,
            atomic_input.molecule.molecular_charge,
            atomic_input.molecule.molecular_multiplicity - 1,
        )

        if "solvent" in atomic_input.keywords:
            calc.set_solvent(get_solvent(atomic_input.keywords["solvent"]))

        if "accuracy" in atomic_input.keywords:
            calc.set_accuracy(atomic_input.keywords["accuracy"])

        if "max_iterations" in atomic_input.keywords:
            calc.set_max_iterations(atomic_input.keywords["max_iterations"])

        if "electronic_temperature" in atomic_input.keywords:
            calc.set_electronic_temperature(
                atomic_input.keywords["electronic_temperature"]
            )

        # Work out how verbose the printing from xtb should be
        verbosity = calc.set_verbosity(verbosity)
        if verbosity > VERBOSITY_MUTED:
            fd = NamedTemporaryFile()
            calc.set_output(fd.name)

        # Perform actual calculation
        res = calc.singlepoint()

        calc.release_output()

        # Check if the calculation has generated a wavefunction
        _wfn = res.get_number_of_orbitals() > 0

        # First we access properties that should be always available
        properties = {
            "return_energy": res.get_energy(),
            "scf_dipole_moment": res.get_dipole(),
        }
        extras = {"xtb": {"return_gradient": res.get_gradient()}}
        # Charges, bond order and so on are stored in the wavefunction
        if _wfn:
            extras["xtb"]["mulliken_charges"] = res.get_charges()
            extras["xtb"]["mayer_indices"] = res.get_bond_orders()

        if atomic_input.driver == "energy":
            return_result = properties["return_energy"]
        elif atomic_input.driver == "gradient":
            return_result = extras["xtb"]["return_gradient"]
        elif atomic_input.driver == "properties":
            return_result = {
                "dipole": properties["scf_dipole_moment"],
            }
            if _wfn:
                return_result["mulliken_charges"] = extras["xtb"]["mulliken_charges"]
                return_result["mayer_indices"] = extras["xtb"]["mayer_indices"]
        else:
            return_result = 0.0
            success = False

            ret_data.update(
                error=qcel.models.ComputeError(
                    error_type="input_error",
                    error_message="Calculation succeeded but invalid driver request provided",
                ),
            )

        ret_data['extras'].update(extras)

    except XTBException as ee:
        success = False

        ret_data.update(
            error=qcel.models.ComputeError(
                error_type="runtime_error", error_message=str(ee),
            ),
        )
        return_result = 0.0
        properties = {}

    if fd is not None:
        output = fd.read().decode()
        fd.close()

    ret_data.update(
        provenance=provenance,
        success=success,
        properties=properties,
        return_result=return_result,
    )

    return qcel.models.AtomicResult(**ret_data, stdout=output)
