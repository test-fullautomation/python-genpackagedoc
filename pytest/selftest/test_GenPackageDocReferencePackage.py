#  Copyright 2020-2024 Robert Bosch GmbH
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
# test_GenPackageDocReferencePackage.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 09.05.2023
#
# --------------------------------------------------------------------------------------------------------------

# -- import standard Python modules
import os, sys, time, platform, pytest, shlex, subprocess

# -- import own Python modules
from PythonExtensionsCollection.String.CString import CString

# --------------------------------------------------------------------------------------------------------------

class Test_GenPackageDocReferencePackage:
   """Tests of component GenPackageDoc (ReferencePackage)."""

   # --------------------------------------------------------------------------------------------------------------

   @pytest.mark.parametrize(
      "Description", ["Call GenPackageDoc for reference package",]
   )
   def test_GenPackageDocReferencePackage_1(self, Description):
      """pytest 'GenPackageDoc'"""

      sPython         = CString.NormalizePath(sys.executable)
      sSelftestFolder = os.path.dirname(os.path.realpath(__file__))
      sGenPackageDoc  = CString.NormalizePath(f"{sSelftestFolder}/reference-package-test/genpackagedoc.py")

      listCmdLineParts = []
      listCmdLineParts.append(f"\"{sPython}\"")
      listCmdLineParts.append(f"\"{sGenPackageDoc}\"")
      sCmdLine = " ".join(listCmdLineParts)
      listCmdLineParts = shlex.split(sCmdLine)
      nReturn = subprocess.call(listCmdLineParts)
      assert nReturn == 0

# eof class Test_GenPackageDocReferencePackage:

# --------------------------------------------------------------------------------------------------------------
