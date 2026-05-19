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
# CDocBuilder.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 19.05.2026
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, time, shlex, subprocess, platform, shutil, re, json
import colorama as col

from docutils.core import publish_parts
from docutils.core import publish_file  # old, replaced by 'publish_string'
from docutils.core import publish_string
from docutils import nodes

from GenPackageDoc.CSourceParser import CSourceParser
from GenPackageDoc.CPatterns import CPatterns

from GenPackageDoc.markdown_extensions import CustomLaTeXWriter
from GenPackageDoc.markdown_extensions import CustomHTMLWriter

from GenPackageDoc import html_index_file_pattern

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Folder.CFolder import CFolder
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBW = col.Style.BRIGHT + col.Fore.WHITE

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

"""
.. highlight::

   CDocBuilder is a Python module containing all methods to generate files in TEX and HTML format.
"""

# --------------------------------------------------------------------------------------------------------------
#TM***

class CDocBuilder():
   """
:pcode:`CDocBuilder` is the main class to build TEX sources out of docstrings of Python modules and separate text files in reST format.

This depends on a JSON configuration file, provided by a :pcode:`oPackageDocConfig` object (that includes the Repository configuration).

Method to execute: :pcode:`Build()`
   """

   def __init__(self, oPackageDocConfig=None):
      """
Constructor of class :pcode:`CDocBuilder`.

* :pcode:`oPackageDocConfig`

  / *Condition*: required / *Type*: CPackageDocConfig() /

  **GenPackageDoc** configuration containing static and dynamic configuration values.
      """

      sMethod = "CDocBuilder.__init__"

      if oPackageDocConfig is None:
         bSuccess = None
         sResult  = "oPackageDocConfig is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      self.__dictPackageDocConfig = oPackageDocConfig.GetConfig()

      # -- syntax extensions
      # Short command '/NL' used in reST, but to avoid slashes in RST content, the short command is replaced by a longer string.
      # Later these longer strings are replaced by corresponding LaTeX specific commands and HTML specific tags.
      # It should be investigated if slashes would harm reST content. Maybe these placeholders are not necessary.
      self.__dictPlaceholder = {}
      self.__dictPlaceholder['/NL']   = ("!N!E!W!L!I!N!E!")
      self.__dictPlaceholder['/NP']   = ("!N!E!W!P!A!G!E!")
      self.__dictPlaceholder['/VS']   = ("!V!S!P!A!C!E!1!")
      self.__dictPlaceholder['/VVS']  = ("!V!S!P!A!C!E!2!")
      self.__dictPlaceholder['/VVVS'] = ("!V!S!P!A!C!E!3!")
      self.__dictPlaceholder['/BS']   = ("!B!A!C!K!S!L!A!S!H!")
      self.__dictPlaceholder['/IBS']  = ("!I!N!L!I!N!E!B!S!L!A!S!H!")
      self.__dictPlaceholder['/HS']   = ("!S!T!A!N!D!A!R!D!H!S!P!A!C!E!")
      self.__dictPlaceholder['/IHS']  = ("!I!N!L!I!N!E!H!S!P!A!C!E!")
      self.__dictPlaceholder['/*IHS'] = ("!I!N!L!I!N!E!M!H!S!P!A!C!E!")
      self.__dictPlaceholder['/US']   = ("!U!N!D!E!R!S!C!O!R!E!")


      # Python modules may contain methods with same name in several classes. Different Python modules may contain classes or functions
      # with the same name. GenPackageDoc parses the content of Python modules. The outcome is that for every Python module GenPackageDoc
      # creates a temporary reST file (because the content of the docstrings also has to be written in reST format).
      # This reST file is converted to LaTeX format by docutils. To support linking docutils adds labels to every
      # heading (that are the names of classes and methods) automatically. The names of the labels are the headings - this means: names of classes
      # and methods are used as label. In case of the names of classes and methods are not unique over all files, also the labels will
      # not be unique. The conversion from reST format to LaTeX format happens for every Python module separately (and therefore the scope
      # is not known). At the end all LaTeX files are put together to one LaTeX file. Outcome: In case of ambiguous labels the LaTeX compiler
      # throws a "multiply-defined labels" warning.
      #
      # To avoid these warnings every headline is replaced by a string containing the full scope (starting with the name of the package folder).
      # This is written to the temporary reST file. Docutils use now these full scope strings for labels when converting the reST code into LaTeX code.
      # Finally by __PostprocessRST within every 'section' and 'subsection' command in the LaTeX code the full scope string (that must be unique)
      # is replaced by the original headline (that might be ambiguous). The full scope strings together with their original headlines are stored
      # in 'self.__dictScopes'.

      self.__dictScopes = {}
      self.__listHTMLFiles = []

   def __del__(self):
      pass


   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __ConvertToScopeFormat(self, sString=""):
      """
Converts a string to 'scope' format.
The scope is a string containing the full import path
(from package folder to method name).
This is used to resolve ambiguous Python file names in different subfolders.
      """
      sString = sString.replace(' ', '-')
      sString = sString.replace('_', '-')
      sString = sString.replace('.', '-')
      sString = sString.replace('/', '-')
      sString = sString.lower()
      return sString

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __filename_to_html_id(self, filename: str) -> str:
      """
Converts file names to strings that can be used as id inside HTML content.
This is used to generate the index.html files of the documentation
in HTML format.
      """
      # Remove invalid characters (everything except letters, digits, -, _, :)
      # Replace spaces and dots with underscores
      id_str = re.sub(r'[\s\.]+', '_', filename)
      # Remove all characters not allowed for id
      id_str = re.sub(r'[^a-zA-Z0-9\-\_\:\.]', '', id_str)
      # id must not start with a digit
      if id_str and id_str[0].isdigit():
         id_str = '_' + id_str
      return id_str

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __replace_in_array(self, arr, search, replace):
       """
Returns a new array where every occurrence of 'search' in any element is replaced by 'replace'.
       """
       new_arr = []
       for elem in arr:
           if search in elem:
               new_elem = elem.replace(search, replace)
               new_arr.append(new_elem)
           else:
               new_arr.append(elem)
       return new_arr

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __GetModulesList(self, sRootPath=None):
      """
Computes a list of all Python modules found recursively within ``sRootPath``.
      """

      sMethod = "CDocBuilder.__GetModulesList"

      if sRootPath is None:
         bSuccess = None
         sResult  = "sRootPath is None"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      tupleSubfoldersToExclude = (".git", "__pycache__") # TODO: make this a configuration parameter

      bSuccess = None
      sResult  = None

      listModules = []
      for sLocalRootPath, listFolderNames, listFileNames in os.walk(sRootPath):
         sFolderName = os.path.basename(sLocalRootPath)
         if sFolderName not in tupleSubfoldersToExclude:
            for sFileName in listFileNames:
               if sFileName.lower().endswith('.py'):
                  sFile = CString.NormalizePath(os.path.join(sLocalRootPath, sFileName))
                  listModules.append(sFile)
      # eof for sLocalRootPath, listFolderNames, listFileNames in os.walk(sRootPath):

      listModules.sort()
      nNrOfModules = len(listModules)

      bSuccess = True
      sResult  = f"Found {nNrOfModules} Python modules within '{sRootPath}'"

      return listModules, bSuccess, sResult

   # eof __GetModulesList(self, sRootPath=None):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __ResolvePlaceholders(self, listLines=[]):
      """
Resolves placeholders used in packagedoc configuration (JSON file)
      """

      sMethod = "CDocBuilder.__ResolvePlaceholders"

      bSuccess = None
      sResult  = None

      listLinesResolved = []

      dictRuntimeVariables = self.__dictPackageDocConfig['dictRuntimeVariables']
      for sLine in listLines:
         sLineResolved = sLine
         for key, value in dictRuntimeVariables.items():
            if type(value) == str:
               sLineResolved = sLineResolved.replace(f"###{key}###", value)
         listLinesResolved.append(sLineResolved)

      bSuccess = True
      sResult  = "Placeholders resolved"

      return listLinesResolved, bSuccess, sResult

   # eof def __ResolvePlaceholders(self, listLines=[]):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __PostprocessRST(self, listLinesRST=[]):
      """
Postprocessing of reST content after reading from reST file or parsing from docstrings and after replacement
of placeholders. This covers e.g. the computation of syntax extensions.

Extensions of the syntax of reST (newline, newpage and vspace) will be masked (by replacement strings, that do no contain
characters belonging to syntax of reST, LaTeX and HTML.
      """

      listLinesProcessed = []
      for sLine in listLinesRST:
         sLine = sLine.rstrip()
         sLine = sLine.replace('/NL'   , self.__dictPlaceholder['/NL'])   # newline
         sLine = sLine.replace('/NP'   , self.__dictPlaceholder['/NP'])   # newpage
         sLine = sLine.replace('/VS'   , self.__dictPlaceholder['/VS'])   # vertical space 1
         sLine = sLine.replace('/VVS'  , self.__dictPlaceholder['/VVS'])  # vertical space 2
         sLine = sLine.replace('/VVVS' , self.__dictPlaceholder['/VVVS']) # vertical space 3
         sLine = sLine.replace('/BS'   , self.__dictPlaceholder['/BS'])   # backslash
         sLine = sLine.replace('/IBS'  , self.__dictPlaceholder['/IBS'])  # inline backslash
         sLine = sLine.replace('/HS'   , self.__dictPlaceholder['/HS'])   # horizontal space (blank)
         sLine = sLine.replace('/IHS'  , self.__dictPlaceholder['/IHS'])  # inline horizontal space (blank)
         sLine = sLine.replace('/*IHS' , self.__dictPlaceholder['/*IHS']) # inline horizontal space (blank), masked for documentation purposes!!
         sLine = sLine.replace('/US'   , self.__dictPlaceholder['/US'])   # underscore (mapping because part of reST syntax)
         listLinesProcessed.append(sLine)

      return listLinesProcessed

   # eof def __PostprocessRST(self, listLines=[]):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __PostprocessTEX(self, listLinesTEX=[]):
      """
Postprocessing of TEX content. This covers e.g. the computation of reST syntax extensions and also
the recovery of the original headlines out of the intermediately used full scope strings.

The masking of newline, newpage and vspace (reST syntax extensions) are replaced by the corresponding LaTeX commands.
      """

      listLinesProcessed = []

      for sLine in listLinesTEX:
         # certain syntax extensions
         sLine = sLine.replace(self.__dictPlaceholder['/NL']   , r"\newline")
         sLine = sLine.replace(self.__dictPlaceholder['/NP']   , r"\newpage")
         sLine = sLine.replace(self.__dictPlaceholder['/VS']   , "\n" + r"\vspace{1ex}" + "\n")
         sLine = sLine.replace(self.__dictPlaceholder['/VVS']  , "\n" + r"\vspace{2ex}" + "\n")
         sLine = sLine.replace(self.__dictPlaceholder['/VVVS'] , "\n" + r"\vspace{3ex}" + "\n")
         sLine = sLine.replace(self.__dictPlaceholder['/BS']   , r"\textbackslash{}")
         sLine = sLine.replace(self.__dictPlaceholder['/IBS']  , "\\\\")
         sLine = sLine.replace(self.__dictPlaceholder['/HS']   , r"{\ttfamily\hspace{0.6em}}")
         sLine = sLine.replace(self.__dictPlaceholder['/IHS']  , r"\ ") # computed by 'literate' in sty file
         sLine = sLine.replace(self.__dictPlaceholder['/*IHS'] , "/IHS")
         sLine = sLine.replace(self.__dictPlaceholder['/US']   , r"\_")

         # To handle ambiguous names of methods, classes and methods, the original names (= document headlines)
         # are replaced by the full scopes. We will not run into trouble any more when docutils create labels out of the headlines
         # when converting the reST source code to LaTeX code.
         # Here we have to undo this replacement: We replace the full scope string in every section and subsection by the original headline.

         # Pandoc adds ligatures in some cases: '--' -> '-\/-'. We do not need them. They have to be removed before we search for sKey,
         # Also the docutils add characters: '--' -> '-{}-'. We do not need them. They have to be removed before we search for sKey,
         # because sKey does not contain these ligatures.
         if "section{" in sLine:
            sLine = sLine.replace(r'\/', '') # undo Pandoc modification (outdated, because Pandoc is not used any more)
            sLine = sLine.replace(r'{}', '') # undo docutils modification

         # The following replaces are adapted to the autogenerated LaTeX content.
         # * full-scope-headlines will be replaced by the original headline
         # * full-scope-headlines will be used as label for the headline
         for sKey in self.__dictScopes:
            # sKey is full scope string
            # value of sKey is original headline (= original name of function, class or method)
            sSearch  = "section{" + sKey + "%" # this includes 'subsection'
            sReplace = "section{" + self.__dictScopes[sKey] + "%"
            sReplace = sReplace.replace('_', r'\_') # LaTeX requires this masking
            sLine = sLine.replace(sSearch, sReplace)

         listLinesProcessed.append(sLine)

      return listLinesProcessed

   # eof def __PostprocessTEX(self, listLinesTEX=[]):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __PostprocessHTML(self, listLinesHTML=[]):
      """
Postprocessing of HTML content. This covers e.g. the computation of reST syntax extensions and also
the recovery of the original headlines out of the intermediately used full scope strings.

The masking of newline, newpage and vspace (reST syntax extensions) are replaced by the corresponding HTML tags.
      """

      listLinesProcessed = []

      for sLine in listLinesHTML:
         # certain syntax extensions
         sLine = sLine.replace(self.__dictPlaceholder['/NL']   , r"<br>")
         sLine = sLine.replace(self.__dictPlaceholder['/NP']   , r"")
         sLine = sLine.replace(self.__dictPlaceholder['/VS']   , "<span style=\"display:block; height:1ex;\"></span>")
         sLine = sLine.replace(self.__dictPlaceholder['/VVS']  , "<span style=\"display:block; height:2ex;\"></span>")
         sLine = sLine.replace(self.__dictPlaceholder['/VVVS'] , "<span style=\"display:block; height:3ex;\"></span>")
         sLine = sLine.replace(self.__dictPlaceholder['/BS']   , "\\")
         sLine = sLine.replace(self.__dictPlaceholder['/IBS']  , "\\")
         sLine = sLine.replace(self.__dictPlaceholder['/HS']   , "&nbsp;")
         sLine = sLine.replace(self.__dictPlaceholder['/IHS']  , "&nbsp;")
         sLine = sLine.replace(self.__dictPlaceholder['/*IHS'] , "/IHS")
         sLine = sLine.replace(self.__dictPlaceholder['/US']   , "_")

