#!/usr/bin/env python3
#
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

import os
import cffi

library = "xtb"
include_header = '#include "' + library + '.h"'
prefix_var = library.upper() + "_PREFIX"
if prefix_var not in os.environ:
    prefix_var = "CONDA_PREFIX"

if __name__ == "__main__":
    import sys

    kwargs = dict(libraries=[library])

    header_file = sys.argv[1]
    module_name = sys.argv[2]

    with open(header_file) as f:
        cdefs = f.read()
else:
    import subprocess

    try:
        import pkgconfig

        if not pkgconfig.exists(library):
            raise ModuleNotFoundError("Unable to find pkg-config package 'xtb'")
        if pkgconfig.installed(library, "< 6.3"):
            raise Exception(
                "Installed 'xtb' version is too old, 6.3 or newer is required"
            )

        kwargs = pkgconfig.parse(library)
        cflags = pkgconfig.cflags(library).split()

    except ModuleNotFoundError:
        kwargs = dict(libraries=[library])
        cflags = []
        if prefix_var in os.environ:
            prefix = os.environ[prefix_var]
            kwargs.update(
                include_dirs=[os.path.join(prefix, "include")],
                library_dirs=[os.path.join(prefix, "lib")],
                runtime_library_dirs=[os.path.join(prefix, "lib")],
            )
            cflags.append("-I" + os.path.join(prefix, "include"))

    cc = os.environ["CC"] if "CC" in os.environ else "cc"

    module_name = library + "._lib" + library

    p = subprocess.Popen(
        [cc, *cflags, "-E", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate(include_header.encode())

    cdefs = out.decode()

ffibuilder = cffi.FFI()
ffibuilder.set_source(module_name, include_header, **kwargs)
ffibuilder.cdef(cdefs)

if __name__ == "__main__":
    ffibuilder.distutils_extension(".")
