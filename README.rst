Python API for the extended tight binding program
=================================================

.. image:: https://img.shields.io/github/license/grimme-lab/xtb-python
   :alt: License
   :target: COPYING.LESSER
.. image:: https://travis-ci.com/grimme-lab/xtb-python.svg?branch=master
   :alt: Travis CI
   :target: https://travis-ci.com/grimme-lab/xtb-python
.. image:: https://readthedocs.org/projects/xtb-python/badge/?version=latest
   :alt: Documentation Status
   :target: https://xtb-python.readthedocs.io/en/latest/?badge=latest
.. image:: https://img.shields.io/lgtm/grade/python/g/grimme-lab/xtb-python.svg
   :alt: LGTM
   :target: https://lgtm.com/projects/g/grimme-lab/xtb-python/context:python
.. image:: https://codecov.io/gh/grimme-lab/xtb-python/branch/master/graph/badge.svg
   :alt: Codecov
   :target: https://codecov.io/gh/grimme-lab/xtb-python

This repository host the Python API for the extended tight binding (``xtb``) program.

The idea of this project is to provide the ``xtb`` API for Python *without*
requiring an additional ``xtb`` installation.


Installation
------------

When building this project from source, make sure to initialize the git submodules
with

.. code::

   git submodules update --init

The project is build with meson, the exact dependencies are defined by the ``xtb``
project, in summary it requires a Fortran and a C compiler as well as a
linear algebra backend. Make yourself familiar with building ``xtb`` first!

Additionally this project requires a development version of Python installed.
Also ensure that you have the ``numpy`` and ``cffi`` packages installed,
configure the build of the extension with:

.. code::

   meson setup build --prefix=$PWD --libdir=xtb
   ninja -C build install

If you have several versions of Python installed you can point meson with
the ``-Dpy=<version>`` option to the correct one.
This will create the CFFI extension ``_libxtb`` and place it in the ``xtb``
directory.

In case meson fails to configure or build, check the options for ``-Dla_backed``
and ``-Dopenmp`` which are passed to the ``xtb`` subproject.
For more information on the build with meson, follow the guide in the ``xtb``
repository `here <https://github.com/grimme-lab/xtb/blob/master/meson/README.adoc>`_.

After creating the ``_libxtb`` extension, the Python module can be installed
as usual with

.. code::

   pip install -e .

For more details visit the `documentation <https://xtb-python.readthedocs.io/en/latest/installation.html>`.


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
