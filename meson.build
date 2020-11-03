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

project(
  'xtb-python',
  'c',
  license: 'LGPL-3.0-or-later',
  default_options: [
    'libdir=xtb',
    'default_library=static',
    'optimization=2',
  ]
)

cc = meson.get_compiler('c')

# In case you actually want to depend on the xtb shared library
if get_option('default_library') == 'shared'
  xtb_dep = declare_dependency(
    include_directories: include_directories('include'),
    dependencies: dependency('xtb', version: '>=6.3', required: true),
  )
  xtb_header = files('include/xtb.h')
else
# Import xtb as subproject, we need the API of version 6.3 or newer,
# in this mode we want to dependency free regarding xtb, therefore,
# we force xtb to provide a _static_ library to avoid depending on xtb at runtime
  xtb_prj = subproject(
    'xtb',
    version: '>=6.3',
    default_options: [
      'default_library=static',
      'static=false',
      'openmp=@0@'.format(get_option('openmp')),
      'la_backend=@0@'.format(get_option('la_backend')),
      'optimization=@0@'.format(get_option('optimization')),
    ],
  )
  xtb_dep = xtb_prj.get_variable('xtb_dep')
  xtb_header = xtb_prj.get_variable('xtb_header')
endif

pymod = import('python')
python = pymod.find_installation(
  'python@0@'.format(get_option('py')),
  modules: [
    'cffi',
  ],
)
python_dep = python.dependency(required: true)

# Python's CFFI is horrible in working with preprocessor statements,
# therefore, we have to preprocess the header before passing it to the ffibuilder
xtb_pp = configure_file(
  command: [cc, '-E', '@INPUT@'],
  input: xtb_header,
  output: '_libxtb.h',
  capture: true,
)

# This is the actual out-of-line API processing of the ffibuilder
xtb_cffi_srcs = configure_file(
  command: [python, files('ffibuilder.py'), '@INPUT@', '@BASENAME@'],
  input: xtb_pp,
  output: '@BASENAME@.c',
)

# Actual generation of the Python extension, since the shared_module does not work
# well with dependency objects, we will trick it by linking a whole static lib
xtb_pyext = python.extension_module(
  '_libxtb',
  link_whole: static_library(
    '_libxtb',
    xtb_cffi_srcs,
    dependencies: [xtb_dep, python_dep],
  ),
  dependencies: [xtb_dep, python_dep],
  install: true,
)
