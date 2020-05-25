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
"""Integration with the QCArchive infrastructure"""

from tempfile import NamedTemporaryFile
from .. import __version__
from ..interface import (
    Calculator,
    Param,
    XTBException,
    get_api_version,
    VERBOSITY_FULL,
)
import qcelemental as qcel


_methods = {
    "GFN2-xTB": Param.GFN2xTB,
    "GFN1-xTB": Param.GFN1xTB,
    "GFN0-xTB": Param.GFN0xTB,
    "GFN-FF": Param.GFNFF,
}


def run_qcschema(input_data: qcel.models.AtomicInput) -> qcel.models.AtomicResult:
    """Perform a calculation based on a QCElemental input"""

    ret_data = input_data.dict()

    provenance = {
        "creator": "xtb",
        "version": get_api_version(),
        "routine": "xtb.qcschema.run_qcschema",
    }

    fd = NamedTemporaryFile()
    success = True
    try:
        calc = Calculator(
            _methods.get(input_data.model.method, Param.GFN2xTB),
            input_data.molecule.atomic_numbers,
            input_data.molecule.geometry,
            input_data.molecule.molecular_charge,
            input_data.molecule.molecular_multiplicity - 1,
        )

        # We want the full printout from xtb
        calc.set_verbosity(VERBOSITY_FULL)
        calc.set_output(fd.name)

        # Perform actual calculation
        res = calc.singlepoint()

        calc.release_output()

        properties = {
            "return_energy": res.get_energy(),
            "scf_dipole_moment": res.get_dipole(),
        }
        extras = dict(
            xtb={
                "return_gradient": res.get_gradient(),
                "mulliken_charges": res.get_charges(),
                "mayer_indices": res.get_bond_orders(),
            }
        )

        if input_data.driver == "energy":
            return_result = properties["return_energy"]
        elif input_data.driver == "gradient":
            return_result = extras["xtb"]["return_gradient"]
        elif input_data.driver == "properties":
            return_result = {
                "mulliken_charges": extras["xtb"]["mulliken_charges"],
                "mayer_indices": extras["xtb"]["mayer_indices"],
            }
        else:
            return_result = 0.0
            success = False

        ret_data.update(
            properties=properties, extras=extras, return_result=return_result,
        )

    except XTBException as ee:
        success = False

        ret_data.update(
            error=qcel.models.ComputeError(
                error_type="runtime_error", error_message=str(ee),
            ),
            return_result=0.0,
            properties={},
        )

    output = fd.read().decode()
    fd.close()

    ret_data.update(
        provenance=provenance, success=success,
    )

    return qcel.models.AtomicResult(**ret_data, stdout=output)
