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

from xtb.libxtb import VERBOSITY_MINIMAL
from xtb.interface import (
    XTBException,
    Molecule,
    Calculator,
    Results,
    Param,
    Solvent,
)
from pytest import approx, raises
import numpy as np


def test_molecule():
    """check if the molecular structure data is working as expected."""

    numbers = np.array(
        [6, 7, 6, 7, 6, 6, 6, 8, 7, 6, 8, 7, 6, 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    )
    positions = np.array(
        [
            [ 2.02799738646442, 0.09231312124713,-0.14310895950963],
            [ 4.75011007621000, 0.02373496014051,-0.14324124033844],
            [ 6.33434307654413, 2.07098865582721,-0.14235306905930],
            [ 8.72860718071825, 1.38002919517619,-0.14265542523943],
            [ 8.65318821103610,-1.19324866489847,-0.14231527453678],
            [ 6.23857175648671,-2.08353643730276,-0.14218299370797],
            [ 5.63266886875962,-4.69950321056008,-0.13940509630299],
            [ 3.44931709749015,-5.48092386085491,-0.14318454855466],
            [ 7.77508917214346,-6.24427872938674,-0.13107140408805],
            [10.30229550927022,-5.39739796609292,-0.13672168520430],
            [12.07410272485492,-6.91573621641911,-0.13666499342053],
            [10.70038521493902,-2.79078533715849,-0.14148379504141],
            [13.24597858727017,-1.76969072232377,-0.14218299370797],
            [ 7.40891694074004,-8.95905928176407,-0.11636933482904],
            [ 1.38702118184179, 2.05575746325296,-0.14178615122154],
            [ 1.34622199478497,-0.86356704498496, 1.55590600570783],
            [ 1.34624089204623,-0.86133716815647,-1.84340893849267],
            [ 5.65596919189118, 4.00172183859480,-0.14131371969009],
            [14.67430918222276,-3.26230980007732,-0.14344911021228],
            [13.50897177220290,-0.60815166181684, 1.54898960808727],
            [13.50780014200488,-0.60614855212345,-1.83214617078268],
            [ 5.41408424778406,-9.49239668625902,-0.11022772492007],
            [ 8.31919801555568,-9.74947502841788, 1.56539243085954],
            [ 8.31511620712388,-9.76854236502758,-1.79108242206824],
        ]
    )
    filename = "xtb-error.log"
    message = "Expecting nuclear fusion warning"

    # Constructor should raise an error for nuclear fusion input
    with raises(XTBException, match="Setup of molecular structure failed"):
        mol = Molecule(numbers, np.zeros((24, 3)))

    # The Python class should protect from garbage input like this
    with raises(ValueError, match="Dimension missmatch"):
        mol = Molecule(np.array([1, 1, 1]), positions)

    # Also check for sane coordinate input
    with raises(ValueError, match="Expected tripels"):
        mol = Molecule(numbers, np.random.rand(7))

    # Construct real molecule
    mol = Molecule(numbers, positions)

    # Try to update a structure with missmatched coordinates
    with raises(ValueError, match="Dimension missmatch for positions"):
        mol.update(np.random.rand(7))

    # Try to add a missmatched lattice
    with raises(ValueError, match="Invalid lattice provided"):
        mol.update(positions, np.random.rand(7))

    # Try to update a structure with nuclear fusion coordinates
    with raises(XTBException, match="Update of molecular structure failed"):
        mol.update(np.zeros((24, 3)))

    # Redirect API output to file
    mol.set_output(filename)

    # Flush the error from the environment log
    mol.show(message)

    # Reset to correct positions, Molecule object should still be intact
    mol.update(positions, np.zeros((3, 3)))


def test_gfn2_xtb_0d():
    """check if the GFN2-xTB interface is working correctly."""
    thr = 1.0e-8
    thr2 = 1.0e-6

    numbers = np.array(
        [6, 7, 6, 7, 6, 6, 6, 8, 7, 6, 8, 7, 6, 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    )
    positions = np.array(
        [
            [ 2.02799738646442, 0.09231312124713,-0.14310895950963],
            [ 4.75011007621000, 0.02373496014051,-0.14324124033844],
            [ 6.33434307654413, 2.07098865582721,-0.14235306905930],
            [ 8.72860718071825, 1.38002919517619,-0.14265542523943],
            [ 8.65318821103610,-1.19324866489847,-0.14231527453678],
            [ 6.23857175648671,-2.08353643730276,-0.14218299370797],
            [ 5.63266886875962,-4.69950321056008,-0.13940509630299],
            [ 3.44931709749015,-5.48092386085491,-0.14318454855466],
            [ 7.77508917214346,-6.24427872938674,-0.13107140408805],
            [10.30229550927022,-5.39739796609292,-0.13672168520430],
            [12.07410272485492,-6.91573621641911,-0.13666499342053],
            [10.70038521493902,-2.79078533715849,-0.14148379504141],
            [13.24597858727017,-1.76969072232377,-0.14218299370797],
            [ 7.40891694074004,-8.95905928176407,-0.11636933482904],
            [ 1.38702118184179, 2.05575746325296,-0.14178615122154],
            [ 1.34622199478497,-0.86356704498496, 1.55590600570783],
            [ 1.34624089204623,-0.86133716815647,-1.84340893849267],
            [ 5.65596919189118, 4.00172183859480,-0.14131371969009],
            [14.67430918222276,-3.26230980007732,-0.14344911021228],
            [13.50897177220290,-0.60815166181684, 1.54898960808727],
            [13.50780014200488,-0.60614855212345,-1.83214617078268],
            [ 5.41408424778406,-9.49239668625902,-0.11022772492007],
            [ 8.31919801555568,-9.74947502841788, 1.56539243085954],
            [ 8.31511620712388,-9.76854236502758,-1.79108242206824],
        ]
    )
    gradient = np.array(
        [
            [-4.48702270e-03,-7.11501681e-04, 4.42250727e-06],
            [ 5.63520998e-03,-2.63277841e-02,-5.47551032e-05],
            [ 4.94394513e-03, 1.91697172e-02, 5.20296937e-05],
            [ 4.14320227e-03, 3.78985927e-03,-3.26124506e-05],
            [-3.44924840e-02,-8.30763633e-03,-3.85476373e-05],
            [ 6.09858493e-03,-4.02776651e-03, 3.46142461e-05],
            [ 1.74698961e-02, 7.91501928e-03, 3.75246600e-05],
            [-1.44268345e-02, 7.07857171e-03,-1.12175048e-04],
            [-5.07088926e-04,-1.13149559e-02, 7.28999985e-05],
            [-1.55778036e-02, 1.26994854e-02,-2.82633017e-05],
            [ 2.84123935e-02,-2.38401320e-02,-3.96858051e-05],
            [ 2.52730535e-03, 1.36557434e-02,-1.07970323e-05],
            [-1.61957397e-03,-2.96924390e-03, 2.89329075e-06],
            [-6.51526117e-03, 7.90714240e-03,-5.83689564e-05],
            [-1.45365262e-03, 2.78387473e-03, 4.39889933e-06],
            [ 2.59676642e-03, 9.07269292e-04, 3.98184821e-03],
            [ 2.59860253e-03, 9.08300767e-04,-3.98462262e-03],
            [-3.77425616e-03, 8.36833530e-03, 2.89789639e-05],
            [ 7.86820850e-03, 2.13957196e-03, 7.31459251e-07],
            [ 9.32145702e-04,-1.65668033e-04, 3.24917573e-03],
            [ 9.57211265e-04,-1.41846051e-04,-3.25368821e-03],
            [-2.06937754e-03,-9.28913451e-03, 1.03587348e-04],
            [ 3.58598494e-04,-9.82977790e-05, 2.38378001e-03],
            [ 3.81284918e-04,-1.28923994e-04,-2.34336886e-03],
        ]
    )
    charges = np.array([
        -0.05445590, -0.00457526,  0.08391889, -0.27870751,  0.11914924,
        -0.02621044,  0.26115960, -0.44071824, -0.10804747,  0.30411699,
        -0.44083760, -0.07457706, -0.04790859, -0.03738239,  0.06457802,
         0.08293905,  0.08296802,  0.05698136,  0.09025556,  0.07152988,
         0.07159003,  0.08590674,  0.06906357,  0.06926350,
    ])

    calc = Calculator(Param.GFN2xTB, numbers, positions)
    calc.set_verbosity(VERBOSITY_MINIMAL)
    assert calc.check() == 0

    calc.set_accuracy(1.0)
    calc.set_max_iterations(50)
    calc.set_electronic_temperature(300.0)

    res = calc.singlepoint()

    assert approx(res.get_energy(), thr) == -42.14746312757416
    assert approx(res.get_gradient(), thr) == gradient
    assert approx(res.get_charges(), thr2) == charges


def test_gfn1_xtb_0d():
    """check if the GFN1-xTB interface is working correctly."""
    thr = 1.0e-8
    thr2 = 1.0e-6

    numbers = np.array(
        [6, 7, 6, 7, 6, 6, 6, 8, 7, 6, 8, 7, 6, 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    )
    positions = np.array(
        [
            [ 2.02799738646442, 0.09231312124713,-0.14310895950963],
            [ 4.75011007621000, 0.02373496014051,-0.14324124033844],
            [ 6.33434307654413, 2.07098865582721,-0.14235306905930],
            [ 8.72860718071825, 1.38002919517619,-0.14265542523943],
            [ 8.65318821103610,-1.19324866489847,-0.14231527453678],
            [ 6.23857175648671,-2.08353643730276,-0.14218299370797],
            [ 5.63266886875962,-4.69950321056008,-0.13940509630299],
            [ 3.44931709749015,-5.48092386085491,-0.14318454855466],
            [ 7.77508917214346,-6.24427872938674,-0.13107140408805],
            [10.30229550927022,-5.39739796609292,-0.13672168520430],
            [12.07410272485492,-6.91573621641911,-0.13666499342053],
            [10.70038521493902,-2.79078533715849,-0.14148379504141],
            [13.24597858727017,-1.76969072232377,-0.14218299370797],
            [ 7.40891694074004,-8.95905928176407,-0.11636933482904],
            [ 1.38702118184179, 2.05575746325296,-0.14178615122154],
            [ 1.34622199478497,-0.86356704498496, 1.55590600570783],
            [ 1.34624089204623,-0.86133716815647,-1.84340893849267],
            [ 5.65596919189118, 4.00172183859480,-0.14131371969009],
            [14.67430918222276,-3.26230980007732,-0.14344911021228],
            [13.50897177220290,-0.60815166181684, 1.54898960808727],
            [13.50780014200488,-0.60614855212345,-1.83214617078268],
            [ 5.41408424778406,-9.49239668625902,-0.11022772492007],
            [ 8.31919801555568,-9.74947502841788, 1.56539243085954],
            [ 8.31511620712388,-9.76854236502758,-1.79108242206824],
        ]
    )
    gradient = np.array(
        [
            [ 3.87497169e-03, 1.05883022e-03, 4.01012413e-06],
            [-6.82002304e-03,-2.54686427e-02,-4.74713878e-05],
            [ 1.06489319e-02, 8.83656933e-03, 4.79964506e-05],
            [ 3.19138203e-04, 7.42440606e-03,-2.84972366e-05],
            [-2.62085234e-02,-9.01316371e-03,-3.86695635e-05],
            [-1.75094079e-03, 3.66993588e-03, 3.41186057e-05],
            [ 1.94850127e-02, 4.74199522e-03, 4.04729092e-05],
            [-1.17234487e-02, 7.48238018e-03,-1.16123385e-04],
            [-1.22410371e-03,-1.91329992e-02, 1.24615909e-04],
            [-1.67669061e-02, 1.21039811e-02,-3.45753133e-05],
            [ 2.48445184e-02,-1.92875717e-02,-4.91970983e-05],
            [ 1.10842561e-02, 1.70041879e-02,-3.22098294e-06],
            [-6.45913430e-03,-4.28606740e-03,-4.08606798e-06],
            [-6.58997261e-03, 1.32209050e-02,-9.01648028e-05],
            [-1.32693744e-03, 2.12474694e-03, 4.09305030e-06],
            [ 1.72269615e-03, 1.17167501e-03, 2.68453033e-03],
            [ 1.72536326e-03, 1.17100604e-03,-2.68802212e-03],
            [-1.55002130e-03, 3.93152833e-03, 2.52250090e-05],
            [ 6.35716726e-03, 2.28982657e-03, 3.48062215e-06],
            [ 5.17423565e-04,-5.06087446e-04, 1.94245792e-03],
            [ 5.40636707e-04,-4.85737643e-04,-1.94565875e-03],
            [-1.26772106e-03,-7.65879097e-03, 8.49174054e-05],
            [ 2.77976049e-04,-1.82969944e-04, 1.40041971e-03],
            [ 2.89640303e-04,-2.09943109e-04,-1.35065134e-03],
        ]
    )
    dipole = np.array([-0.81941935,  1.60912848,  0.00564382])


    calc = Calculator(Param.GFN1xTB, numbers, positions)

    res = Results(calc)

    # check if we cannot retrieve properties from the unallocated result
    with raises(XTBException, match="Energy is not available"):
        res.get_energy()
    with raises(XTBException, match="Gradient is not available"):
        res.get_gradient()
    with raises(XTBException, match="Virial is not available"):
        res.get_virial()
    with raises(XTBException, match="Partial charges are not available"):
        res.get_charges()
    with raises(XTBException, match="Dipole moment is not available"):
        res.get_dipole()
    with raises(XTBException, match="Bond orders are not available"):
        res.get_bond_orders()

    assert res.get_number_of_orbitals() == 0

    with raises(XTBException, match="Orbital eigenvalues are not available"):
        res.get_orbital_eigenvalues()
    with raises(XTBException, match="Occupation numbers are not available"):
        res.get_orbital_occupations()
    with raises(XTBException, match="Orbital coefficients are not available"):
        res.get_orbital_coefficients()

    # Start calculation by restarting with result
    res = calc.singlepoint(res)

    assert approx(res.get_energy(), thr) == -44.509702418208896
    assert approx(res.get_gradient(), thr) == gradient
    assert approx(res.get_dipole(), thr2) == dipole


def test_gfn2_xtb_3d():
    """Test if GFN2-xTB correctly fails for periodic input"""

    numbers = np.array(
        [6, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7, 7]
    )
    positions = np.array([
        [ 9.77104501e-01,  1.24925555e-01,  8.22139769e+00],
        [ 8.37995371e-01,  8.23489051e+00,  3.74893761e+00],
        [ 4.62693404e+00, -2.45721089e+00,  8.22052352e+00],
        [ 4.62532610e+00,  1.41051267e+00,  5.97940016e+00],
        [ 9.71618351e-01,  1.17570237e-01,  3.75065164e+00],
        [-2.80917006e+00,  6.94865315e+00,  5.99166085e+00],
        [ 4.06610161e+00,  4.51252077e+00,  6.46827038e-01],
        [ 2.76223056e-01, -8.50055887e-01,  2.06420987e+00],
        [ 2.84806942e-01,  2.07039689e+00,  8.22836360e+00],
        [ 2.90284064e+00,  8.22939158e+00,  3.73820878e+00],
        [ 6.69188274e+00, -2.46191735e+00,  8.22593771e+00],
        [ 6.69035555e+00,  1.41863696e+00,  5.97712614e+00],
        [ 7.73011343e+00,  1.91963880e+00,  6.45533278e-01],
        [ 3.94842571e+00,  3.36121142e+00,  5.97668593e+00],
        [-3.49960564e+00,  5.97197638e+00,  7.67502785e+00],
        [ 2.79250975e-01,  2.06298102e+00,  3.73907675e+00],
        [-3.50586965e+00,  5.96534053e+00,  4.31491171e+00],
        [ 1.56432603e-01,  7.25773353e+00,  2.06229892e+00],
        [-4.98732693e-02,  6.88619344e+00,  5.98746725e+00],
        [-4.50657119e-03, -1.16906911e+00,  5.98934273e+00],
        [ 3.73678498e+00,  1.55157272e-01,  8.27155126e+00],
        [ 3.73119434e+00,  1.47879860e-01,  3.69345547e+00],
        ])
    lattice = np.array([
        [ 1.13437228e+01, -1.84405404e-03,  1.33836685e-05],
        [-3.78300868e+00,  1.06992286e+01, -1.04202175e-03],
        [-3.78025723e+00, -5.34955718e+00,  9.26593601e+00],
        ])
    periodic = np.array([True, True, True])

    # GFN2-xTB does not support periodic boundary conditions,
    # yet the constructor should not flag this error to keep the interface uniform
    calc = Calculator(
        Param.GFN2xTB, numbers, positions, lattice=lattice, periodic=periodic
    )

    res = Results(calc)

    with raises(XTBException, match="Single point calculation failed"):
        calc.singlepoint(res)


def test_gfn1_xtb_3d():
    """Test GFN1-xTB for periodic input"""
    thr = 1.0e-8
    thr2 = 1.0e-6

    numbers = np.array(
        [6, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7, 7]
    )
    positions = np.array([
        [ 9.77104501e-01,  1.24925555e-01,  8.22139769e+00],
        [ 8.37995371e-01,  8.23489051e+00,  3.74893761e+00],
        [ 4.62693404e+00, -2.45721089e+00,  8.22052352e+00],
        [ 4.62532610e+00,  1.41051267e+00,  5.97940016e+00],
        [ 9.71618351e-01,  1.17570237e-01,  3.75065164e+00],
        [-2.80917006e+00,  6.94865315e+00,  5.99166085e+00],
        [ 4.06610161e+00,  4.51252077e+00,  6.46827038e-01],
        [ 2.76223056e-01, -8.50055887e-01,  2.06420987e+00],
        [ 2.84806942e-01,  2.07039689e+00,  8.22836360e+00],
        [ 2.90284064e+00,  8.22939158e+00,  3.73820878e+00],
        [ 6.69188274e+00, -2.46191735e+00,  8.22593771e+00],
        [ 6.69035555e+00,  1.41863696e+00,  5.97712614e+00],
        [ 7.73011343e+00,  1.91963880e+00,  6.45533278e-01],
        [ 3.94842571e+00,  3.36121142e+00,  5.97668593e+00],
        [-3.49960564e+00,  5.97197638e+00,  7.67502785e+00],
        [ 2.79250975e-01,  2.06298102e+00,  3.73907675e+00],
        [-3.50586965e+00,  5.96534053e+00,  4.31491171e+00],
        [ 1.56432603e-01,  7.25773353e+00,  2.06229892e+00],
        [-4.98732693e-02,  6.88619344e+00,  5.98746725e+00],
        [-4.50657119e-03, -1.16906911e+00,  5.98934273e+00],
        [ 3.73678498e+00,  1.55157272e-01,  8.27155126e+00],
        [ 3.73119434e+00,  1.47879860e-01,  3.69345547e+00],
        ])
    lattice = np.array([
        [ 1.13437228e+01, -1.84405404e-03,  1.33836685e-05],
        [-3.78300868e+00,  1.06992286e+01, -1.04202175e-03],
        [-3.78025723e+00, -5.34955718e+00,  9.26593601e+00],
    ])
    periodic = np.array([True, True, True])
    gradient = np.array([
        [ 5.46952312e-03, -3.12525543e-03, -6.52896786e-03],
        [-5.71285287e-03,  4.38725269e-03,  6.32349907e-03],
        [-5.02173630e-03,  4.34885633e-03, -7.00803496e-03],
        [-4.87551596e-03, -7.09454257e-03,  3.77244368e-04],
        [ 5.02630829e-03, -3.79620239e-03,  6.30421751e-03],
        [ 4.91374216e-03,  8.09631816e-03, -3.68676539e-04],
        [-7.28717739e-05,  1.30568980e-03, -6.38908884e-04],
        [ 9.79695284e-05,  1.46129903e-03,  1.04762274e-03],
        [ 7.73360338e-05, -1.75682759e-03,  7.51987006e-04],
        [-1.23628606e-03, -4.69633640e-04, -7.39566395e-04],
        [-1.91940111e-03, -4.73100704e-04,  6.08278469e-04],
        [-1.77181502e-03,  7.83050332e-04, -4.59767804e-06],
        [ 1.17661172e-03,  2.89377463e-04, -9.14361241e-04],
        [ 1.34273926e-03, -1.27328012e-03, -1.21190000e-04],
        [ 7.78894324e-05, -2.90779544e-05, -1.64479354e-03],
        [ 2.01000804e-04, -1.68099958e-03, -7.42723431e-04],
        [-6.00020414e-05,  2.71877066e-05,  1.56139664e-03],
        [ 1.25834445e-03,  4.52585494e-04,  7.01094853e-04],
        [-1.59037639e-03,  6.66092068e-03,  1.53044955e-03],
        [ 6.42180919e-03, -6.01295157e-04, -1.95941235e-04],
        [-1.85390467e-03, -4.18967639e-03, -5.23581022e-03],
        [-1.94851179e-03, -3.32264614e-03,  4.93778178e-03],
    ])
    charges = np.array([
        0.06182382,  0.06099432,  0.03885390,  0.06788916,  0.06428087,
        0.05876764,  0.03243010,  0.02574899,  0.02339485,  0.03323515,
        0.02257734,  0.02147826,  0.03444456,  0.02614362,  0.03103734,
        0.02593346,  0.03068062,  0.03220337, -0.16214463, -0.17714762,
       -0.17554024, -0.17708487,
    ])


    calc = Calculator(
        Param.GFN1xTB, numbers, positions, lattice=lattice, periodic=periodic
    )

    res = Results(calc)

    # Start calculation by restarting with result, since we are working with
    # a pointer under the hood, we don't have to catch the return value to
    # access the results
    calc.singlepoint(res)

    assert approx(res.get_energy(), thr) == -31.906084801853034
    assert approx(res.get_gradient(), thr) == gradient
    assert approx(res.get_charges(), thr2) == charges


def test_gfn1xtb_solvation():
    """Use GFN1-xTB/GBSA for a mindless molecule"""
    thr = 1.0e-7

    numbers = np.array([
        1, 1, 6, 5, 1, 15, 8, 17, 13, 15, 5, 1, 9, 15, 1, 15,
    ])
    positions = np.array([
        [ 2.79274810283778,  3.82998228828316, -2.79287054959216],
        [-1.43447454186833,  0.43418729987882,  5.53854345129809],
        [-3.26268343665218, -2.50644032426151, -1.56631149351046],
        [ 2.14548759959147, -0.88798018953965, -2.24592534506187],
        [-4.30233097423181, -3.93631518670031, -0.48930754109119],
        [ 0.06107643564880, -3.82467931731366, -2.22333344469482],
        [ 0.41168550401858,  0.58105573172764,  5.56854609916143],
        [ 4.41363836635653,  3.92515871809283,  2.57961724984000],
        [ 1.33707758998700,  1.40194471661647,  1.97530004949523],
        [ 3.08342709834868,  1.72520024666801, -4.42666116106828],
        [-3.02346932078505,  0.04438199934191, -0.27636197425010],
        [ 1.11508390868455, -0.97617412809198,  6.25462847718180],
        [ 0.61938955433011,  2.17903547389232, -6.21279842416963],
        [-2.67491681346835,  3.00175899761859,  1.05038813614845],
        [-4.13181080289514, -2.34226739863660, -3.44356159392859],
        [ 2.85007173009739, -2.64884892757600,  0.71010806424206],
        ])
    dipole = np.array(
        [-1.7019679049596192, -2.3705248395254794, 2.3242138027827446]
    )
    gradient = np.array([
        [ 0.009559998512721449,  0.003160492649991202,  0.002493263404035152],
        [-0.014057002659599450,  0.001307143355963449, -0.006896995523674975],
        [ 0.003153682694711128,  0.000577646576754350,  0.003242310422859749],
        [ 0.003450958779103499, -0.003371154526376105,  0.006833209066374420],
        [-0.001015432627909870, -0.003296949677104424,  0.001316980539002961],
        [-0.006952278070976579,  0.004741461728853791, -0.010835641525482725],
        [ 0.004676820346825542,  0.013884337727247118, -0.001369508087834928],
        [-0.008836453325485083, -0.008509582724068617, -0.004439799174447864],
        [ 0.014459308335089790,  0.005276511880967742,  0.004903442725946663],
        [-0.036094040309768836, -0.003785312815195147,  0.006658677483987865],
        [ 0.008136405754401969,  0.004504379636843624,  0.003321663239613836],
        [ 0.008869982110786701, -0.011001116814485038, -0.001446882216395328],
        [ 0.016590179303752735, -0.004068517105666850,  0.002429055885660720],
        [-0.007907876155693029, -0.003802464713817357, -0.003873086023200218],
        [-0.000245758070628337,  0.000875351650743832, -0.003291567698024252],
        [ 0.006211505382668360,  0.003507773169348530,  0.000954877481578866],
    ])

    calc = Calculator(Param.GFN1xTB, numbers, positions)

    calc.set_solvent(Solvent.methanol)

    res = calc.singlepoint()

    assert approx(res.get_energy(), thr) == -33.66717660261584
    assert approx(res.get_dipole(), thr) == dipole
    assert approx(res.get_gradient(), thr) == gradient

    calc.set_solvent()

    res = calc.singlepoint(res, copy=True)

    assert approx(res.get_energy(), thr) == -33.63768565903155


def test_gfn2xtb_solvation():
    """Use GFN2-xTB/GBSA for a mindless molecule"""
    thr = 1.0e-7

    numbers = np.array([
        1, 9, 15, 13, 1, 1, 13, 5, 3, 15, 8, 1, 1, 5, 16, 1,
    ])
    positions = np.array([
        [-2.14132037405479, -1.34402701877044, -2.32492500904728],
        [ 4.46671289205392, -2.04800110524830,  0.44422406067087],
        [-4.92212517643478, -1.73734240529793,  0.96890323821450],
        [-1.30966093045696, -0.52977363497805,  3.44453452239668],
        [-4.34208759006189, -4.30470270977329,  0.39887431726215],
        [ 0.61788392767516,  2.62484136683297, -3.28228926932647],
        [ 4.23562873444840, -1.68839322682951, -3.53824299552792],
        [ 2.23130060612446,  1.93579813100155, -1.80384647554323],
        [-2.32285463652832,  2.90603947535842, -1.39684847191937],
        [ 2.34557941578250,  2.86074312333371,  1.82827238641666],
        [-3.66431367659153, -0.42910188232667, -1.81957402856634],
        [-0.34927881505446, -1.75988134003940,  5.98017466326572],
        [ 0.29500802281217, -2.00226104143537,  0.53023447931897],
        [ 2.10449364205058, -0.56741404446633,  0.30975625014335],
        [-1.59355304432499,  3.69176153150419,  2.87878226787916],
        [ 4.34858700256050,  2.39171478113440, -2.61802993563738],
    ])
    dipole = np.array(
        [ 0.24089806056398366, -0.8387798297446885, -2.490982140104827]
    )
    gradient = np.array([
        [ 0.00665983765172852, -0.000306100468371254,  0.002975729588167250],
        [-0.00075554832215171,  0.001103331394141163,  0.002917549694785815],
        [ 0.00103709572973848, -0.000861474437293449,  0.005249091862608099],
        [ 0.00345933752444154, -0.004301298519638866, -0.003786850195834586],
        [-0.00078541037746589, -0.004659889270757375,  0.000757596433662243],
        [ 0.00322292779086688, -0.003572675716601181, -0.004746876147864423],
        [-0.00513395549346115,  0.011449011590338731,  0.002505538991042167],
        [-0.00574879905769782,  0.004579255119010918, -0.002779923711244377],
        [ 0.00241040419407409,  0.003121180180444150,  0.003515870816111050],
        [-0.00021150434069988, -0.002620960429434571, -0.008691267383737740],
        [-0.00323129790918273,  0.005268717780263234, -0.010531374769279896],
        [ 0.00203571944238303, -0.004757311655869700,  0.005097227197421218],
        [-0.00606663933320002,  0.003597297542372022, -0.002467813364587243],
        [ 0.00024286212984382, -0.009680057140546466,  0.014999309475018330],
        [-0.00090824770994144,  0.004745736486598619, -0.001923154458354601],
        [ 0.00377321808072424, -0.003104762454655897, -0.003090654027913303],
    ])

    calc = Calculator(Param.GFN2xTB, numbers, positions)

    res = calc.singlepoint()

    assert approx(res.get_energy(), thr) == -25.0841508410945

    calc.set_solvent(Solvent.ch2cl2)

    res = calc.singlepoint(res)

    assert approx(res.get_energy(), thr) == -25.11573992702904
    assert approx(res.get_dipole(), thr) == dipole
    assert approx(res.get_gradient(), thr) == gradient


def test_gfn1xtb_orbitals():
    """Try to access the GFN1-xTB wavefunction for a small molecule like water"""
    thr = 1.0e-6

    numbers = np.array([8, 1, 1])
    positions = np.array([
        [ 0.00000000000000, 0.00000000000000,-0.73578586109551],
        [ 1.44183152868459, 0.00000000000000, 0.36789293054775],
        [-1.44183152868459, 0.00000000000000, 0.36789293054775],
    ])
    eigenvalues = np.array([
        -0.75821687, -0.61119872, -0.54824272, -0.50023252,
        -0.15792833, -0.05043755,  0.33342098,  0.45699087,
    ])
    occupations = np.array([2.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0])
    coefficients = np.array([
        [
            -7.96486314e-01,  1.91513472e-15, -3.81069986e-01,  1.06627860e-15,
            -3.85581374e-01, -2.77555756e-16,  6.66133815e-16,  8.73808841e-01,
        ],
        [
             8.67361738e-16,  7.06326895e-01,  2.06085149e-15,  5.99181075e-17,
            -2.35922393e-16,  9.10524298e-02, -9.80328049e-01,  1.05471187e-15,
        ],
        [
             6.66133815e-16, -2.22044605e-16,  2.27595720e-15,  1.00000000e+00,
            -1.66533454e-16,  1.11022302e-16, -2.77555756e-17,  1.38777878e-17,
        ],
        [
            -7.03752745e-02, -2.35922393e-15,  8.51677843e-01, -1.85493019e-15,
            -1.38148603e-01,  4.02455846e-16,  7.77156117e-16,  7.23141261e-01,
        ],
        [
            -1.79427083e-01,  3.32421120e-01,  1.83354106e-01, -2.70755099e-17,
             3.63066743e-01, -3.84174939e-01,  8.29758195e-01, -7.50228671e-01,
        ],
        [
            -1.38489858e-02,  4.55724612e-02,  4.79829369e-02, -2.77816056e-16,
            -5.47923122e-01,  6.88051905e-01,  3.00554964e-01, -4.79998559e-01,
        ],
        [
            -1.79427083e-01, -3.32421120e-01,  1.83354106e-01, -4.15348025e-16,
             3.63066743e-01,  3.84174939e-01, -8.29758195e-01, -7.50228671e-01,
        ],
        [
            -1.38489858e-02, -4.55724612e-02,  4.79829369e-02, -1.37843421e-16,
            -5.47923122e-01, -6.88051905e-01, -3.00554964e-01, -4.79998559e-01,
        ],
    ], order='F')

    calc = Calculator(Param.GFN1xTB, numbers, positions)

    res = calc.singlepoint()

    assert res.get_number_of_orbitals() == 8
    assert approx(res.get_orbital_eigenvalues(), thr) == eigenvalues
    assert approx(res.get_orbital_occupations(), thr) == occupations
    this_coefficients = res.get_orbital_coefficients()
    # remember, signs of wavefunctions are tricky, better get this one right
    for i in range(res.get_number_of_orbitals()):
        assert approx(this_coefficients[i], thr) == +coefficients[i] \
            or approx(this_coefficients[i], thr) == -coefficients[i]
