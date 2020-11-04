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
"""Tests for the ASE Calculator

.. important::

    The ASE calculator is taking input coordinates in Angstrom and returns
    energies in eV (while xtb is working internally in atomic units).
"""

from xtb.ase.calculator import XTB
from ase.atoms import Atoms
from ase.calculators.calculator import CalculationFailed, InputError
from pytest import approx, raises
import numpy as np


def test_gfn2_xtb_0d():
    """Test ASE interface to GFN2-xTB"""
    thr = 1.0e-5

    atoms = Atoms(
        symbols = 'CHOCH2CH4CH2OH',
        positions = np.array([
            [ 1.578385,  0.147690,  0.343809],
            [ 1.394750,  0.012968,  1.413545],
            [ 1.359929, -1.086203, -0.359782],
            [ 0.653845,  1.215099, -0.221322],
            [ 1.057827,  2.180283,  0.093924],
            [ 0.729693,  1.184864, -1.311438],
            [-0.817334,  1.152127,  0.208156],
            [-1.303525,  2.065738, -0.145828],
            [-0.883765,  1.159762,  1.299260],
            [ 1.984120, -1.734446, -0.021385],
            [ 2.616286,  0.458948,  0.206544],
            [-1.627725, -0.034052, -0.311301],
            [-2.684229,  0.151015, -0.118566],
            [-1.501868, -0.118146, -1.397506],
            [-1.324262, -1.260154,  0.333377],
            [-0.417651, -1.475314,  0.076637],
        ]),
    )
    forces = np.array([
        [-0.28561158, -0.48592026, -0.28392327],
        [-0.05526158, -0.07403455,  0.09665539],
        [ 0.18824950,  0.39170140,  0.33881928],
        [-0.01166074,  0.24653252, -0.16779606],
        [-0.05367503,  0.03368063,  0.05115422],
        [-0.09605262, -0.10000389,  0.01097286],
        [ 0.09423300,  0.18573616,  0.17797438],
        [ 0.02651896, -0.04073849, -0.03655980],
        [ 0.07886359, -0.05806479,  0.00649360],
        [-0.00780520, -0.07979390, -0.03175697],
        [ 0.13328595,  0.03209283, -0.04638514],
        [ 0.08197778, -0.39157299,  0.12107401],
        [-0.11453823, -0.01485088,  0.09974068],
        [ 0.09786017, -0.09130861, -0.05738675],
        [-0.26643400,  0.47603727, -0.27856705],
        [ 0.19005003, -0.02949244, -0.00050938],
    ])
    charges = np.array([
        0.08239823,  0.03066406, -0.44606929, -0.06139043,  0.03610596,
        0.05389499, -0.06991855,  0.03384415,  0.04665524,  0.28688538,
        0.02246569,  0.08251610,  0.03810481,  0.01883776, -0.46691965,
        0.31192554,
    ])
    dipole_moment = np.array([0.62120710, 0.28006659, 0.04465985])

    calc = XTB(method="GFN2-xTB", atoms=atoms)

    assert approx(atoms.get_potential_energy(), abs=thr) == -592.6794366990786
    assert approx(atoms.get_forces(), abs=thr) == forces
    assert approx(atoms.get_charges(), abs=thr) == charges
    assert approx(atoms.get_dipole_moment(), abs=thr) == dipole_moment

    atoms.calc.set(
        accuracy=0.1,
        electronic_temperature=500.0,
        max_iterations=20,
        solvent="ch2cl2",
    )

    assert approx(atoms.get_potential_energy(), abs=thr) == -592.9940608761889


def test_gfn1_xtb_0d():
    """Test ASE interface to GFN1-xTB"""
    thr = 1.0e-5

    atoms = Atoms(
        symbols = 'CHOCH2CH4CH2OH',
        positions = np.array([
            [ 1.578385,  0.147690,  0.343809],
            [ 1.394750,  0.012968,  1.413545],
            [ 1.359929, -1.086203, -0.359782],
            [ 0.653845,  1.215099, -0.221322],
            [ 1.057827,  2.180283,  0.093924],
            [ 0.729693,  1.184864, -1.311438],
            [-0.817334,  1.152127,  0.208156],
            [-1.303525,  2.065738, -0.145828],
            [-0.883765,  1.159762,  1.299260],
            [ 1.984120, -1.734446, -0.021385],
            [ 2.616286,  0.458948,  0.206544],
            [-1.627725, -0.034052, -0.311301],
            [-2.684229,  0.151015, -0.118566],
            [-1.501868, -0.118146, -1.397506],
            [-1.324262, -1.260154,  0.333377],
            [-0.417651, -1.475314,  0.076637],
        ]),
    )
    forces = np.array([
        [-0.37070590, -0.51067739, -0.27981764],
        [-0.04339461, -0.09290876,  0.22940156],
        [ 0.11141234,  0.46678720,  0.24552625],
        [ 0.04255709,  0.19019316, -0.23531997],
        [-0.01897377,  0.10810803,  0.05314982],
        [-0.07150720, -0.05182148, -0.08413638],
        [ 0.06631826,  0.10587709,  0.29833479],
        [-0.01062355,  0.02301460, -0.04964730],
        [ 0.06610108, -0.02724994,  0.09234280],
        [ 0.06519070, -0.19311773, -0.01152205],
        [ 0.23879786,  0.09871398, -0.04009526],
        [-0.04381577, -0.49997745,  0.08672818],
        [-0.23259608,  0.13735636,  0.06783414],
        [ 0.08297636, -0.09566973, -0.20602954],
        [-0.23686052,  0.57454371, -0.17194215],
        [ 0.35512370, -0.23317164,  0.00519275]
    ])
    charges = np.array([
        0.19494678,  0.01759972, -0.57108503, -0.05371086,  0.02458495,
        0.03915074, -0.06889977,  0.02521441,  0.03350058,  0.34380081,
        0.01442221,  0.20053193,  0.02454679,  0.01011690, -0.58349877,
        0.34877861,
    ])
    dipole_moment = np.array([0.76943477, 0.33021928, 0.05670150])

    atoms.calc = XTB(method="GFN1-xTB")

    assert approx(atoms.get_potential_energy(), abs=thr) == -632.7363734598027
    assert approx(atoms.get_forces(), abs=thr) == forces
    assert approx(atoms.get_charges(), abs=thr) == charges
    assert approx(atoms.get_dipole_moment(), abs=thr) == dipole_moment


