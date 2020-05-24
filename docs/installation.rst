Installation
============

To install ``xtb-python`` from source clone the repository from GitHub with

.. code::

   git clone https://github.com/grimme-lab/xtb-python
   cd xtb-python
   git submodule update --init

This will ensure that you have access to the ``xtb-python`` and the parent ``xtb`` repository, with the latter to be found in ``subprojects/xtb``.
It is highly recommend to make yourself familiar with building ``xtb`` first.

To work with ``xtb-python`` it is necessary to build the extension to the ``xtb`` API first, this is accomplised by using meson and the C foreign function interface.
Following modules should be available to build this project:

.. code::

   cffi
   numpy
   meson  # build only

Additionally you will need a development version of Python, for the Python headers, a Fortran and a C compiler (GCC 7 or newer or Intel 17 or newer) and a linear algebra backend (providing LAPACK and BLAS API).

To install the meson build system first check your package manager for an up-to-date meson version, usually this will also install ninja as dependency.
Alternatively, you can install the latest version of meson and ninja with ``pip`` (or ``pip3`` depending on your system):

.. code::

   pip install cffi numpy meson ninja

If you prefer ``conda`` as a package manage you can install meson and ninja from the conda-forge channel.
Make sure to select the conda-forge channel for searching packages.

.. code::

   conda config --add channels conda-forge
   conda install cffi numpy meson ninja

Now, setup the project by building the CFFI extension module from the ``xtb`` API with:

.. code::

   meson setup build --prefix=$PWD --libdir=xtb
   ninja -C build install

If you have several versions of Python installed you can point meson with the ``-Dpy=<version>`` option to the correct one.
Depending on your setup you have to export your compilers (``CC`` and ``FC``) first and set the ``-Dla_backend=<name>`` and ``-Dopenmp=<bool>`` option accordingly.
For more information on the build with meson, follow the guide in the ``xtb`` repository `here <https://github.com/grimme-lab/xtb/blob/master/meson/README.adoc>`_.

This step will create the CFFI extension ``_libxtb`` and place it in the ``xtb`` directory.
After creating the ``_libxtb`` extension, the Python module can be installed as usual with

.. code::

   pip install -e .

Now you are set to start using ``xtb-python``.
You can test your setup by opening a new Python interpreter and try to import the interface module

.. code::

   >>> import xtb.interface