# >>> to be verified; most probably outdated:
# # # To handle ambiguous names of methods, classes and methods, the original names (= document headlines)
# # # are replaced by the full scopes. We will not run into trouble any more when docutils create labels out of the headlines
# # # when converting the reST source code to LaTeX code.
# # # Here we have to undo this replacement: We replace the full scope string in every section and subsection by the original headline.

# # # Pandoc adds ligatures in some cases: '--' -> '-\/-'. We do not need them. They have to be removed before we search for sKey,
# # # Also the docutils add characters: '--' -> '-{}-'. We do not need them. They have to be removed before we search for sKey,
# # # because sKey does not contain these ligatures.
# # if "section{" in sLine:
   # # sLine = sLine.replace(r'\/', '') # undo Pandoc modification (outdated, because Pandoc is not used any more)
   # # sLine = sLine.replace(r'{}', '') # undo docutils modification

         # The following replaces are adapted to the autogenerated HTML content.
         # * full-scope-headlines will be replaced by the original headline
         # TODO: * full-scope-headlines will be used as label for the headline
         #
         # <section id="genpackagedoc-cdocbuilder-cdocbuilder">       # full-scope-string will be kept as label
         # <h2>genpackagedoc-cdocbuilder-cdocbuilder</h2>             # full-scope-string will be replaced by actual name in headlines
         # <section id="genpackagedoc-cdocbuilder-cdocbuilder-build"> # full-scope-string will be kept as label
         # <h3>genpackagedoc-cdocbuilder-cdocbuilder-build</h3>       # full-scope-string will be replaced by actual name in headlines

         for sKey in self.__dictScopes:
            # sKey is full scope string
            # value of sKey is original headline (= original name of function, class or method)
            sSearch  = f">{sKey}</h"
            sReplace = f">{self.__dictScopes[sKey]}</h"
            sLine = sLine.replace(sSearch, sReplace)

         listLinesProcessed.append(sLine)

      return listLinesProcessed

   # eof def __PostprocessHTML(self, listLinesHTML=[]):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __CleanFolder(self, sFolder=None):
      """
Cleans a folder (to a avoid a mixture of current and previous results).
The meaning of clean is: *delete*, followed by *create*.
      """

      sMethod = "CDocBuilder.__CleanFolder"

      bSuccess = None
      sResult  = None

      if os.path.isdir(sFolder) is True:
         print(f"* Deleting folder '{sFolder}'")
         print()
         try:
            shutil.rmtree(sFolder)
         except Exception as ex:
            bSuccess = None
            sResult  = str(ex)
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      try:
         os.makedirs(sFolder)
      except Exception as ex:
         bSuccess = None
         sResult  = str(ex)
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      bSuccess = True
      sResult  = f"Folder '{sFolder}' cleaned"

      return bSuccess, sResult

   # eof def __CleanFolder(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __CopyPictures(self):
      """
Copies the pictures folder to the output folder (required to keep relative paths valid also in created tex files)
      """

      sMethod = "CDocBuilder.__CopyPictures"

      bSuccess = None
      sResult  = "UNKNOWN"

      sPicturesSourceDir = self.__dictPackageDocConfig['PICTURES']
      if sPicturesSourceDir is None:
         bSuccess = True
         sResult  = f"No pictures defined, nothing to copy"
      else:
         if os.path.isdir(sPicturesSourceDir) is True:
            # copy the pictures folder to output folder
            sDirName = os.path.basename(sPicturesSourceDir)
            sPicturesDestinationDir = f"{self.__dictPackageDocConfig['OUTPUT']}/{sDirName}"
            try:
               shutil.copytree(sPicturesSourceDir, sPicturesDestinationDir)
            except Exception as ex:
               bSuccess = None
               sResult  = str(ex)
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
            bSuccess = True
            sResult  = f"Pictures folder '{sPicturesSourceDir}' copied to build folder '{sPicturesDestinationDir}'"
         else:
            bSuccess = False
            sResult  = f"Pictures folder '{sPicturesSourceDir}' does not exist"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      # eof else - if sPicturesSourceDir is None:

      return bSuccess, sResult

   # eof def __CopyPictures(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __RenderDiagrams(self):
      """
Render all diagrams in 'DIAGRAMS' folder (with PlantUML). Diagram files are expected to have the extension '.puml'.
      """

      sMethod = "CDocBuilder.__RenderDiagrams"

      bSuccess = None
      sResult  = "UNKNOWN"

      sDiagramsSourceDir = self.__dictPackageDocConfig['DIAGRAMS']
      if sDiagramsSourceDir is None:
         bSuccess = True
         # message is irrelevant for users: sResult  = f"No diagrams folder configured in DIAGRAMS section of GenPackageDoc configuration; nothing to render"
         sResult = None
         return bSuccess, sResult
      else:
         if os.path.isdir(sDiagramsSourceDir) is True:
            # -- identify diagram files
            listDiagramFiles = []
            for sLocalRootPath, listFolderNames, listFileNames in os.walk(sDiagramsSourceDir):
               for sFileName in listFileNames:
                  if sFileName.endswith('.puml'):
                     sDiagramFile = CString.NormalizePath(os.path.join(sLocalRootPath, sFileName))
                     if sDiagramFile not in listDiagramFiles:
                        listDiagramFiles.append(sDiagramFile)
            # eof for ...

            nNrOfDiagramFiles = len(listDiagramFiles)
            if nNrOfDiagramFiles == 0:
               bSuccess = True
               sResult  = f"No diagram files found in '{sDiagramsSourceDir}'; nothing to render"
               return bSuccess, sResult

            # diagram files available in diagrams folder (DIAGRAMS), therefore we need JAVA and PLANT_UML
            # -- JAVA
            JAVA = self.__dictPackageDocConfig['JAVA']
            if JAVA is None:
               bSuccess = False
               sResult  = f"Java not configured in GenPackageDoc configuration; cannot render diagrams"
               return bSuccess, sResult
            if os.path.isfile(JAVA) is False:
               bSuccess = False
               sResult  = f"Java '{JAVA}' not found; check GenPackageDoc configuration; cannot render diagrams"
               return bSuccess, sResult
            # -- PLANT_UML
            PLANT_UML = self.__dictPackageDocConfig['PLANT_UML']
            if PLANT_UML is None:
               bSuccess = False
               sResult  = f"PlantUML not configured in GenPackageDoc configuration; cannot render diagrams"
               return bSuccess, sResult
            if os.path.isfile(PLANT_UML) is False:
               bSuccess = False
               sResult  = f"PlantUML '{PLANT_UML}' not found; check GenPackageDoc configuration; cannot render diagrams"
               return bSuccess, sResult

            print(COLBY + "Rendering diagrams ...")
            print()

            # -- render all diagrams
            nCntDiagramFiles = 0
            for sDiagramFile in listDiagramFiles:
               nCntDiagramFiles = nCntDiagramFiles + 1
               sInfo = f"* ({nCntDiagramFiles}/{nNrOfDiagramFiles}) : '{sDiagramFile}'"
               print(sInfo)
               print()
               listCmdLineParts = []
               listCmdLineParts.append(f"\"{JAVA}\"")
               listCmdLineParts.append(f"-jar")
               listCmdLineParts.append(f"\"{PLANT_UML}\"")
               listCmdLineParts.append(f"\"{sDiagramFile}\"")

               sCmdLine = " ".join(listCmdLineParts)
               # -- debug
               print("Now executing command line:\n" + sCmdLine)
               print()
               del listCmdLineParts
               listCmdLineParts = shlex.split(sCmdLine)

               try:
                  nReturn = subprocess.call(listCmdLineParts)
                  print(f"PlantUML returned {nReturn}")
                  print()
               except Exception as ex:
                  bSuccess = None
                  sResult  = str(ex)
                  return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            # eof for sDiagramFile in listDiagramFiles:

            bSuccess = True
            sResult  = f"{nCntDiagramFiles} diagrams within '{sDiagramsSourceDir}' rendered"
         else:
            bSuccess = False
            sResult  = f"Diagrams folder '{sDiagramsSourceDir}' does not exist"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      # eof else - if sDiagramsSourceDir is None:

      return bSuccess, sResult

   # eof def __RenderDiagrams(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __CopyDiagrams(self):
      """
Copies the diagrams folder to the output folder (required to keep relative paths valid also in created tex files)
      """

      sMethod = "CDocBuilder.__CopyDiagrams"

      bSuccess = None
      sResult  = "UNKNOWN"

      sDiagramsSourceDir = self.__dictPackageDocConfig['DIAGRAMS']
      if sDiagramsSourceDir is None:
         bSuccess = True
         sResult  = f"No diagrams defined, nothing to copy"
      else:
         if os.path.isdir(sDiagramsSourceDir) is True:
            # copy the diagrams folder to output folder
            sDirName = os.path.basename(sDiagramsSourceDir)
            sDiagramsDestinationDir = f"{self.__dictPackageDocConfig['OUTPUT']}/{sDirName}"
            try:
               shutil.copytree(sDiagramsSourceDir, sDiagramsDestinationDir)
            except Exception as ex:
               bSuccess = None
               sResult  = str(ex)
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
            bSuccess = True
            sResult  = f"Pictures folder '{sDiagramsSourceDir}' copied to build folder '{sDiagramsDestinationDir}'"
         else:
            bSuccess = False
            sResult  = f"Pictures folder '{sDiagramsSourceDir}' does not exist"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      # eof else - if sDiagramsSourceDir is None:

      return bSuccess, sResult

   # eof def __CopyDiagrams(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __GenDocPDF(self):
      """
Executes the LaTeX compiler to create the PDF file out of the generated source tex files
      """

      sMethod = "CDocBuilder.__GenDocPDF"

      bSuccess = None
      sResult  = None

      sPDFFileExpected = None

      # -- consider strictness regarding availability of LaTeX compiler
      sLaTeXInterpreter = self.__dictPackageDocConfig['LATEXINTERPRETER']
      if os.path.isfile(sLaTeXInterpreter) is False:
         bStrict = self.__dictPackageDocConfig['CONTROL']['STRICT']
         print()
         print(COLBR + f"Missing LaTeX compiler '{sLaTeXInterpreter}'!")
         print()
         if bStrict is True:
            bSuccess = False
            sResult  = f"Generating the documentation in PDF format not possible because of missing LaTeX compiler ('strict' mode)!"
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            bSuccess = True
            sResult  = f"Generating the documentation in PDF format not possible because of missing LaTeX compiler ('non strict' mode)!"
         return bSuccess, sResult

      sBuildFolder = self.__dictPackageDocConfig['OUTPUT']
      sMainTexFile = self.__dictPackageDocConfig['sMainTexFile']

      listCmdLineParts = []
      listCmdLineParts.append(f"\"{sLaTeXInterpreter}\"")
      listCmdLineParts.append(f"\"{sMainTexFile}\"")

      sCmdLine = " ".join(listCmdLineParts)
      del listCmdLineParts
      listCmdLineParts = shlex.split(sCmdLine)

      # -- debug
      sCmdLine = " ".join(listCmdLineParts)
      print("Now executing command line:\n" + sCmdLine)
      print()

      for nDummy in range(2): # call LaTeX compiler 2 times to get TOC and index lists updated properly
         cwd = os.getcwd() # we have to save cwd because later we have to change
         nReturn = ERROR
         try:
            os.chdir(sBuildFolder) # otherwise LaTeX compiler is not able to find files inside
            nReturn = subprocess.call(listCmdLineParts)
            print()
            print(f"LaTeX compiler returned {nReturn}")
            print()
            os.chdir(cwd) # restore original value
         except Exception as ex:
            os.chdir(cwd) # restore original value
            bSuccess = None
            sResult  = str(ex)
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         if nReturn != SUCCESS:
            bSuccess = False
            sResult  = f"LaTeX compiler not returned expected value {SUCCESS}"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      # eof for nDummy in range(2):

      # -- verify the outcome
      sPDFFileExpected = self.__dictPackageDocConfig['sPDFFileExpected']
      if os.path.isfile(sPDFFileExpected) is True:
         # expected PDF file found
         bSuccess = True
         sResult  = f"PDF file '{sPDFFileExpected}' generated"
         if self.__dictPackageDocConfig['PDFDEST'] is not None:
            # further destination defined => copy PDF from build folder to there
            sDestinationPDFFile = f"{self.__dictPackageDocConfig['PDFDEST']}/{self.__dictPackageDocConfig['sPDFFileName']}"
            oPDFFile = CFile(sPDFFileExpected)
            bSuccess, sResult = oPDFFile.CopyTo(sDestinationPDFFile, bOverwrite=True)
            del oPDFFile
            if bSuccess is True:
               # replacement for sResult with line breaks
               sResult = f"Documentation in PDF format:\n'{sDestinationPDFFile}'"
            else:
               sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
      else:
         bSuccess = False
         sResult  = f"Expected PDF file '{sPDFFileExpected}' not generated"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def __GenDocPDF(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __PrepareHTMLDoc(self):
      """
Copies HTML files (and corresponding stylesheehs) from build folder to the HTML destination folder.
Creates the corresponding index.html file also.
      """

      bSuccess = False
      sResult  = "UNKNOWN"

      # check if feature is configured
      html_dest = self.__dictPackageDocConfig.get('HTMLDEST') 
      if not html_dest:
         bSuccess = True
         sResult  = f"Documentation in HTML format not defined - skipping this step!"
         return bSuccess, sResult

      # check availability of output folder (= temporary build folder containing all build artefacts)
      html_source = self.__dictPackageDocConfig.get('OUTPUT')
      if not html_source:
         bSuccess = False
         sResult  = f"'OUTPUT' key not defined in configuration"
         return bSuccess, sResult
      if not os.path.exists(html_source):
         bSuccess = False
         sResult  = f"Output build folder containing the HTML documentation source files '{html_source}' does not exist!"
         return bSuccess, sResult

      # prepare additional output folders
      print(f"HTML documentation folder '{html_dest}'")
      print()

      bSuccess, sResult = self.__CleanFolder(html_dest)
      if not bSuccess:
         return bSuccess, sResult

      styles_dest = f"{html_dest}/styles"
      if not os.path.exists(styles_dest):
         os.makedirs(styles_dest)

      # copy HTML files from temporary output/build folder to final HTML folder
      for filename in os.listdir(html_source):
          if filename.lower().endswith('.html'):
              src = os.path.join(html_source, filename)
              dst = os.path.join(html_dest, filename)
              shutil.copy2(src, dst)
              print(f"* Copied: {src} -> {dst}")

      # copy also the CSS stylesheets to final HTML folder
      styles_source = f"{html_source}/styles"
      if not os.path.exists(styles_source):
         # This should not occur here, because steps before __PrepareHTMLDoc()
         # are responsible for creating this folder
         bSuccess = False
         sResult  = f"HTML styleshhets folder '{styles_source}' does not exist!"
         return bSuccess, sResult

      # copy CSS files
      for filename in os.listdir(styles_source):
          if filename.lower().endswith('.css'):
              src = os.path.join(styles_source, filename)
              dst = os.path.join(styles_dest, filename)
              shutil.copy2(src, dst)
              print(f"* Copied: {src} -> {dst}")

      # If a PICTURES folder is configured in the GenPackageDoc configuration, this folder
      # is copied to the OUTPUT folder (to make the pictures available by imports in LaTeX files
      # when the PDF file is created).
      # If a HTMLDEST folder is configured in the GenPackageDoc configuration, the pictures need
      # to be copied to the HTMLDEST folder too (to make the pictures available by imports in HTML files).
      # Same with DIAGRAMS folder.
      # Background: To keep the file structure organized, the PDF documentation and the HTML documentation
      # are stored in separate and independent folders. Both of them require the presence of all files
      # that are imported.

      # prepare output folder for pictures
      pictures_source = self.__dictPackageDocConfig['PICTURES']
      if pictures_source:
         if os.path.exists(pictures_source):
            pictures_folder_name = os.path.basename(pictures_source)
            pictures_dest = f"{html_dest}/{pictures_folder_name}"
            if not os.path.exists(pictures_dest):
               os.makedirs(pictures_dest)
            # copy pictures
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.pdf', '.eps', '.tif', '.tiff', '.webp')
            for filename in os.listdir(pictures_source):
                if filename.lower().endswith(image_extensions):
                    src = os.path.join(pictures_source, filename)
                    dst = os.path.join(pictures_dest, filename)
                    shutil.copy2(src, dst)
                    print(f"* Copied: {src} -> {dst}")

      # prepare output folder for diagrams
      diagrams_source = self.__dictPackageDocConfig['DIAGRAMS']
      if diagrams_source:
         if os.path.exists(diagrams_source):
            diagrams_folder_name = os.path.basename(diagrams_source)
            diagrams_dest = f"{html_dest}/{diagrams_folder_name}"
            if not os.path.exists(diagrams_dest):
               os.makedirs(diagrams_dest)
            # copy diagrams (also pictures, but placed in DIAGRAMS folder)
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.pdf', '.eps', '.tif', '.tiff', '.webp')
            for filename in os.listdir(diagrams_source):
                if filename.lower().endswith(image_extensions):
                    src = os.path.join(diagrams_source, filename)
                    dst = os.path.join(diagrams_dest, filename)
                    shutil.copy2(src, dst)
                    print(f"* Copied: {src} -> {dst}")

      # Prepare the file list within index.html.
      #  -Files originally in reST format, have extension .html.
      # - Interface files have extension .py.html.
      html_file_list_code = []
      prev_is_pyhtml = None
      for html_file in self.__listHTMLFiles:
         basename = os.path.basename(html_file)
         is_pyhtml = basename.lower().endswith('.py.html')
         if prev_is_pyhtml is not None and is_pyhtml != prev_is_pyhtml:
            html_file_list_code.append('<hr>')
         prev_is_pyhtml = is_pyhtml
         name, _ = os.path.splitext(basename)
         html_row = html_index_file_pattern.html_list_row
         file_id_name = self.__filename_to_html_id(basename)
         html_row = html_row.replace("###FILE_ID_NAME###", file_id_name)
         html_row = html_row.replace("###FILE_NAME###", basename)
         html_row = html_row.replace("###FILE_NAME_ONLY###", name) # means: without extension .html
         html_file_list_code.append(html_row)

      index_file_code = html_index_file_pattern.html_index_file_pattern
      # TODO: check index [0]
      first_file_name = os.path.basename(self.__listHTMLFiles[0])
      index_file_code = index_file_code.replace("###ON_OPEN_SHOW_FILE###", first_file_name)
      index_file_code = index_file_code.replace("###APP_NAME###", self.__dictPackageDocConfig['PACKAGENAME'])
      index_file_code = index_file_code.replace("###HTML_FILE_LIST###", "\n".join(html_file_list_code))

      # prepare index.html
      index_htmlfile = f"{html_dest}/index.html"
      oHTMLFile = CFile(index_htmlfile)
      oHTMLFile.Write(index_file_code)
      del oHTMLFile

      # Save also the HTML files list in configuration.
      # The content is dumped to a config file in JSON format. And this file can be used for further computation by other applications.
      self.__dictPackageDocConfig['HTML_FILES'] = self.__listHTMLFiles

      # Save also path and name of index file (will be written to console at end of script).
      self.__dictPackageDocConfig['INDEX_HTMLFILE'] = index_htmlfile

      bSuccess = True
      sResult  = f"HTML documentation created within\n'{html_dest}'"

      return bSuccess, sResult

   # eof def __PrepareHTMLDoc(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def Build(self):
      """
**Arguments:**

(*no arguments*)

**Returns:**

* :pcode:`bSuccess`

  / *Type*: bool /

  Indicates if the computation of the method :pcode:`sMethod` was successful or not.

* :pcode:`sResult`

  / *Type*: str /

  The result of the computation of the method :pcode:`sMethod`.
      """

      sMethod = "CDocBuilder.Build"

      sBuildFolder = self.__dictPackageDocConfig.get('OUTPUT')
      if not sBuildFolder:
         bSuccess = False
         sResult  = f"'OUTPUT' key not defined in configuration"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      bSuccess, sResult = self.__CleanFolder(sBuildFolder)
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      bSuccess, sResult = self.__RenderDiagrams()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      if sResult is not None:
          print(COLBY + sResult)
          print()

      bSuccess, sResult = self.__CopyDiagrams()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      bSuccess, sResult = self.__CopyPictures()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sBuildFolder = self.__dictPackageDocConfig['OUTPUT']

      oSourceParser = CSourceParser()

      listofdictChapterInfo = [] # needed for TOC of main TeX file

      # needed for LaTeX definitions autogenerated by docutils
      # (debug reference only, the corresponding active file is maintained manually)
      collected_latex_defs = set()

      # docutils settings
      settings_overrides = {
          'output_encoding'      : 'utf-8',
          'font_encoding'        : 'T1',
          'language_code'        : 'en',  # default set explicitly for better readability
          'legacy_column_widths' : False, # activates a table rendering behavior that is new and more flexible (currently docutils throw a future warning)
          'use_latex_citations'  : True   # avoid docutils future warning
      }

      # -- check if files need to be excluded from computation
      listExcludes = self.__dictPackageDocConfig['TOC'].get('EXCLUDE', [])

      # -- check existence of document parts and parse the content

      listDocumentParts = self.__dictPackageDocConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPart in listDocumentParts:
         sDocumentPartPath = self.__dictPackageDocConfig['TOC'][sDocumentPart]

         # -- check existence

         if sDocumentPart.startswith("INTERFACE"):
            if os.path.isdir(sDocumentPartPath) is False:
               bSuccess = False
               sResult  = f"Interface folder '{sDocumentPartPath}' does not exist."
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            if os.path.isfile(sDocumentPartPath) is False:
               bSuccess = False
               sResult  = f"File '{sDocumentPartPath}' does not exist."
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

         # -- parse the content

         print(f"* Document part : '{sDocumentPart}' : '{sDocumentPartPath}'")

         if sDocumentPart.startswith("INTERFACE"):

            sRootPath = sDocumentPartPath
            sSourceFilesRootFolderName = os.path.basename(sRootPath) # should be the package name (the import name)

            listModules, bSuccess, sResult = self.__GetModulesList(sRootPath)
            if bSuccess is not True:
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            print()
            print(sResult)
            print()

            for sModule in listModules:

               listLinesRST = [] # the module/chapter specific subset

               # -- get informations about the source file and derive further information

               oModule = CFile(sModule)
               dModuleFileInfo = oModule.GetFileInfo()
               del oModule
               sModuleFilePath     = dModuleFileInfo['sFilePath']
               sModuleFileNameOnly = dModuleFileInfo['sFileNameOnly']
               sModuleFileSubPath  = sModuleFilePath[len(sRootPath)+1:]

               if sModuleFileNameOnly in listExcludes:
                  print(f"* Skipping module : '{sModule}'")
                  continue

               print(f"* Module : '{sModule}'")

               # -- prepare the scope of the module file (used for labels within LaTeX code and for the names of LaTeX files generated out of reST code)
               sModuleFileScope = ""
               if sModuleFileSubPath == "":
                  sModuleFileScope = f"{sSourceFilesRootFolderName}-{sModuleFileNameOnly}"
               else:
                  sModuleFileScope = f"{sSourceFilesRootFolderName}-{sModuleFileSubPath}-{sModuleFileNameOnly}"
               sModuleFileScope   = self.__ConvertToScopeFormat(sModuleFileScope)
               sModuleTeXFileName = f"{sModuleFileScope}.tex"
               sModuleTeXFile     = f"{sBuildFolder}/{sModuleTeXFileName}"

               # -- prepare the import path of the module in Python 'import' notation
               sPythonModuleImport = ""
               if sModuleFileSubPath == "":
                  sPythonModuleImport = f"{sSourceFilesRootFolderName}.{sModuleFileNameOnly}"
               else:
                  sModuleFileSubPath = sModuleFileSubPath.replace('/', '.')
                  sPythonModuleImport = f"{sSourceFilesRootFolderName}.{sModuleFileSubPath}.{sModuleFileNameOnly}"

               # -- get all informations out of the source file
               dictContent, bSuccess, sResult = oSourceParser.ParseSourceFile(sModule,
                                                                              self.__dictPackageDocConfig['CONTROL']['INCLUDEPRIVATE'],
                                                                              self.__dictPackageDocConfig['CONTROL']['INCLUDEUNDOCUMENTED'])
               if bSuccess is not True:
                  return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

               if dictContent is None:
                  print("  nothing relevant inside")
                  print()
                  continue

               listofdictFunctions = dictContent['listofdictFunctions']
               listofdictClasses   = dictContent['listofdictClasses']
               sFileDescription    = dictContent['sFileDescription']

               # -- file description
               if sFileDescription is not None:
                  print("  file description found")
                  listLinesRST.append(sFileDescription)
                  listLinesRST.append("")

               # -- reST content of all functions

               for dictFunction in listofdictFunctions:
                  sFunctionName  = dictFunction['sFunctionName']
                  sFunctionScope = f"{sModuleFileScope}-{sFunctionName}"
                  sFunctionScope = self.__ConvertToScopeFormat(sFunctionScope)
                  sFunctionHeadline = f"Function: {sFunctionName}"
                  self.__dictScopes[sFunctionScope] = sFunctionHeadline

                  sFunctionDocString = dictFunction['sFunctionDocString']

                  print(f"    > Function : '{sFunctionName}' / scope: '{sFunctionScope}'")

                  listLinesRST.append(sFunctionScope)
                  sFunctionHeadlineUnderline = len(sFunctionScope)*"="
                  listLinesRST.append(sFunctionHeadlineUnderline)
                  listLinesRST.append("")
                  if sFunctionDocString is not None:
                     listLinesRST.append(sFunctionDocString)
                     listLinesRST.append("")

               # eof for dictFunction in listofdictFunctions:


               # -- reST content of all classes and methods

               for dictClass in listofdictClasses:
                  sClassName  = dictClass['sClassName']
                  sClassScope = f"{sModuleFileScope}-{sClassName}"
                  sClassScope = self.__ConvertToScopeFormat(sClassScope)
                  sClassHeadline = f"Class: {sClassName}"
                  self.__dictScopes[sClassScope] = sClassHeadline

                  sClassDocString   = dictClass['sClassDocString']
                  listofdictMethods = dictClass['listofdictMethods']

                  print(f"  > Class : '{sClassName}' / scope: '{sClassScope}'")

                  # tmp mapping
                  sClassHeadline = sClassScope

                  sPythonModuleImportFull = f"from {sPythonModuleImport} import {sClassName}"

                  listLinesRST.append(sClassHeadline)
                  sClassHeadlineUnderline = len(sClassHeadline)*"="
                  listLinesRST.append(sClassHeadlineUnderline)
                  listLinesRST.append("")
                  # # Let's skip this. The resulting lines are too long for the width of a DinA4 page.
                  # # And the information is also not so much important.
                  # # listLinesRST.append("*Imported by*:")
                  # # listLinesRST.append("")
                  # # listLinesRST.append(".. code:: python")
                  # # listLinesRST.append("")
                  # # listLinesRST.append(f"    {sPythonModuleImportFull}")
                  # # listLinesRST.append("")
                  if sClassDocString is not None:
                     listLinesRST.append(sClassDocString)
                     listLinesRST.append("")


                  for dictMethod in listofdictMethods:
                     sMethodName = dictMethod['sMethodName']
                     bIsKeyword  = dictMethod['bIsKeyword']
                     sIdentifier = "Method"
                     if bIsKeyword is True:
                        sIdentifier = "Keyword"
                     sMethodHeadline = f"{sIdentifier}: {sMethodName}"
                     sMethodScope    = f"{sModuleFileScope}-{sClassName}-{sMethodName}"
                     sMethodScope    = self.__ConvertToScopeFormat(sMethodScope)
                     self.__dictScopes[sMethodScope] = sMethodHeadline

                     print(f"    - {sIdentifier} : '{sMethodName}' / scope: '{sMethodScope}'")

                     # tmp mapping
                     sMethodHeadline = sMethodScope

                     listLinesRST.append(sMethodHeadline)
                     sMethodHeadlineUnderline = len(sMethodHeadline)*"-"
                     listLinesRST.append(sMethodHeadlineUnderline)
                     listLinesRST.append("")
                     sMethodDocString = dictMethod['sMethodDocString']
                     if sMethodDocString is not None:
                        listLinesRST.append(sMethodDocString)
                        listLinesRST.append("")

               # eof for dictClass in listofdictClasses:

               print()

               listLinesResolved, bSuccess, sResult = self.__ResolvePlaceholders(listLinesRST)
               if bSuccess is not True:
                  return listLinesResolved, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

               # -- reST postprocessing (extended syntax)
               listLinesProcessed = self.__PostprocessRST(listLinesResolved)

               sRSTCode = "\n".join(listLinesProcessed)

               # debug only; sRSTCodeFile not really required
               # maybe move to below __PostprocessTEX() call
               sRSTCodeFileName = os.path.basename(sModule) + ".rst"
               sRSTCodeFile = f"{sBuildFolder}/{sRSTCodeFileName}"
               oRSTCodeFile = CFile(sRSTCodeFile)
               oRSTCodeFile.Write(sRSTCode)
               del oRSTCodeFile

               # -----------------------------------------------------------------------------
               # sRSTCode:
               # * reST content with resolved placeholders (__ResolvePlaceholders)
               # * Contains still extended syntax and multiply-defined labels
               #   (Resolving will be handled individually for tex and HTML output)
               # -----------------------------------------------------------------------------

               # -----------------------------------------------------------------------------
               # -- convert the complete reST content of the current source file to tex format
               # -----------------------------------------------------------------------------
               latex_parts = publish_parts(source=sRSTCode, writer=CustomLaTeXWriter(), settings_overrides=settings_overrides)
               definition_names = ("requirements", "fallbacks", "pdfsetup", "stylesheet")
               for definition_name in definition_names:
                  definition = latex_parts.get(definition_name, "").strip()
                  definition = f"% {definition_name}\n{definition}\n% -------------------------------------------\n\n"
                  collected_latex_defs.add(definition)

               latex_code = latex_parts['body'] # the LaTeX text
               listLinesTEX = latex_code.splitlines() # ensure proper line endings

               # -- tex postprocessing (extended syntax and multiply-defined labels)
               listLinesProcessed = self.__PostprocessTEX(listLinesTEX)
               sTEX = "\n".join(listLinesProcessed)

               # -- create the corresponding tex file for the current source file
               oModuleTeXFile = CFile(sModuleTeXFile)
               oModuleTeXFile.Write("%")
               oModuleTeXFile.Write("% Generated at " + time.strftime('%d.%m.%Y - %H:%M:%S') + " by " + self.__dictPackageDocConfig['PACKAGENAME'])
               oModuleTeXFile.Write("%")
               oModuleTeXFile.Write()
               oModuleTeXFile.Write(sTEX)
               del oModuleTeXFile

               # -- save some infos needed for TOC of main TeX file
               sFileName = dModuleFileInfo['sFileName']
               dictChapterInfo ={}
               dictChapterInfo['sChaptername'] = sFileName
               dictChapterInfo['sTeXFileName'] = sModuleTeXFileName
               dictChapterInfo['sLabel']       = sModuleFileScope
               listofdictChapterInfo.append(dictChapterInfo)

               # ------------------------------------------------------------------------------
               # -- convert the complete reST content of the current source file to HTML format
               # ------------------------------------------------------------------------------
               tuplestylesheets = ("./styles/common.css",
                                   "./styles/pythoncode.css",
                                   "./styles/pcode.css",
                                   "./styles/robotcode.css",
                                   "./styles/rcode.css",
                                   "./styles/jsoncode.css",
                                   "./styles/jcode.css",
                                   "./styles/consolelog.css",
                                   "./styles/filesystem.css",
                                   "./styles/anycontent.css",
                                   "./styles/highlight.css",
                                   "./styles/simpletable.css")
               stylesheets = ",".join(tuplestylesheets)

               html_content = publish_string(
                       source=sRSTCode,
                       writer=CustomHTMLWriter(),
                       settings_overrides={
                           'stylesheet'      : stylesheets,
                           'stylesheet_path' : None,
                           'embed_stylesheet': False,
                           'title'           : sFileName
                       })

               listLinesHTML = html_content.decode('utf-8').splitlines()
               # add headline to HTML file
               listLinesHTML = self.__replace_in_array(listLinesHTML, "<main>", f"<main>\n\n<h1>{sFileName}</h1>")

               # -- html postprocessing (extended syntax and multiply-defined labels)
               listLinesProcessed = self.__PostprocessHTML(listLinesHTML)
               sHTML = "\n".join(listLinesProcessed)

               # -- create the corresponding HTML file for the current source file

               sHTMLCodeFileName = os.path.basename(sModule) + ".html"
               sHTMLCodeFile = f"{sBuildFolder}/{sHTMLCodeFileName}"  # TODO: check for ambiguitvity; full scope in name required? (like in tex files?)
               oHTMLCodeFile = CFile(sHTMLCodeFile)
               oHTMLCodeFile.Write(sHTML)
               del oHTMLCodeFile
               self.__listHTMLFiles.append(sHTMLCodeFile)

            # eof for sModule in listModules:

         # eof if sDocumentPart.startswith("INTERFACE"):

         else:

            # all other separate files (reST or tex)

            if sDocumentPartPath.lower().endswith('rst'):
               sRSTFile = sDocumentPartPath
               oRSTFile = CFile(sRSTFile)
               listLinesRST, bSuccess, sResult = oRSTFile.ReadLines()
               if bSuccess is not True:
                  del oRSTFile
                  return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

               dRSTFileInfo = oRSTFile.GetFileInfo()
               sRSTFileNameOnly = dRSTFileInfo['sFileNameOnly']
               del oRSTFile
               sChaptername = sRSTFileNameOnly
               sTeXFile = f"{sBuildFolder}/{sRSTFileNameOnly}.tex"

               listLinesResolved, bSuccess, sResult = self.__ResolvePlaceholders(listLinesRST)
               if bSuccess is not True:
                  return listLinesResolved, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

               # -- reST postprocessing (extended syntax)
               listLinesProcessed = self.__PostprocessRST(listLinesResolved)

               sRSTCode = "\n".join(listLinesProcessed)

               # -- convert the complete reST content of the current source file to tex format
               latex_parts = publish_parts(source=sRSTCode, writer=CustomLaTeXWriter(), settings_overrides=settings_overrides)
               definition_names = ("requirements", "fallbacks", "pdfsetup", "stylesheet")
               for definition_name in definition_names:
                  definition = latex_parts.get(definition_name, "").strip()
                  definition = f"% {definition_name}\n{definition}\n% -------------------------------------------\n\n"
                  collected_latex_defs.add(definition)

               latex_code = latex_parts['body'] # the LaTeX text
               listLinesTEX = latex_code.splitlines() # ensure proper line endings

               # -- tex postprocessing (extended syntax and multiply-defined labels)
               ####1
               listLinesProcessed = self.__PostprocessTEX(listLinesTEX)
               sTEX = "\n".join(listLinesProcessed)

               # -- create the corresponding tex file for the current source file

               oTeXFile = CFile(sTeXFile)
               oTeXFile.Write("%")
               oTeXFile.Write("% Generated at " + time.strftime('%d.%m.%Y - %H:%M:%S') + " by " + self.__dictPackageDocConfig['PACKAGENAME'])
               oTeXFile.Write("%")
               oTeXFile.Write()
               oTeXFile.Write(sTEX)
               del oTeXFile

               # -- save some infos needed for TOC of main TeX file
               dictChapterInfo ={}
               dictChapterInfo['sChaptername'] = sChaptername
               dictChapterInfo['sTeXFileName'] = f"{sRSTFileNameOnly}.tex"
               dictChapterInfo['sLabel']       = self.__ConvertToScopeFormat(f"{sRSTFileNameOnly}")
               listofdictChapterInfo.append(dictChapterInfo)

               # ------------------------------------------------------------------------------
               # -- convert the complete reST content of the current source file to HTML format
               # ------------------------------------------------------------------------------
               tuplestylesheets = ("./styles/common.css",
                                   "./styles/pythoncode.css",
                                   "./styles/pcode.css",
                                   "./styles/robotcode.css",
                                   "./styles/rcode.css",
                                   "./styles/jsoncode.css",
                                   "./styles/jcode.css",
                                   "./styles/consolelog.css",
                                   "./styles/filesystem.css",
                                   "./styles/anycontent.css",
                                   "./styles/highlight.css",
                                   "./styles/simpletable.css")
               stylesheets = ",".join(tuplestylesheets)

               html_content = publish_string(
                       source=sRSTCode,
                       writer=CustomHTMLWriter(),
                       settings_overrides={
                           'stylesheet'      : stylesheets,
                           'stylesheet_path' : None,
                           'embed_stylesheet': False,
                           'title'           : sChaptername
                       })

               listLinesHTML = html_content.decode('utf-8').splitlines()
               # add headline to HTML file
               listLinesHTML = self.__replace_in_array(listLinesHTML, "<main>", f"<main>\n\n<h1>{sChaptername}</h1>")

               # -- html postprocessing (extended syntax and multiply-defined labels)
               listLinesProcessed = self.__PostprocessHTML(listLinesHTML)
               sHTML = "\n".join(listLinesProcessed)

               # -- create the corresponding HTML file for the current source file

               sHTMLCodeFileName = f"{sRSTFileNameOnly}.html"
               sHTMLCodeFile = f"{sBuildFolder}/{sHTMLCodeFileName}"               # TODO: consider full scope in name, like tex files too
               oHTMLCodeFile = CFile(sHTMLCodeFile)
               oHTMLCodeFile.Write(sHTML)
               del oHTMLCodeFile
               self.__listHTMLFiles.append(sHTMLCodeFile)

            # eof if sDocumentPartPath.lower().endswith('rst'):

            elif sDocumentPartPath.lower().endswith('tex'):
               # We keep the tex file untouched, but we have to copy this file to the output folder
               # and we have to import the file into the main tex file.
               sTEXFile = sDocumentPartPath
               oTEXFile = CFile(sTEXFile)
               dTEXFileInfo = oTEXFile.GetFileInfo()
               sTEXFileNameOnly = dTEXFileInfo['sFileNameOnly']
               sChaptername = sTEXFileNameOnly
               sTEXFileNameOnly = sTEXFileNameOnly.replace(" ", "_")
               sDestTeXFile = f"{sBuildFolder}/{sTEXFileNameOnly}.tex"
               bSucces, sResult = oTEXFile.CopyTo(sDestTeXFile, bOverwrite=True)
               if bSuccess is not True:
                  return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
               del oTEXFile
               # -- save some infos needed for TOC of main tex file
               dictChapterInfo ={}
               dictChapterInfo['sChaptername'] = sChaptername
               dictChapterInfo['sTeXFileName'] = f"{sTEXFileNameOnly}.tex"
               dictChapterInfo['sLabel']       = self.__ConvertToScopeFormat(f"{sTEXFileNameOnly}")
               listofdictChapterInfo.append(dictChapterInfo)

            # eof else - if sDocumentPartPath.lower().endswith('rst'):
         # eof else - if sDocumentPart.startswith("INTERFACE"):
      # eof for sDocumentPart in listDocumentParts:

      print()

      # -- finally create the main TeX file, the autogenerated style files and the PDF

      # make the styles folder available within the new build folder
      sStylesFolder = self.__dictPackageDocConfig['LATEXSTYLESFOLDER']
      oStylesFolder = CFolder(sStylesFolder)
      bSuccess, sResult = oStylesFolder.CopyTo(sBuildFolder)
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # 1. Collected LaTeX definitions autogenerated by docutils
      latex_defs_file = f"{sBuildFolder}/styles/docutils_autogen.sty.txt"
      latex_defs_file_handle = CFile(latex_defs_file)
      hint = f"% file autogenerated by GenPackageDoc at '{time.strftime('%d.%m.%Y - %H:%M:%S')}'"
      latex_defs_file_handle.Write(hint)
      for definition in collected_latex_defs:
         latex_defs_file_handle.Write(f"{definition}\n")
      del latex_defs_file_handle

      # access to patterns
      oPatterns = CPatterns()

      # 2. Autodefined sty file (containing runtime informations)
      sAutodefinedFile = f"{sBuildFolder}/styles/autodefined.sty"
      oAutodefinedFile = CFile(sAutodefinedFile)
      sAutodefinedHeader = oPatterns.GetAutodefinedHeader(time.strftime('%d.%m.%Y - %H:%M:%S'))
      oAutodefinedFile.Write(sAutodefinedHeader)
      REPOSITORYNAME = self.__dictPackageDocConfig['REPOSITORYNAME'].replace("_", r"\_")
      sCommand = r"\newcommand{\repo}{\textbf{" + REPOSITORYNAME + "}}"
      oAutodefinedFile.Write(sCommand)
      PACKAGENAME = self.__dictPackageDocConfig['PACKAGENAME'].replace("_", r"\_")
      sCommand = r"\newcommand{\pkg}{\textbf{" + PACKAGENAME + "}}"
      oAutodefinedFile.Write(sCommand)
      oAutodefinedFile.Write()
      del oAutodefinedFile

      # 3. Main tex file
      sDocumentationTeXFileName = self.__dictPackageDocConfig['DOCUMENT']['OUTPUTFILENAME']
      sMainTexFile = f"{sBuildFolder}/{sDocumentationTeXFileName}"
      self.__dictPackageDocConfig['sMainTexFile'] = sMainTexFile
      oMainTexFile = CFile(sMainTexFile)
      dMainTexFileInfo = oMainTexFile.GetFileInfo()
      sMainTexFileNameOnly = dMainTexFileInfo['sFileNameOnly']
      sPDFFileName = f"{sMainTexFileNameOnly}.pdf"
      sPDFFileExpected = f"{sBuildFolder}/{sPDFFileName}"
      self.__dictPackageDocConfig['sPDFFileName']     = sPDFFileName # used later to copy the file to another location
      self.__dictPackageDocConfig['sPDFFileExpected'] = sPDFFileExpected # used later to verify the build
      sHeader = oPatterns.GetHeader(sTitle=self.__dictPackageDocConfig['DOCUMENT']['TITLE'],
                                    sVersion=self.__dictPackageDocConfig['DOCUMENT']['VERSION'],
                                    sAuthor=self.__dictPackageDocConfig['DOCUMENT']['AUTHOR'],
                                    sDate=self.__dictPackageDocConfig['DOCUMENT']['DATE'])
      oMainTexFile.Write(sHeader)

      # -- add modules to main TeX file
      for dictChapterInfo in listofdictChapterInfo:
         sChapter = oPatterns.GetChapter(sHeadline=dictChapterInfo['sChaptername'], sLabel=dictChapterInfo['sLabel'], sDocumentName=dictChapterInfo['sTeXFileName'])
         oMainTexFile.Write(sChapter)

      # -- add creation date to main TeX file
      sPDFFileName_masked = sPDFFileName.replace('_', r'\_') # LaTeX requires this masking
      oMainTexFile.Write(r"\vfill")
      oMainTexFile.Write(r"\begin{center}")
      oMainTexFile.Write(r"\begin{tabular}{m{16em}}\hline")
      oMainTexFile.Write(r"   \multicolumn{1}{c}{\textbf{" + f"{sPDFFileName_masked}" + r"}}\\")
      oMainTexFile.Write(r"   \multicolumn{1}{c}{\textit{Created at " + self.__dictPackageDocConfig['NOW'] + r"}}\\")
      oMainTexFile.Write(r"   \multicolumn{1}{c}{\textit{by " + self.__dictPackageDocConfig['DOCBUILDERFULLNAME'] + r"}}\\ \hline")
      oMainTexFile.Write(r"\end{tabular}")
      oMainTexFile.Write(r"\end{center}")

      sFooter = oPatterns.GetFooter()
      oMainTexFile.Write(sFooter)

      del oMainTexFile

      # 4. HTML documentation files
      if self.__dictPackageDocConfig['HTMLDEST']:
         bSuccess, sResult = self.__PrepareHTMLDoc()
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            print(COLBY + f"\n{sResult}")
            print()

      # 5. PDF file
      if self.__dictPackageDocConfig['bSimulateOnly'] is True:
         print()
         print(COLBY + "GenPackageDoc is running in simulation mode.")
         print(COLBY + "Skipping call of LaTeX compiler. No new PDF output will be generated, already existing output will not be updated!")
         print(COLBY + "! This is not handled as error and also not handled as warning !")
         print()
         bSuccess = True
         sResult  = f"Generation of PDF output skipped because of simulation mode!"
      else:
         bSuccess, sResult = self.__GenDocPDF()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      else:
         print(COLBY + sResult)
         print()

      # 6. Dump the complete configuration (in temporary output folder)
      sOutputFolder = self.__dictPackageDocConfig['OUTPUT']
      sPackageName  = self.__dictPackageDocConfig['PACKAGENAME']

      # 6.a text format
      sDumpConfigFileNameTxt = f"_CONFIG_{sPackageName}.txt"
      sDumpConfigFileTxt = f"{sOutputFolder}/{sDumpConfigFileNameTxt}"
      try:
         hDumpConfigFile = open(sDumpConfigFileTxt, "w", encoding="utf-8")
         PrettyPrint(self.__dictPackageDocConfig, hDumpConfigFile, bToConsole=False, sPrefix=None)
         hDumpConfigFile.close()
         del hDumpConfigFile
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason)
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # 6.b JSON format
      sDumpConfigFileNameJson = f"_CONFIG_{sPackageName}.json"
      sDumpConfigFileJson = f"{sOutputFolder}/{sDumpConfigFileNameJson}"
      try:
         hDumpConfigFile = open(sDumpConfigFileJson, "w", encoding="utf-8")
         json.dump(self.__dictPackageDocConfig, hDumpConfigFile, indent=3)
         hDumpConfigFile.close()
         del hDumpConfigFile
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason)
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # 6.c Make a backup of the configuration (if configured)
      sConfigDestFolder = self.__dictPackageDocConfig['CONFIGDEST']
      if sConfigDestFolder is not None:
         sDumpConfigFileTxtDest = f"{sConfigDestFolder}/{sDumpConfigFileNameTxt}"
         oDumpConfigFileTxt = CFile(sDumpConfigFileTxt)
         bSuccess, sResult = oDumpConfigFileTxt.CopyTo(sDumpConfigFileTxtDest, bOverwrite=True)
         del oDumpConfigFileTxt
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            sResult = f"Configuration dump in text format\n'{sDumpConfigFileTxtDest}'"
            print(COLBY + sResult)
            print()
         sDumpConfigFileJsonDest = f"{sConfigDestFolder}/{sDumpConfigFileNameJson}"
         oDumpConfigFileJson = CFile(sDumpConfigFileJson)
         bSuccess, sResult = oDumpConfigFileJson.CopyTo(sDumpConfigFileJsonDest, bOverwrite=True)
         del oDumpConfigFileJson
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            sResult = f"Configuration dump in JSON format\n'{sDumpConfigFileJsonDest}'"
            print(COLBY + sResult)
            print()

      # further feedback at end of computation (= after lots of LaTeX output in console)
      if 'INDEX_HTMLFILE' in self.__dictPackageDocConfig:
          index_htmlfile = self.__dictPackageDocConfig['INDEX_HTMLFILE']
          if os.path.isfile(index_htmlfile):
              sResult = f"Documentation in HTML format:\n'{index_htmlfile}'"
              print(COLBY + sResult)
              print()

      if bSuccess is True:
         sResult = "GenPackageDoc build done."
      else:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def Build(self):

   # --------------------------------------------------------------------------------------------------------------

# eof class CDocBuilder():

# --------------------------------------------------------------------------------------------------------------
