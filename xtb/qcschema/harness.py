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

If the QCElemental package is installed the ``xtb.qcschema.harness`` module becomes
importable and provides the ``run_qcschema`` function supporting QCSchema v1.
If the QCElemental package is >=0.50.0, ``xtb.qcschema.harness`` supports QCSchema v1
and v2, returning whichever version was submitted. Note that Python 3.14+ only
works with QCSchema v2 due to Pydantic restrictions.

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

import sys
from typing import Any, Dict, overload, Union
from tempfile import NamedTemporaryFile
from ..libxtb import VERBOSITY_MUTED, get_api_version
from ..interface import Calculator, XTBException
from ..utils import get_method, get_solvent

if sys.version_info < (3, 14):
    try:
        import qcelemental.models.v1 as qcel_v1
    except ModuleNotFoundError:
        import qcelemental.models as qcel_v1
else:
    qcel_v1 = None

try:
    import qcelemental.models.v2 as qcel_v2
except ModuleNotFoundError:
    qcel_v2 = None


if qcel_v1 is None and qcel_v2 is None:
    raise ModuleNotFoundError(
        "The qcelemental package is required for qcschema support. "
        "Please install it with 'pip install qcelemental'."
    )

_keywords = [
    "accuracy",
    "electronic_temperature",
    "max_iterations",
    "solvent",
    "verbosity"
]


if qcel_v1 is not None:
    @overload
    def run_qcschema(
        input_data: Union[Dict[str, Any], "qcel_v1.AtomicInput"],
    ) -> Union["qcel_v1.AtomicResult", "qcel_v1.FailedOperation"]: ...

if qcel_v2 is not None:
    @overload
    def run_qcschema(
        input_data: Union[Dict[str, Any], "qcel_v2.AtomicInput"],
    ) -> Union["qcel_v2.AtomicResult", "qcel_v2.FailedOperation"]: ...


def run_qcschema(input_data):
    """Perform a calculation based on a v1 or v2 QCSchema atomic input model.

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

    if qcel_v2 is not None and isinstance(input_data, qcel_v2.AtomicInput):
        atomic_input = input_data
    elif qcel_v1 is not None and isinstance(input_data, qcel_v1.AtomicInput):
        atomic_input = input_data
    elif qcel_v2 is not None and input_data.get("specification"):
        atomic_input = qcel_v2.AtomicInput(**input_data)
    elif qcel_v1 is not None:
        atomic_input = qcel_v1.AtomicInput(**input_data)
    else:
        raise ValueError(
            "Input data is not a valid QCSchema AtomicInput for either v1 or v2."
        )

    schema_version = atomic_input.schema_version
    if schema_version == 1:
        ret_data = atomic_input.dict()
        input_keywords = atomic_input.keywords
        input_method = atomic_input.model.method
        input_driver = atomic_input.driver
    elif schema_version == 2:
        ret_data = {
            "input_data": atomic_input,
            "extras": {},
            "molecule": atomic_input.molecule,
        }
        input_keywords = atomic_input.specification.keywords
        input_method = atomic_input.specification.model.method
        input_driver = atomic_input.specification.driver
    else:
        raise ValueError(
            f"Unsupported QCSchema version: {schema_version}. Only v1 and v2 are supported."
        )

    provenance = {
        "creator": "xtb",
        "version": get_api_version(),
        "routine": "xtb.qcschema.run_qcschema",
    }

    _method = get_method(input_method)
    if _method is None:
        error = dict(
            error_type="input_error",
            error_message="Invalid method {} provided in model".format(
                input_method
            ),
        )
        if schema_version == 1:
            ret_data.update(
                success=False,
                return_result=0.0,
                provenance=provenance,
                properties={},
                error=error,
            )
            return qcel_v1.AtomicResult(**ret_data)
        elif schema_version == 2:
            return qcel_v2.FailedOperation(
                input_data=atomic_input, error=qcel_v2.ComputeError(**error)
            )

    verbosity = input_keywords.get("verbosity", "full")
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

        if "solvent" in input_keywords:
            calc.set_solvent(get_solvent(input_keywords["solvent"]))

        if "accuracy" in input_keywords:
            calc.set_accuracy(input_keywords["accuracy"])

        if "max_iterations" in input_keywords:
            calc.set_max_iterations(input_keywords["max_iterations"])

        if "electronic_temperature" in input_keywords:
            calc.set_electronic_temperature(
                input_keywords["electronic_temperature"]
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

        if input_driver == "energy":
            return_result = properties["return_energy"]
        elif input_driver == "gradient":
            return_result = extras["xtb"]["return_gradient"]
        elif input_driver == "properties":
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
                error=dict(
                    error_type="input_error",
                    error_message="Calculation succeeded but invalid driver request provided",
                ),
            )

        ret_data['extras'].update(extras)

    except XTBException as ee:
        success = False

        ret_data.update(
            error=dict(error_type="runtime_error", error_message=str(ee)),
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

    if schema_version == 1:
        return qcel_v1.AtomicResult(**ret_data)

    if "error" in ret_data:
        return qcel_v2.FailedOperation(
            input_data=atomic_input, error=ret_data["error"]
        )
    return qcel_v2.AtomicResult(**ret_data)
