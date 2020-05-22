Python API for the extended tight binding program
=================================================

This repository host the Python API for the extended tight binding (``xtb``) program.

The idea of this project is to provide the ``xtb`` API for Python *without*
requiring an additional ``xtb`` installation.

*This project is still work in progress!*


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
Also ensure that you have the ``numpy`` and ``cffi`` package installed,
configure the build of the extension with:

.. code::

   meson setup build --prefix=$PWD --libdir=xtb
   ninja -C build install

If you have several versions of Python installed you can point meson with
the ``-Dpy=<version>`` to the correct one.
This will create the CFFI module ``xtb._libxtb``.

After creating the ``_libxtb`` extension, the python module can be installed
as usual

.. code::

   pip install -e .


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
