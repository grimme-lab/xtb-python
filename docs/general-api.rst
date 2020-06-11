.. module:: xtb.interface

API Documentation
=================

.. important::

   All properties exchanged with the ``xtb`` API are given in `atomic units <https://en.wikipedia.org/wiki/Hartree_atomic_units>`_.
   For integrations with other frameworks the unit conventions might differ and require conversion.

.. contents::

Calculation Environment
-----------------------

.. autoclass:: Environment
   :members:

Molecular Structure Data
------------------------

.. autoclass:: Molecule
   :members:

Single Point Calculator
-----------------------

.. autoclass:: Calculator
   :members:

Calculation Results
-------------------

.. autoclass:: Results
   :members:

Available Calculation Methods
-----------------------------

.. autoclass:: Param
   :members:

.. automethod:: xtb.utils.get_method
