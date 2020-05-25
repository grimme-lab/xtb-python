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

from pytest import approx
from xtb.qcschema.harness import run_qcschema
import qcelemental as qcel
import numpy as np

def test_gfn2xtb_energy():
    """Use QCSchema to calculate the energy a halogen bond compoind"""
    thr = 1.0e-8

    atomic_input = qcel.models.AtomicInput(
        molecule = qcel.models.Molecule(
            symbols = [
                "C", "C", "C", "C", "C", "C", "I", "H", "H",
                "H", "H", "H", "S", "H", "C", "H", "H", "H",
            ],
            geometry = [
                -1.42754169820131, -1.50508961850828, -1.93430551124333,
                 1.19860572924150, -1.66299114873979, -2.03189643761298,
                 2.65876001301880,  0.37736955363609, -1.23426391650599,
                 1.50963368042358,  2.57230374419743, -0.34128058818180,
                -1.12092277855371,  2.71045691257517, -0.25246348639234,
                -2.60071517756218,  0.67879949508239, -1.04550707592673,
                -2.86169588073340,  5.99660765711210,  1.08394899986031,
                 2.09930989272956, -3.36144811062374, -2.72237695164263,
                 2.64405246349916,  4.15317840474646,  0.27856972788526,
                 4.69864865613751,  0.26922271535391, -1.30274048619151,
                -4.63786461351839,  0.79856258572808, -0.96906659938432,
                -2.57447518692275, -3.08132039046931, -2.54875517521577,
                -5.88211879210329, 11.88491819358157,  2.31866455902233,
                -8.18022701418703, 10.95619984550779,  1.83940856333092,
                -5.08172874482867, 12.66714386256482, -0.92419491629867,
                -3.18311711399702, 13.44626574330220, -0.86977613647871,
                -5.07177399637298, 10.99164969235585, -2.10739192258756,
                -6.35955320518616, 14.08073002965080, -1.68204314084441,
            ],
        ),
        driver = "energy",
        model = {
            "method": "GFN2-xTB",
        },
    )
    dipole_moment = np.array(
        [0.3345064021648074, -1.0700925215553294, -1.2299195418603437]
    )

    atomic_result = run_qcschema(atomic_input)

    assert atomic_result.success
    assert approx(atomic_result.return_result, thr) == -26.60185037124828
    assert approx(atomic_result.properties.scf_dipole_moment, thr) == dipole_moment


def test_gfn1xtb_gradient():
    """Use QCSchema to perform a calculation on a mindless molecule"""
    thr = 1.0e-8

    atomic_input = qcel.models.AtomicInput(
        molecule = qcel.models.Molecule(
            symbols = [
                "H", "H", "C", "B", "H", "P", "O", "Cl",
                "Al", "P", "B", "H", "F", "P", "H", "P",
            ],
            geometry = [
                 2.79274810283778,  3.82998228828316, -2.79287054959216,
                -1.43447454186833,  0.43418729987882,  5.53854345129809,
                -3.26268343665218, -2.50644032426151, -1.56631149351046,
                 2.14548759959147, -0.88798018953965, -2.24592534506187,
                -4.30233097423181, -3.93631518670031, -0.48930754109119,
                 0.06107643564880, -3.82467931731366, -2.22333344469482,
                 0.41168550401858,  0.58105573172764,  5.56854609916143,
                 4.41363836635653,  3.92515871809283,  2.57961724984000,
                 1.33707758998700,  1.40194471661647,  1.97530004949523,
                 3.08342709834868,  1.72520024666801, -4.42666116106828,
                -3.02346932078505,  0.04438199934191, -0.27636197425010,
                 1.11508390868455, -0.97617412809198,  6.25462847718180,
                 0.61938955433011,  2.17903547389232, -6.21279842416963,
                -2.67491681346835,  3.00175899761859,  1.05038813614845,
                -4.13181080289514, -2.34226739863660, -3.44356159392859,
                 2.85007173009739, -2.64884892757600,  0.71010806424206,
            ],
        ),
        driver = "gradient",
        model = {
            "method": "GFN1-xTB",
        },
    )
    dipole_moment = np.array(
        [-1.46493585, -2.03036834,  2.08330405]
    )
    gradient = np.array([
        [ 0.009232625741587227,  0.003155461859519221,  0.002442986999241168],
        [-0.011856864082491841, -0.001160759424710484, -0.001479499047578632],
        [ 0.003451262987231787,  0.000215308710760728,  0.003730567708416359],
        [ 0.003799388943258326, -0.004765860859119094,  0.007885211727762723],
        [-0.000379213106866044, -0.002675726930398858,  0.001107252098240491],
        [-0.007936554347068041,  0.005513289713065560, -0.010832254028311825],
        [ 0.006084605665938956,  0.013967585988624595, -0.009310025918892868],
        [-0.003220049379416426, -0.003946107654179984, -0.003740489224738476],
        [ 0.006756157759172355,  0.000984515116819424,  0.007424736434524648],
        [-0.030710275643265804, -0.004788736649680724,  0.009562034140682116],
        [ 0.008109832723283130,  0.003419009494804033,  0.001692916089380574],
        [ 0.005703460535291335, -0.009863992151429374,  0.001725512568523476],
        [ 0.011742825276516265, -0.002780169889933200, -0.001075047642530233],
        [-0.007336820690528053, -0.002159490005562796, -0.004872570579801525],
        [-0.000541853527432064,  0.000671321722173119, -0.003239422092578492],
        [ 0.007101471144788836,  0.004214350959247828, -0.001021909232339549],
    ])

    atomic_result = run_qcschema(atomic_input)

    assert atomic_result.success
    assert approx(atomic_result.properties.return_energy, thr) == -33.63768565903155
    assert approx(atomic_result.properties.scf_dipole_moment, thr) == dipole_moment
    assert approx(atomic_result.return_result, thr) == gradient


