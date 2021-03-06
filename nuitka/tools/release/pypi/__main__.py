#!/usr/bin/python -u
#     Copyright 2019, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

""" Make PyPI upload of Nuitka, and check success of it. """

from __future__ import print_function

import os
import shutil
import sys

from nuitka.tools.release.Documentation import createReleaseDocumentation
from nuitka.tools.release.Release import checkBranchName
from nuitka.tools.testing.Virtualenv import withVirtualenv
from nuitka.Version import getNuitkaVersion


def main():
    nuitka_version = getNuitkaVersion()

    branch_name = checkBranchName()

    # Only real master releases so far.
    assert branch_name == "master", branch_name
    assert "pre" not in nuitka_version and "rc" not in nuitka_version


    print("Uploading Nuitka '%s'" % nuitka_version)

    # Need to remove the contents from the Rest, or else PyPI will not render
    # it. Stupid but true.
    contents = open("README.rst", "rb").read()
    contents = contents.replace(b".. contents::\n", b"")
    contents = contents.replace(b".. image:: doc/images/Nuitka-Logo-Symbol.png\n", b"")
    contents = contents.replace(b".. raw:: pdf\n\n   PageBreak oneColumn\n   SetPageCounter 1", b"")

    open("README.rst", "wb").write(contents)

    # Make sure it worked.
    contents = open("README.rst", "rb").read()
    assert b".. contents" not in contents

    shutil.rmtree("check_nuitka", ignore_errors = True)
    shutil.rmtree("dist", ignore_errors = True)

    print("Creating documentation.")
    createReleaseDocumentation()
    print("Creating source distribution.")
    assert os.system("python setup.py sdist") == 0

    print("Creating a virtualenv for quick test:")
    with withVirtualenv("check_nuitka") as venv:
        print("Installing Nuitka into virtualenv:")
        print('*' * 40)
        venv.runCommand("pip install ../dist/Nuitka*.tar.gz")
        print('*' * 40)

        print("Compiling basic test:")
        print('*' * 40)
        venv.runCommand("nuitka-run ../tests/basics/Asserts.py")
        print('*' * 40)

    if "check" not in sys.argv:
        print("Uploading source dist")
        assert os.system("twine upload dist/*") == 0
        print("Uploaded.")
    else:
        print("Checked OK, not uploaded.")
