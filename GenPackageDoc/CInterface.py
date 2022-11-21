# **************************************************************************************************************
#
#  Copyright 2020-2022 Robert Bosch GmbH
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
#
# **************************************************************************************************************
#
# CInterface.py
#
# XC-CT/ECA3-Queckenstedt
#
# 21.11.2022
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing an interface for **GenPackageDoc**. This interface can be used to get access to the
LaTeX stylesheets that are part of the **GenPackageDoc** installation.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time
import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Folder.CFolder import CFolder
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLNY = col.Style.NORMAL + col.Fore.YELLOW
COLBW = col.Style.BRIGHT + col.Fore.WHITE

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

class CInterface():

   def __init__(self):
      """
Constructor of class ``CInterface``.
      """

      sMethod = "CInterface.__init__"

      sThisFile = CString.NormalizePath(__file__)
      sThisFilePath = os.path.dirname(sThisFile)
      self.__sStylesFolder = f"{sThisFilePath}/styles"

   # eof def __init__(self, oRepositoryConfig=None):

   def __del__(self):
      pass

   def GetLaTeXStyles(self, sDestination=None):
      """
The LaTeX stylesheets are part of the installation of **GenPackageDoc**. In case of anyone else than **GenPackageDoc**
needs these stylesheets, this method can be used to copy them to any other folder.

**Arguments:**

* ``sDestination``

  / *Condition*: required / *Type*: str /

  Path and name of a folder in which the styles folder from **GenPackageDoc** will be copied.

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method ``sMethod`` was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method ``sMethod``.
      """
      sMethod  = "CInterface.GetLaTeXStyles"
      bSuccess = False
      sResult  = "UNKNOWN"
      if sDestination is None:
         bSuccess = None
         sResult  = "sDestination is None"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sDestination = CString.NormalizePath(sDestination)

      oStylesFolder = CFolder(self.__sStylesFolder)
      bSuccess, sResult = oStylesFolder.CopyTo(sDestination, bOverwrite=True)
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

# eof class CPackageDocConfig(): 

# **************************************************************************************************************


