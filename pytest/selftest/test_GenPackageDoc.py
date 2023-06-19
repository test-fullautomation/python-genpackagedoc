#  Copyright 2020-2023 Robert Bosch GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# --------------------------------------------------------------------------------------------------------------
#
# test_GenPackageDoc.py
#
# XC-CT/ECA3-Queckenstedt
#
# 10.11.2022
#
# --------------------------------------------------------------------------------------------------------------

# -- import standard Python modules
import os, sys, time, platform, pytest, shlex, subprocess

# -- import own Python modules
from PythonExtensionsCollection.String.CString import CString

# --------------------------------------------------------------------------------------------------------------

class Test_GenPackageDoc:
   """Tests of component GenPackageDoc."""

   # --------------------------------------------------------------------------------------------------------------

   @pytest.mark.parametrize(
      "Description", ["Call GenPackageDoc for current repository",]
   )
   def test_GenPackageDoc_1(self, Description):
      """pytest 'GenPackageDoc'"""

      sPython           = CString.NormalizePath(sys.executable)
      sRepositoryFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
      sGenPackageDoc    = CString.NormalizePath(f"{sRepositoryFolder}/genpackagedoc.py")

      listCmdLineParts = []
      listCmdLineParts.append(f"\"{sPython}\"")
      listCmdLineParts.append(f"\"{sGenPackageDoc}\"")
      sCmdLine = " ".join(listCmdLineParts)
      listCmdLineParts = shlex.split(sCmdLine)
      nReturn = subprocess.call(listCmdLineParts)
      assert nReturn == 0

# eof class Test_GenPackageDoc:

# --------------------------------------------------------------------------------------------------------------
