.. _install:

Installation
============

For the basic functionalities the ``xtb-python`` project requires following
packages:

.. code::

   cffi
   numpy

Additionally the project provides a calculator implementation for ASE (see :ref:`ase`) which becomes available if the ``ase`` package is installed.
For integration with the QCArchive infrastructure (see :ref:`qcarchive`) the ``qcelemental`` package is required.

Of course, the package depends on the `extended tight binding program package <https://xtb-docs.readthedocs.io>`_ as well, directly or indirectly.
Depending on how ``xtb-python`` was packaged it requires an installation of ``xtb`` or it will be able to provide its own.
For more details on the ``xtb`` API dependency see :ref:`building`.


.. _building:

Building from Source
--------------------

To install ``xtb-python`` from source clone the repository from GitHub with

.. code::

   git clone https://github.com/grimme-lab/xtb-python
   cd xtb-python
   git submodule update --init

This will ensure that you have access to the ``xtb-python`` and the parent ``xtb`` repository, with the latter to be found in ``subprojects/xtb``.


Building the Extension Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To work with ``xtb-python`` it is necessary to build the extension to the ``xtb`` API first, this is accomplised by using meson and the C foreign function interface (CFFI).
Following modules should be available to build this project:

.. code::

   cffi
   numpy
   meson  # build only

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

   meson setup build --prefix=$PWD --libdir=xtb --default-library=shared
   ninja -C build install

This step will create the CFFI extension ``_libxtb`` and place it in the ``xtb`` directory.


Meson cannot find xtb dependency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If meson cannot find your ``xtb`` installation check if you have ``pkg-config`` installed and that ``xtb`` can be found using

.. code::

   pkg-config xtb --print-errors

In case this fails ensure that the ``xtb.pc`` file is in a directory in the ``PKG_CONFIG_PATH`` and retry.
For the official release tarball you possible have to edit the first line of ``xtb.pc`` to point to the location where you installed ``xtb``:

.. code:: diff

   --- a/lib/pkgconfig/xtb.pc
   +++ b/lib/pkgconfig/xtb.pc
   @@ -1,4 +1,4 @@
   -prefix=/
   +prefix=/absolute/path/to/xtb
    libdir=${prefix}/lib
    includedir=${prefix}/include/xtb

.. note::

   Installs from conda-forge should work out-of-box.


Dealing with Several Versions of Python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have several versions of Python installed you can point meson with the ``-Dpy=<version>`` option to the correct one.
Depending on your setup you have to export your compilers (``CC`` and ``FC``) first and set the ``-Dla_backend=<name>`` and ``-Dopenmp=<bool>`` option accordingly.


.. _devel-install:

Installing in Development Mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After creating the ``_libxtb`` extension, the Python module can be installed as usual with

.. code::

   pip install -e .

Now you are set to start using ``xtb-python``.
You can test your setup by opening a new Python interpreter and try to import the interface module

.. code::

   >>> import xtb.interface

If you also want to use extensions install with

.. code::

   pip install -e '.[ase,qcschema]'

Now you can test your installation with

.. code::

   pytest --pyargs xtb


Helpful Tools
^^^^^^^^^^^^^

We aim for a high quality code base and encourage substainable development models.

Please, install a linter like ``flake8`` or ``pylint`` to catch errors before they become bugs.
Also, typehints are mandatory in this project, you should typecheck locally with ``mypy``.
A consistent coding style is enforced by using ``black``, every source file should be reformatted using ``black``, the only exceptions are tests.


Building without Upstream Dependency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For convenience we also offer a mode to work without an upstream ``xtb`` dependency, this can be quite handy if you also want to work on the ``xtb`` API itself or want to create a failsafe package that cannot break due to ABI or API incompatibilities.

.. note::

   It is highly recommend to make yourself familiar with building ``xtb`` first.

For this approach we follow the same scheme as with the normal extension build.
You will need the following packages installed

.. code::

   cffi
   numpy
   meson  # build only

Additionally you will need a development version of Python, for the Python headers, a Fortran and a C compiler (GCC 7 or newer or Intel 17 or newer) and a linear algebra backend (providing LAPACK and BLAS API).

We closely follow the approach from before, but we change the configuration of the extension build to

.. code::

   meson setup build --prefix=$PWD --libdir=xtb --default-library=static
   ninja -C build install


Depending on how you acquired the project mesons wrap-tool will first need to download the ``xtb`` source code.
Instead of dynamically depending on ``xtb`` the complete project will be build and included as a whole into the CFFI extension module, making your ``xtb-python`` effectively independent of ``xtb``.

You can pass the ``-Dopenmp=<bool>`` and ``-Dla_backend=<netlib|openblas|mkl>`` in the configuration step to configure the ``xtb`` build.
To change the compiler used export them in the environment variables ``CC`` and ``FC``.

.. tip::

   For more information on the build with meson, follow the guide in the ``xtb`` repository `here <https://github.com/grimme-lab/xtb/blob/master/meson/README.adoc>`_.

From here you can proceed with :ref:`devel-install`.
