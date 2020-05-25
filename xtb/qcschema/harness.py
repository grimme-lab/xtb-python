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

from .. import __version__
from ..interface import Calculator, Param, XTBException, VERBOSITY_MUTED
import qcelemental as qcel


_methods = {
    "GFN2-xTB": Param.GFN2xTB,
    "GFN1-xTB": Param.GFN1xTB,
    "GFN0-xTB": Param.GFN0xTB,
    "GFN-FF": Param.GFNFF,
}


def run_qcschema(input_data: qcel.models.AtomicInput) -> qcel.models.AtomicResult:
    """Perform a calculation based on a QCElemental input"""

    success = True
    try:
        calc = Calculator(
            _methods.get(input_data.model.method, "GFN2-xTB"),
            input_data.molecule.atomic_numbers,
            input_data.molecule.geometry,
            input_data.molecule.molecular_charge,
            input_data.molecule.molecular_multiplicity - 1,
        )
        calc.set_verbosity(VERBOSITY_MUTED)

        res = calc.singlepoint()

        properties = {
            "return_energy": res.get_energy(),
            "scf_dipole_moment": res.get_dipole(),
        }
        extras = {
            "return_gradient": res.get_gradient(),
        }

        if input_data.driver == "energy":
            return_result = properties["return_energy"]
        elif input_data.driver == "gradient":
            return_result = extras["return_gradient"]
        else:
            return_result = None
            success = False

    except XTBException:
        success = False

    provenance = {
        "creator": "xtb",
        "version": __version__,
        "routine": "xtb.qcschema.run_qcschema",
    }

    ret_data = input_data.dict()
    ret_data.update(
        success=success,
        provenance=provenance,
        properties=properties,
        extras=extras,
        return_result=return_result,
    )

    return qcel.models.AtomicResult(**ret_data)
