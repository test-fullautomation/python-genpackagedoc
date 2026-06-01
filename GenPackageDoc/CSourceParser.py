# **************************************************************************************************************
#
#  Copyright 2020-2026 Robert Bosch GmbH
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
# XC-HWP/ESW3-Queckenstedt
#
# 29.05.2026
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing all methods to parse the documentation content of Python source files.
"""

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
The ``CSourceParser`` class provides a method to parse the functions, classes and their methods
together with the corresponding docstrings out of Python modules. The docstrings have to be written in rst syntax.
   """

   def __is_user_interface_node(self, node: ast.AST) -> bool:
       """
Checks whether an AST node is decorated with @is_user_interface.

Handles all common decorator forms:
  - @is_user_interface          (simple name)
  - @module.is_user_interface   (attribute access)
  - @is_user_interface()        (call without arguments)
  - @module.is_user_interface() (call on attribute)

Note: This is a static code check via AST. The attribute set by the
decorator does not yet exist at analysis time, so we inspect the
decorator node itself instead of checking the attribute value.

**Arguments:**

* ``node``

  / *Condition*: required / *Type*: AST node /

  An AST node that has a decorator_list (e.g. ``ast.ClassDef``,
  ``ast.FunctionDef``, ``ast.AsyncFunctionDef``).

**Returns:**

``True`` if the node carries the @is_user_interface decorator, ``False`` otherwise.
       """
       TARGET = 'is_user_interface'

       for decorator in node.decorator_list:
           # @is_user_interface
           if hasattr(decorator, 'id') and decorator.id == TARGET:
               return True
           # @module.is_user_interface
           if hasattr(decorator, 'attr') and decorator.attr == TARGET:
               return True
           # @is_user_interface() or @module.is_user_interface()
           if isinstance(decorator, ast.Call):
               func = decorator.func
               if (hasattr(func, 'id') and func.id == TARGET) or \
                  (hasattr(func, 'attr') and func.attr == TARGET):
                   return True
       return False


   def ParseSourceFile(self, sFile=None, bIncludePrivate=False, bIncludeUndocumented=True):
      """
The method ``ParseSourceFile`` parses the content of a Python module.

**Arguments:**

* ``sFile``

  / *Condition*: required / *Type*: str /

  Path and name of a single Python module.

* ``bIncludePrivate`` (currently not active, is ``False``)

  / *Condition*: optional / *Type*: bool / *Default*: False /

  If ``False``: private methods are skipped, otherwise they are included in documentation.

* ``bIncludeUndocumented``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  If ``True``: also classes and methods without docstring are listed in the documentation (together with a hint that information is not available),
  otherwise they are skipped.

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

      sMethod = "CSourceParser.ParseSourceFile"

      dictContent = {}

      if sFile is None:
         bSuccess = None
         sResult  = "sFile is None"
         return dictContent, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      if os.path.isfile(sFile) is False:
         bSuccess = False
         sResult  = f"File '{sFile}' does not exist"
         return dictContent, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      oSourceFile = CFile(sFile)
      listLines, bSuccess, sResult = oSourceFile.ReadLines()
      del oSourceFile
      sContent = "\n".join(listLines)

      astModule = ast.parse(sContent)

      listofdictFunctions = []
      listofdictClasses   = []
      sFileDescription    = None

      bIsFirstExpressionConstant = True

      for node in astModule.body:
         if isinstance(node, ast.Expr):
            if bIsFirstExpressionConstant is True:
               oExpression = node.value
               if isinstance(oExpression, ast.Constant):
                  bIsFirstExpressionConstant = False
                  sFileDescription = oExpression.value

         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sFunctionName = f"{node.name}"
            sFunctionDocString = ast.get_docstring(node)

            bTakeIt = True
            if bIncludePrivate is False:
               if sFunctionName.startswith('_'):
                  # is private
                  bTakeIt = False
            # eof if bIncludePrivate is False:
            if bIncludeUndocumented is False:
               if sFunctionDocString is None:
                  # is undocumented
                  bTakeIt = False
            # eof if bIncludeUndocumented is False:

            if isinstance(node, ast.AsyncFunctionDef):
               sFunctionName = f"async {sFunctionName}"

            if bTakeIt is True:
               dictFunction = {}
               dictFunction['sFunctionName']      = sFunctionName
               dictFunction['is_ui']              = self.__is_user_interface_node(node)
               dictFunction['sFunctionDocString'] = sFunctionDocString
               listofdictFunctions.append(dictFunction)
            # eof if bTakeIt is True:
         # eof if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

         if isinstance(node, ast.ClassDef):
            # is class => bIncludeUndocumented has no relevance
            sClassName = f"{node.name}"
            sClassDocString = ast.get_docstring(node)
            dictClass = {}
            dictClass['sClassName'] = sClassName
            dictClass['sClassDocString'] = sClassDocString

            listofdictMethods = []

            for subnode in node.body:
               if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                  sMethodName = f"{subnode.name}"
                  sMethodDocString = ast.get_docstring(subnode)

                  bTakeIt = True
                  if bIncludePrivate is False:
                     if sMethodName.startswith('_'):
                        # is private
                        bTakeIt = False
                  # eof if bIncludePrivate is False:
                  if bIncludeUndocumented is False:
                     if sMethodDocString is None:
                        # is undocumented
                        bTakeIt = False
                  # eof if bIncludeUndocumented is False:

                  if isinstance(subnode, ast.AsyncFunctionDef):
                     sMethodName = f"async {sMethodName}"

                  # is keyword?
                  bIsKeyword = False
                  for decorator in subnode.decorator_list:
                     if hasattr(decorator, 'id'):
                        if decorator.id == "keyword":
                           bIsKeyword = True
                           break

                  if bTakeIt is True:
                     dictMethod = {}
                     dictMethod['sMethodName']      = sMethodName
                     dictMethod['bIsKeyword']       = bIsKeyword
                     dictMethod['is_ui']            = self.__is_user_interface_node(subnode)
                     dictMethod['sMethodDocString'] = sMethodDocString
                     listofdictMethods.append(dictMethod)
                  # eof if bTakeIt is True:
               # eof if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # eof for subnode in node.body:

            dictClass['listofdictMethods'] = listofdictMethods

            listofdictClasses.append(dictClass)
         # eof if isinstance(node, ast.ClassDef):

      # eof for node in astModule.body:

      if ( (len(listofdictFunctions) == 0) and (len(listofdictClasses) == 0) and (sFileDescription is None) ):
         dictContent = None # nothing relevant found inside this file
      else:
         dictContent['listofdictFunctions'] = listofdictFunctions
         dictContent['listofdictClasses']   = listofdictClasses
         dictContent['sFileDescription']    = sFileDescription

      bSuccess = True
      sResult  = "Done"

      return dictContent, bSuccess, sResult

   # eof def ParseSourceFile(self, sFile=None, bIncludePrivate=False, bIncludeUndocumented=True):

# eof class CSourceParser():

# --------------------------------------------------------------------------------------------------------------

