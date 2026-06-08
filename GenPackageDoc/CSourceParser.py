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
# 05.06.2026
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

   def __is_gpd_decorated(self, node):
       """
       Checks if a function/method has the @genpackagedoc decorator.

       Parameters:
       - node: ast.FunctionDef or ast.AsyncFunctionDef

       Returns:
       - dict: {
           'is_gpd': bool,           # True if @genpackagedoc decorator is present
           'is_ui': bool or None,    # is_ui value from is_ui=... parameter
           'tags': list              # List of tags from tags=[...] parameter
         }
       """
       # TODO: check if "result['is_gpd']" is really required
       result = {
           'is_gpd': False,
           'is_ui': None,
           'tags': []
       }

       if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
           return result

       for decorator in node.decorator_list:
           # Case 1: @genpackagedoc (simple name, without parameters)
           if isinstance(decorator, ast.Name) and decorator.id == 'genpackagedoc':
               result['is_gpd'] = True
               return result

           # Case 2: @genpackagedoc() or @genpackagedoc(is_ui=..., tags=[...])
           if isinstance(decorator, ast.Call):
               # Check if func is 'genpackagedoc'
               if isinstance(decorator.func, ast.Name) and decorator.func.id == 'genpackagedoc':
                   result['is_gpd'] = True
                   # Extract 'is_ui' and 'tags' keyword arguments
                   for keyword_arg in decorator.keywords:
                       if keyword_arg.arg == 'is_ui':
                           # Extract the is_ui boolean value
                           if isinstance(keyword_arg.value, ast.Constant):
                               result['is_ui'] = keyword_arg.value.value
                           elif isinstance(keyword_arg.value, ast.NameConstant):  # Python < 3.8 compatibility
                               result['is_ui'] = keyword_arg.value.value

                       elif keyword_arg.arg == 'tags':
                           # Extract tags list
                           result['tags'] = self._extract_list(keyword_arg.value)

                   return result

               # Check if func is fully qualified (e.g., 'module.genpackagedoc')
               if isinstance(decorator.func, ast.Attribute):
                   # Walk through the attribute chain
                   parts = []
                   current = decorator.func
                   while isinstance(current, ast.Attribute):
                       parts.insert(0, current.attr)
                       current = current.value
                   if isinstance(current, ast.Name):
                       parts.insert(0, current.id)

                   # Check if it ends with 'genpackagedoc' (flexible for different module paths)
                   if parts[-1] == 'genpackagedoc':
                       result['is_gpd'] = True
                       # Extract 'is_ui' and 'tags' keyword arguments
                       for keyword_arg in decorator.keywords:
                           if keyword_arg.arg == 'is_ui':
                               if isinstance(keyword_arg.value, ast.Constant):
                                   result['is_ui'] = keyword_arg.value.value
                               elif isinstance(keyword_arg.value, ast.NameConstant):
                                   result['is_ui'] = keyword_arg.value.value

                           elif keyword_arg.arg == 'tags':
                               result['tags'] = self._extract_list(keyword_arg.value)

                       return result

           # Case 3: @module.genpackagedoc (attribute chain without call)
           if isinstance(decorator, ast.Attribute):
               parts = []
               current = decorator
               while isinstance(current, ast.Attribute):
                   parts.insert(0, current.attr)
                   current = current.value
               if isinstance(current, ast.Name):
                   parts.insert(0, current.id)

               # Check if it ends with 'genpackagedoc'
               if parts[-1] == 'genpackagedoc':
                   result['is_gpd'] = True
                   return result

       return result

   # eof def __is_gpd_decorated(self, node):


   def __is_robot_decorated(self, node):
       """
Checks if a function/method has the @keyword decorator (Robot Framework).

Parameters:
- node: ast.FunctionDef or ast.AsyncFunctionDef

Returns:
- dict: {
    'is_keyword': bool,         # True if @keyword decorator is present
    'alias_name': str or None,  # Alias name from name='...' parameter
    'tags': list                # List of tags from tags=[...] parameter
  }
       """
       result = {
           'is_keyword': False,
           'alias_name': None,
           'tags': []
       }

       if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
           return result

       for decorator in node.decorator_list:
           # Case 1: @keyword (simple name)
           if isinstance(decorator, ast.Name) and decorator.id == 'keyword':
               result['is_keyword'] = True
               return result

           # Case 2: @keyword() or @keyword(name='...', tags=[...])
           if isinstance(decorator, ast.Call):
               # Check if func is 'keyword'
               if isinstance(decorator.func, ast.Name) and decorator.func.id == 'keyword':
                   result['is_keyword'] = True
                   # Extract 'name' and 'tags' keyword arguments
                   for keyword_arg in decorator.keywords:
                       if keyword_arg.arg == 'name':
                           # Extract the name value
                           if isinstance(keyword_arg.value, ast.Constant):
                               result['alias_name'] = keyword_arg.value.value
                           elif isinstance(keyword_arg.value, ast.Str):  # Python < 3.8 compatibility
                               result['alias_name'] = keyword_arg.value.s

                       elif keyword_arg.arg == 'tags':
                           # Extract tags list
                           result['tags'] = self._extract_list(keyword_arg.value)

                   return result

               # Check if func is 'robot.api.deco.keyword' (full qualified)
               if isinstance(decorator.func, ast.Attribute):
                   # Walk through the attribute chain
                   parts = []
                   current = decorator.func
                   while isinstance(current, ast.Attribute):
                       parts.insert(0, current.attr)
                       current = current.value
                   if isinstance(current, ast.Name):
                       parts.insert(0, current.id)

                   # Check if it matches 'robot.api.deco.keyword'
                   if parts == ['robot', 'api', 'deco', 'keyword']:
                       result['is_keyword'] = True
                       # Extract 'name' and 'tags' keyword arguments
                       for keyword_arg in decorator.keywords:
                           if keyword_arg.arg == 'name':
                               if isinstance(keyword_arg.value, ast.Constant):
                                   result['alias_name'] = keyword_arg.value.value
                               elif isinstance(keyword_arg.value, ast.Str):
                                   result['alias_name'] = keyword_arg.value.s

                           elif keyword_arg.arg == 'tags':
                               result['tags'] = self._extract_list(keyword_arg.value)

                       return result

           # Case 3: @robot.api.deco.keyword (attribute chain without call)
           if isinstance(decorator, ast.Attribute):
               parts = []
               current = decorator
               while isinstance(current, ast.Attribute):
                   parts.insert(0, current.attr)
                   current = current.value
               if isinstance(current, ast.Name):
                   parts.insert(0, current.id)

               if parts == ['robot', 'api', 'deco', 'keyword']:
                   result['is_keyword'] = True
                   return result

       return result

   # eof def __is_robot_decorated(self, node):


   def _extract_list(self, list_node):
       """
Extracts string values from an ast.List node.

Parameters:
- list_node: ast.List or ast.Constant

Returns:
- list of str
       """
       tags = []

       if isinstance(list_node, ast.List):
           for element in list_node.elts:
               if isinstance(element, ast.Constant):
                   tags.append(element.value)
               elif isinstance(element, ast.Str):  # Python < 3.8 compatibility
                   tags.append(element.s)

       return tags

   #eof def _extract_list(self, list_node):


   def _format_node_features(self, name=None,
                                   alias_name=None,
                                   is_documented=None,
                                   is_async=None,
                                   is_private=None,
                                   is_keyword=None,
                                   is_ui=None,
                                   tags=None,
                                   take_it=None):
       """
Formats all node features to a single string.

Parameters:
- node features

Returns:
- formatted string to print the node features to screen
       """
       node_feature_info = f"  > Parsed : '{name}'"
       if alias_name:
          node_feature_info = f"{node_feature_info} (alias: '{alias_name}')"
       if is_documented:
          node_feature_info = f"{node_feature_info} / is documented"
       else:
          node_feature_info = f"{node_feature_info} / is not documented"
       if is_async:
          node_feature_info = f"{node_feature_info} / is async"
       if is_private:
          node_feature_info = f"{node_feature_info} / is private"
       if is_keyword:
          node_feature_info = f"{node_feature_info} / is keyword"
       if is_ui:
          node_feature_info = f"{node_feature_info} / is user interface"
       if tags:
          node_feature_info = f"{node_feature_info} / tagged with: '{tags}'"
       if take_it:
          node_feature_info = f"{node_feature_info} / take it"
       else:
          node_feature_info = f"{node_feature_info} / skip"
       return node_feature_info
   # eof def _format_node_features(self, name=None,


   def ParseSourceFile(self, source_file=None, include_private=False, include_undocumented=True):
      """
The method ``ParseSourceFile`` parses the content of a Python module.

**Arguments:**

* ``source_file``

  / *Condition*: required / *Type*: str /

  Path and name of a single Python module.

* ``include_private``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  If ``False``: private methods are skipped, otherwise they are included in documentation.

* ``include_undocumented``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  If ``True``: also classes and methods without docstring are listed in the documentation (together with a hint that information is not available),
  otherwise they are skipped.

**Returns:**

* ``dictContent``

  / *Type*: dict /

  A dictionary containing all the information parsed out of ``source_file``.

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method ``sMethod`` was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method ``sMethod``.
      """

      sMethod = "CSourceParser.ParseSourceFile"

      dictContent = {}

      if source_file is None:
         bSuccess = None
         sResult  = "'source_file' is None"
         return dictContent, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      if os.path.isfile(source_file) is False:
         bSuccess = False
         sResult  = f"File '{source_file}' does not exist"
         return dictContent, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      oSourceFile = CFile(source_file)
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
#QWERT
            function_name = f"{node.name}"
            function_docstring = ast.get_docstring(node)
            # detect node features
            is_private = False
            if function_name.startswith('_'):
               is_private = True
            is_documented = False
            if function_docstring:
               is_documented = True
            is_async = False
            if isinstance(node, ast.AsyncFunctionDef):
               is_async = True

            # decide whether to add the node to documentation or not
            take_it = True
            if not include_private:
               if is_private:
                  take_it = False
            if not is_documented:
               if not include_undocumented:
                  take_it = False

            # Compute further node features
            # 1. Robot Framework keyword decorator
            node_features_robot = self.__is_robot_decorated(node)
            alias_name = node_features_robot.get('alias_name')
            is_keyword = node_features_robot.get('is_keyword')
            robot_tags = node_features_robot.get('tags', [])
            # 2. GenPackageDoc documentation decorator
            node_features_gpd = self.__is_gpd_decorated(node)
            is_ui    = node_features_gpd.get('is_ui')
            gpd_tags = node_features_gpd.get('tags', [])
            # join tags and remove duplicates
            tags = list(dict.fromkeys(robot_tags + gpd_tags))

            node_feature_info = self._format_node_features(function_name,
                                                           alias_name,
                                                           is_documented,
                                                           is_async,
                                                           is_private,
                                                           is_keyword,
                                                           is_ui,
                                                           tags,
                                                           take_it)
            print(node_feature_info)

            if take_it is True:
               dictFunction = {}
               dictFunction['function_name']      = function_name
               dictFunction['alias_name']         = alias_name
               dictFunction['is_async']           = is_async
               dictFunction['is_keyword']         = is_keyword
               dictFunction['is_ui']              = is_ui
               dictFunction['tags']               = tags
               dictFunction['function_docstring'] = function_docstring
               listofdictFunctions.append(dictFunction)

         # eof if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

         if isinstance(node, ast.ClassDef):
            dictClass = {}
            dictClass['class_name']      = f"{node.name}"
            dictClass['class_docstring'] = ast.get_docstring(node)

            listofdictMethods = []

            for subnode in node.body:
               if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
