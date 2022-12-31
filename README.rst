Python API for the extended tight binding program
=================================================

.. image:: https://img.shields.io/conda/vn/conda-forge/xtb-python.svg
   :alt: Conda Version
   :target: https://anaconda.org/conda-forge/xtb-python
.. image:: https://img.shields.io/github/license/grimme-lab/xtb-python
   :alt: License
   :target: COPYING.LESSER
.. image:: https://readthedocs.org/projects/xtb-python/badge/?version=latest
   :alt: Documentation Status
   :target: https://xtb-python.readthedocs.io/en/latest/?badge=latest
.. image:: https://img.shields.io/lgtm/grade/python/g/grimme-lab/xtb-python.svg
   :alt: LGTM
   :target: https://lgtm.com/projects/g/grimme-lab/xtb-python/context:python
.. image:: https://codecov.io/gh/grimme-lab/xtb-python/branch/main/graph/badge.svg
   :alt: Codecov
   :target: https://codecov.io/gh/grimme-lab/xtb-python

This repository hosts the Python API for the extended tight binding (``xtb``) program.

The idea of this project is to provide the ``xtb`` API for Python *without*
requiring an additional ``xtb`` installation.


Installation
------------

Depending on what you plan to do with ``xtb-python`` there are two recommended
ways to install.

* If you plan to use this project in your workflows, follow the 
  Conda Installation section.
* If you plan to develop on this project, proceed
  with the Build from Source section.

For more details visit the `documentation <https://xtb-python.readthedocs.io/en/latest/installation.html>`_.


Conda Installation
~~~~~~~~~~~~~~~~~~

Installing ``xtb-python`` from the ``conda-forge`` channel can be achieved by adding ``conda-forge`` to your channels with:

.. code::

   conda config --add channels conda-forge

Once the ``conda-forge`` channel has been enabled, ``xtb-python`` can be installed with:

.. code::

   conda install xtb-python

It is possible to list all of the versions of ``xtb-python`` available on your platform with:

.. code::

   conda search xtb-python --channel conda-forge


Build from Source
~~~~~~~~~~~~~~~~~

The project is build with meson, the exact dependencies are defined by the ``xtb``
project, in summary it requires a Fortran and a C compiler as well as a
linear algebra backend. Make yourself familiar with building ``xtb`` first!

Additionally this project requires a development version of Python installed.
Also ensure that you have the ``numpy`` and ``cffi`` packages installed,
configure the build of the extension with.

All steps to build the project are automated using

.. code::

   pip install .

To pass options to the meson build of xtb use ``--config-setting setup-args="-Dxtb-6.5.1:la_backend=openblas"`` to set for example the linear algebra backend to OpenBLAS.


Contributing
------------

Contributions to this open source project are very welcome. Before starting,
review our `contributing guidelines <CONTRIBUTING.rst>`_ first, please.


License
-------

``xtb-python`` is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

``xtb-python`` is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
merchantability or fitness for a particular purpose.  See the
GNU Lesser General Public License for more details.