def test_gfn2xtb_gradient():
    """Use QCSchema to perform a GFN2-xTB calculation on a mindless molecule"""
    thr = 1.0e-8

    atomic_input = qcel.models.AtomicInput(
        molecule = qcel.models.Molecule(
            symbols = [
                "H", "F", "P", "Al", "H", "H", "Al", "B",
                "Li", "P", "O", "H", "H", "B", "S", "H",
            ],
            geometry = [
                -2.14132037405479, -1.34402701877044, -2.32492500904728,
                 4.46671289205392, -2.04800110524830,  0.44422406067087,
                -4.92212517643478, -1.73734240529793,  0.96890323821450,
                -1.30966093045696, -0.52977363497805,  3.44453452239668,
                -4.34208759006189, -4.30470270977329,  0.39887431726215,
                 0.61788392767516,  2.62484136683297, -3.28228926932647,
                 4.23562873444840, -1.68839322682951, -3.53824299552792,
                 2.23130060612446,  1.93579813100155, -1.80384647554323,
                -2.32285463652832,  2.90603947535842, -1.39684847191937,
                 2.34557941578250,  2.86074312333371,  1.82827238641666,
                -3.66431367659153, -0.42910188232667, -1.81957402856634,
                -0.34927881505446, -1.75988134003940,  5.98017466326572,
                 0.29500802281217, -2.00226104143537,  0.53023447931897,
                 2.10449364205058, -0.56741404446633,  0.30975625014335,
                -1.59355304432499,  3.69176153150419,  2.87878226787916,
                 4.34858700256050,  2.39171478113440, -2.61802993563738,
            ],
        ),
        driver = "gradient",
        model = {
            "method": "GFN2-xTB",
        },
    )
    dipole_moment = np.array(
        [ 0.1965142200947483, -0.8278681912495578, -1.9355888893816835]
    )
    gradient = np.array([
        [ 0.0069783199901860, -0.0013477246501793,  0.0010781169024996],
        [ 0.0002245760328214,  0.0002461647063229,  0.0062721657019107],
        [ 0.0036253147861844,  0.0003663697566435,  0.0021555726017106],
        [ 0.0019571014953462, -0.0033251320565502, -0.0110309510839002],
        [-0.0009186617501583, -0.0039884254506426,  0.0011419318270997],
        [ 0.0052286904677730, -0.0043940169970672, -0.0027343675046787],
        [-0.0046665513593806,  0.0111387001975174, -0.0006277441729905],
        [-0.0072317611360968,  0.0056220899535598, -0.0056491341759185],
        [ 0.0006715799480324,  0.0045954408931370, -0.0009594930700533],
        [ 0.0015378112227006, -0.0012738847766192, -0.0068208361151305],
        [-0.0059049703734566,  0.0037272603873189, -0.0037133077831667],
        [ 0.0029282115252705, -0.0055314984132877,  0.0087808276778173],
        [-0.0059661722391951,  0.0042074193137524, -0.0010409230261016],
        [-0.0005376291052159, -0.0099752599374293,  0.0132926284229436],
        [-0.0013041988551268,  0.0036683821340513,  0.0018650958736729],
        [ 0.0033783393503154, -0.0037358850605277, -0.0020095820757144],
    ])

    atomic_result = run_qcschema(atomic_input)

    assert atomic_result.success
    assert approx(atomic_result.properties.return_energy, thr) == -25.0841508410945
    assert approx(atomic_result.properties.scf_dipole_moment, thr) == dipole_moment
    assert approx(atomic_result.return_result, thr) == gradient


