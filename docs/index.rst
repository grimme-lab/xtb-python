Python API for the extended tight binding program
=================================================

This is the documentation of the Python API for the extended tight binding
program (``xtb``).
The project is hosted at `GitHub <https://github.com/grimme-lab/xtb-python>`_.


.. code::

   >>> from xtb.interface import Calculator
   >>> from xtb.utils import get_method
   >>> import numpy as np
   >>> numbers = np.array([8, 1, 1])
   >>> positions = np.array([
   ... [ 0.00000000000000, 0.00000000000000,-0.73578586109551],
   ... [ 1.44183152868459, 0.00000000000000, 0.36789293054775],
   ... [-1.44183152868459, 0.00000000000000, 0.36789293054775]])
   ...
   >>> calc = Calculator(get_method("GFN2-xTB"), numbers, positions)
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
   array([[ 6.24500451e-17 -3.47909735e-17 -5.07156941e-03]
          [-1.24839222e-03  2.43536791e-17  2.53578470e-03]
          [ 1.24839222e-03  1.04372944e-17  2.53578470e-03]])
   >>> res.get_charges()
   array([-0.56317912  0.28158956  0.28158956])


.. toctree::
   :maxdepth: 3
   :caption: Contents

   installation
   general-api
   ase-calculator
   qcarchive
