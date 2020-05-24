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

from xtb.interface import Param
from xtb.ase.calculator import XTB
from ase.atoms import Atoms
from pytest import approx
import numpy as np

def test_gfn2_xtb_0d():
    """Test ASE interface to GFN2-xTB"""
    thr = 1.0e-6

    atoms = Atoms(
        symbols = 'CHOCH2CH4CH2OH',
        positions = np.array([
            [ 2.98271538225471,  0.27909365256588,  0.64970485202128],
            [ 2.63569552384225,  0.02450596849126,  2.67121292650984],
            [ 2.56989337016904, -2.05262619471878, -0.67988944754186],
            [ 1.23558798335661,  2.29620433434321, -0.41823796718252],
            [ 1.99900332597202,  4.12013776218631,  0.17749063730515],
            [ 1.37891993108372,  2.23906846471541, -2.47825866025928],
            [-1.54453741909595,  2.17720450030314,  0.39335783291694],
            [-2.46330525736976,  3.90367908229492, -0.27557498250645],
            [-1.67007381582968,  2.19163255932772,  2.45524557541300],
            [ 3.74944341478106, -3.27762793227897, -0.04041179335176],
            [ 4.94406402530285,  0.86728602923560,  0.39031159439073],
            [-3.07595446965128, -0.06434895427702, -0.58827363489343],
            [-5.07245768794950,  0.28537699195773, -0.22405726867172],
            [-2.83811920774470, -0.22326358369591, -2.64090360906448],
            [-2.50249250818741, -2.38134594526037,  0.62999122900302],
            [-0.78924600912582, -2.78793942001205,  0.14482294164596],
        ]),
    )
    forces = np.array([
        [-0.28561161, -0.48592025, -0.28392329],
        [-0.05526157, -0.07403454,  0.09665525],
        [ 0.18824961,  0.39170145,  0.33881942],
        [-0.01166074,  0.24653248, -0.16779604],
        [-0.05367508,  0.03368050,  0.05115418],
        [-0.09605263, -0.10000389,  0.01097300],
        [ 0.09423301,  0.18573613,  0.17797436],
        [ 0.02651902, -0.04073861, -0.03655976],
        [ 0.07886360, -0.05806479,  0.00649346],
        [-0.00780530, -0.07979378, -0.03175702],
        [ 0.13328582,  0.03209279, -0.04638513],
        [ 0.08197780, -0.39157298,  0.12107404],
        [-0.11453809, -0.01485091,  0.09974066],
        [ 0.09786016, -0.09130860, -0.05738661],
        [-0.26643389,  0.47603740, -0.27856717],
        [ 0.19004988, -0.02949239, -0.00050935],
    ])
    charges = np.array([
        0.08239823,  0.03066406, -0.44606929, -0.06139043,  0.03610596,
        0.05389499, -0.06991855,  0.03384415,  0.04665524,  0.28688538,
        0.02246569,  0.08251610,  0.03810481,  0.01883776, -0.46691965,
        0.31192554,
    ])

    calc = XTB(method=Param.GFN2xTB)
    atoms.set_calculator(calc)

    assert approx(atoms.get_potential_energy(), thr) == -592.6794366990786
    assert approx(atoms.get_forces(), thr) == forces
    assert approx(atoms.get_charges(), thr) == charges