#QWERT
                  method_name      = f"{subnode.name}"
                  method_docstring = ast.get_docstring(subnode)
                  # detect node features
                  is_private = False
                  if method_name.startswith('_'):
                     is_private = True
                  is_documented = False
                  if method_docstring:
                     is_documented = True
                  is_async = False
                  if isinstance(subnode, ast.AsyncFunctionDef):
                     is_async = True

                  # decide whether to add the subnode to documentation or not
                  take_it = True
                  if not include_private:
                     if is_private:
                        take_it = False
                  if not is_documented:
                     if not include_undocumented:
                        take_it = False

                  # Compute further subnode features
                  # 1. Robot Framework keyword decorator
                  node_features_robot = self.__is_robot_decorated(subnode)
                  alias_name = node_features_robot.get('alias_name')
                  is_keyword = node_features_robot.get('is_keyword')
                  robot_tags = node_features_robot.get('tags', [])
                  # 2. GenPackageDoc documentation decorator
                  node_features_gpd = self.__is_gpd_decorated(subnode)
                  is_ui    = node_features_gpd.get('is_ui')
                  gpd_tags = node_features_gpd.get('tags', [])
                  # join tags and remove duplicates
                  tags = list(dict.fromkeys(robot_tags + gpd_tags))

                  node_feature_info = self._format_node_features(method_name,
                                                                 alias_name,
                                                                 is_documented,
                                                                 is_async,
                                                                 is_private,
                                                                 is_keyword,
                                                                 is_ui,
                                                                 tags,
                                                                 take_it)
                  print(node_feature_info)

                  if take_it is True:
                     # store all node features
                     dictMethod = {}
                     dictMethod['method_name']      = method_name
                     dictMethod['alias_name']       = alias_name
                     dictMethod['is_async']         = is_async
                     dictMethod['is_keyword']       = is_keyword
                     dictMethod['is_ui']            = is_ui
                     dictMethod['tags']             = tags
                     dictMethod['method_docstring'] = method_docstring
                     listofdictMethods.append(dictMethod)
                  # eof if take_it is True:
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

   # eof def ParseSourceFile(self, source_file=None, include_private=False, include_undocumented=True):

# eof class CSourceParser():

# --------------------------------------------------------------------------------------------------------------