def test_gfn1_xtb_3d():
    """Test ASE interface to GFN1-xTB"""
    thr = 5.0e-6

    atoms = Atoms(
        symbols = 'C4O8',
        positions = np.array([
            [0.9441259872,  0.9437851680,  0.9543505632],
            [3.7179966528,  0.9556570368,  3.7316862240],
            [3.7159517376,  3.7149292800,  0.9692330016],
            [0.9529872864,  3.7220864832,  3.7296981120],
            [1.6213905408,  1.6190616096,  1.6313879040],
            [0.2656685664,  0.2694175776,  0.2776540416],
            [4.3914553920,  1.6346256864,  3.0545920000],
            [3.0440834880,  0.2764611744,  4.4080419264],
            [4.3910577696,  3.0416409504,  0.2881058304],
            [3.0399936576,  4.3879335936,  1.6497353376],
            [0.2741322432,  4.4003734944,  3.0573754368],
            [1.6312174944,  3.0434586528,  4.4023048032],
        ]),
        cell = np.array([5.68032, 5.68032, 5.68032]),
        pbc = np.array([True, True, True]),
    )
    forces = np.array([
        [ 0.05008078,  0.06731033,  0.06324782],
        [-0.03885473,  0.07550136, -0.06667888],
        [-0.06455676, -0.04199831,  0.06908718],
        [ 0.04672903, -0.06303119, -0.06002863],
        [-1.9460667 , -1.94514641, -1.94923488],
        [ 1.92953942,  1.91109506,  1.92038457],
        [-1.91269913, -1.95500822,  1.94675148],
        [ 1.94009239,  1.91238163, -1.93489981],
        [-1.90757165,  1.94211445,  1.94655816],
        [ 1.94283273, -1.90965163, -1.95863335],
        [ 1.91207771, -1.94256232,  1.9337591 ],
        [-1.95160309,  1.94899525, -1.91031277],
    ])
    charges = np.array([
         0.74256902,  0.74308482,  0.74305612,  0.74300613, -0.37010244,
        -0.37234708, -0.37134504, -0.37177066, -0.37176288, -0.37133667,
        -0.37178059, -0.37127074,
    ])

    atoms.calc = XTB(method="GFN1-xTB")
    assert atoms.pbc.all()

    assert approx(atoms.get_potential_energy(), abs=thr) == -1256.768167202048
    assert approx(atoms.get_forces(), abs=thr) == forces
    assert approx(atoms.get_charges(), abs=thr) == charges


def test_gfn2_xtb_3d():
    """Test ASE interface to GFN2-xTB, should fail"""
    thr = 5.0e-6

    atoms = Atoms(
        symbols = 'C4O8',
        positions = np.array([
            [0.9441259872,  0.9437851680,  0.9543505632],
            [3.7179966528,  0.9556570368,  3.7316862240],
            [3.7159517376,  3.7149292800,  0.9692330016],
            [0.9529872864,  3.7220864832,  3.7296981120],
            [1.6213905408,  1.6190616096,  1.6313879040],
            [0.2656685664,  0.2694175776,  0.2776540416],
            [4.3914553920,  1.6346256864,  3.0545920000],
            [3.0440834880,  0.2764611744,  4.4080419264],
            [4.3910577696,  3.0416409504,  0.2881058304],
            [3.0399936576,  4.3879335936,  1.6497353376],
            [0.2741322432,  4.4003734944,  3.0573754368],
            [1.6312174944,  3.0434586528,  4.4023048032],
        ]),
        cell = np.array([5.68032, 5.68032, 5.68032]),
        pbc = np.array([True, True, True]),
    )

    calc = XTB(method="GFN2-xTB")
    atoms.calc = calc

    with raises(CalculationFailed):
        atoms.get_potential_energy()

    # make structure molecular
    atoms.set_pbc(False)
    assert approx(atoms.get_potential_energy(), abs=thr) == -1121.9196707084955

    with raises(InputError):
        atoms.positions = np.zeros((len(atoms), 3))
        calc.calculate(atoms=atoms, system_changes=["positions"])


def test_invalid_method():
    """GFN-xTB without method number is invalid, should raise an input error"""

    with raises(InputError):
        calc = XTB(method="GFN-xTB")