def test_gfn1xtb_hessian():
    """Hessian not available from API, should fail"""

    atomic_input = qcel.models.AtomicInput(
        molecule = qcel.models.Molecule(
            symbols = [
                "C", "C", "C", "C", "N", "C", "S", "H", "H", "H", "H", "H",
            ],
            geometry = [
                -2.56745685564671, -0.02509985979910,  0.00000000000000,
                -1.39177582455797,  2.27696188880014,  0.00000000000000,
                 1.27784995624894,  2.45107479759386,  0.00000000000000,
                 2.62801937615793,  0.25927727028120,  0.00000000000000,
                 1.41097033661123, -1.99890996077412,  0.00000000000000,
                -1.17186102298849, -2.34220576284180,  0.00000000000000,
                -2.39505990368378, -5.22635838332362,  0.00000000000000,
                 2.41961980455457, -3.62158019253045,  0.00000000000000,
                -2.51744374846065,  3.98181713686746,  0.00000000000000,
                 2.24269048384775,  4.24389473203647,  0.00000000000000,
                 4.66488984573956,  0.17907568006409,  0.00000000000000,
                -4.60044244782237, -0.17794734637413,  0.00000000000000,
            ],
        ),
        driver = "hessian",
        model = {
            "method": "GFN1-xTB",
        },
    )

    atomic_result = run_qcschema(atomic_input)

    assert not atomic_result.success


def test_gfn2xtb_properties():
    """Also test properties run type once, should just return everything
    available as a dict"""
    thr = 1.0e-8

    atomic_input = qcel.models.AtomicInput(
        molecule = qcel.models.Molecule(
            symbols = [
                "Li", "Li", "Li", "Li", "C", "C", "C", "C",
                "H", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H",
            ],
            geometry = [
                 1.58746019997201, -1.58746019997201,  1.58746019997201,
                -1.58746019997201,  1.58746019997201,  1.58746019997201,
                -1.58746019997201, -1.58746019997201, -1.58746019997201,
                 1.58746019997201,  1.58746019997201, -1.58746019997201,
                -2.38500089414639, -2.38500089414639,  2.38500089414639,
                 2.38500089414639, -2.38500089414639, -2.38500089414639,
                -2.38500089414639,  2.38500089414639, -2.38500089414639,
                 2.38500089414639,  2.38500089414639,  2.38500089414639,
                -4.43487372589517, -2.13523102374668,  2.13523102374668,
                -2.13523102374668, -4.43487372589517,  2.13523102374668,
                -2.13523102374668, -2.13523102374668,  4.43487372589517,
                 2.13523102374668,  4.43487372589517,  2.13523102374668,
                 2.13523102374668,  2.13523102374668,  4.43487372589517,
                 4.43487372589517,  2.13523102374668,  2.13523102374668,
                 2.13523102374668, -2.13523102374668, -4.43487372589517,
                 4.43487372589517, -2.13523102374668, -2.13523102374668,
                 2.13523102374668, -4.43487372589517, -2.13523102374668,
                -2.13523102374668,  2.13523102374668, -4.43487372589517,
                -4.43487372589517,  2.13523102374668, -2.13523102374668,
                -2.13523102374668,  4.43487372589517, -2.13523102374668,
            ],
        ),
        driver = "properties",
        model = {
            "method": "GFN2-xTB",
        },
    )

    atomic_result = run_qcschema(atomic_input)

    assert atomic_result.success
    assert approx(atomic_result.return_result['return_energy'], thr) == -15.6117512083347
