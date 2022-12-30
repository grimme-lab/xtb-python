.. _install:

Installation
============

Depending on what you plan to do with ``xtb-python`` there are two recommended ways to install.

If you plan to use this project in your workflows, proceed with the :ref:`conda-forge`.
If you plan to develop on this project, proceed with :ref:`building`.

.. contents::

For the basic functionalities the ``xtb-python`` project requires following packages:

.. code-block:: none

   cffi
   numpy

Additionally the project provides a calculator implementation for ASE (see :ref:`ase`) which becomes available if the ``ase`` package is installed.
For integration with the QCArchive infrastructure (see :ref:`qcarchive`) the ``qcelemental`` package is required.

Of course, the package depends on the `extended tight binding program package <https://xtb-docs.readthedocs.io>`_ as well, directly or indirectly.
Depending on how ``xtb-python`` was packaged it requires an installation of ``xtb`` or it will be able to provide its own.
For more details on the ``xtb`` API dependency see :ref:`building`.


.. _conda-forge:

Installation with Conda
-----------------------

For details on how to setup conda look up the `conda documentation <https://docs.conda.io>`_.

Installing ``xtb-python`` from the conda-forge channel can be achieved by adding conda-forge to your channels with:

.. code-block:: none

   conda config --add channels conda-forge

Once the conda-forge channel has been enabled, ``xtb-python`` can be installed with:

.. code-block:: none

   conda install xtb-python

It is possible to list all of the versions of ``xtb-python`` available on your platform with:

.. code-block:: none

   conda search xtb-python --channel conda-forge

To install the additional dependencies for ASE and QCArchive integration use

.. code-block:: none

   conda install qcelemental ase


.. _building:

Building from Source
--------------------

To install ``xtb-python`` from source clone the repository from GitHub with

.. code-block:: none

   git clone https://github.com/grimme-lab/xtb-python
   cd xtb-python


Building the Extension Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To work with ``xtb-python`` it is necessary to build the extension to the ``xtb`` API first, this is accomplised by using meson and the C foreign function interface (CFFI).
Following modules should be available to build this project:

.. code-block:: none

   cffi
   numpy
   meson  # build only

To install the meson build system first check your package manager for an up-to-date meson version, usually this will also install ninja as dependency.
Alternatively, you can install the latest version of meson and ninja with ``pip`` (or ``pip3`` depending on your system):

.. code-block:: none

   pip install cffi numpy meson ninja

If you prefer ``conda`` as a package manage you can install meson and ninja from the conda-forge channel.
Make sure to select the conda-forge channel for searching packages.

.. code-block:: none

   conda config --add channels conda-forge
   conda install cffi numpy meson ninja

Now, setup the project by building the CFFI extension module from the ``xtb`` API with:

.. code-block:: none

   meson setup build --prefix=$HOME/.local
   ninja -C build install


Meson cannot find xtb dependency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If meson cannot find your ``xtb`` installation check if you have ``pkg-config`` installed and that ``xtb`` can be found using

.. code-block:: none

   pkg-config xtb --print-errors

In case this fails ensure that the ``xtb.pc`` file is in a directory in the ``PKG_CONFIG_PATH`` and retry.
For the official release tarball you possible have to edit the first line of ``xtb.pc`` to point to the location where you installed ``xtb``:

.. code-block:: diff

   --- a/lib/pkgconfig/xtb.pc
   +++ b/lib/pkgconfig/xtb.pc
   @@ -1,4 +1,4 @@
   -prefix=/
   +prefix=/absolute/path/to/xtb
    libdir=${prefix}/lib
    includedir=${prefix}/include/xtb

.. note::

   Installs from conda-forge should work out-of-box.


Helpful Tools
^^^^^^^^^^^^^

We aim for a high quality code base and encourage substainable development models.

Please, install a linter like ``flake8`` or ``pylint`` to catch errors before they become bugs.
Also, typehints are mandatory in this project, you should typecheck locally with ``mypy``.
A consistent coding style is enforced by using ``black``, every source file should be reformatted using ``black``, the only exceptions are tests.
