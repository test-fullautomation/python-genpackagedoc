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
# CSourceParser.py
#
# XC-CT/ECA3-Queckenstedt
#
# 13.04.2022
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, shlex, subprocess
import colorama as col
import ast

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW

# --------------------------------------------------------------------------------------------------------------

class CSourceParser():
   """
Class: CSourceParser
====================

The ``CSourceParser`` class provides a method to parse the functions, classes and their methods
together with the corresponding docstrings out of Python modules. The docstrings have to be written in rst syntax.
   """

   def ParseSourceFile(self, sFile=None):
      """
Method: ParseSourceFile
-----------------------

The method ``ParseSourceFile`` parses the content of a Python module.

**Arguments:**

* ``sFile``

  / *Condition*: required / *Type*: str /

  Path and name of a single Python module.

**Returns:**

* ``dictContent``

  / *Type*: dict /

  A dictionary containing all the information parsed out of ``sFile``.

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method ``sMethod`` was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method ``sMethod``.
      """

      sMethod = "ParseSourceFile"

      # error of sFile is None or does not exist

      oSourceFile = CFile(sFile)
      listLines, bSuccess, sResult = oSourceFile.ReadLines()
      del oSourceFile
      sContent = "\n".join(listLines)

      astModule = ast.parse(sContent)

      dictContent = {}
      listofdictFunctions = []
      listofdictClasses = []

      # print(f"================= sMethod : {sMethod}")

      for node in astModule.body:

         # print("================= node")

         if isinstance(node, ast.FunctionDef):
            dictFunction = {}
            sFunctionName = f"{node.name}"
            # print(f"* function : '{sFunctionName}'")
            dictFunction['sFunctionName'] = sFunctionName
            sFunctionDocString = ast.get_docstring(node)
            dictFunction['sFunctionDocString'] = sFunctionDocString
            listofdictFunctions.append(dictFunction)
         # eof if isinstance(node, ast.FunctionDef):

         if isinstance(node, ast.ClassDef):
            dictClass = {}
            sClassName = f"{node.name}"
            # print(f"* class : '{sClassName}'")
            dictClass['sClassName'] = sClassName
            sClassDocString = ast.get_docstring(node)
            dictClass['sClassDocString'] = sClassDocString

            listofdictMethods = []

            for subnode in node.body:
               if isinstance(subnode, ast.FunctionDef):
                  sMethodName = f"{subnode.name}"
                  if not sMethodName.startswith('_'):           # currently no private methods; TODO: make this a configuration or command line parameter
                     dictMethod = {}
                     # print(f"* method : '{sMethodName}'")
                     dictMethod['sMethodName'] = sMethodName
                     sMethodDocString = ast.get_docstring(subnode)
                     dictMethod['sMethodDocString'] = sMethodDocString
                     listofdictMethods.append(dictMethod)
                  # eof if not sMethodName.startswith('_'):
               # eof if isinstance(subnode, ast.FunctionDef):
            # eof for subnode in node.body:

            dictClass['listofdictMethods'] = listofdictMethods

            listofdictClasses.append(dictClass)
         # eof if isinstance(node, ast.ClassDef):

      # eof for node in astModule.body:

      if ( (len(listofdictFunctions) == 0) and (len(listofdictClasses) == 0) ):
         dictContent = None # nothing relevant found inside this file
      else:
         dictContent['listofdictFunctions'] = listofdictFunctions
         dictContent['listofdictClasses'] = listofdictClasses

      bSuccess = True
      sResult  = "Done"

      return dictContent, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

   # eof def ParseSourceFile(self, sFile=None):

# eof class CSourceParser():

# --------------------------------------------------------------------------------------------------------------

