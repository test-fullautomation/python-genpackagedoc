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
# CDocBuilder.py
#
# XC-CT/ECA3-Queckenstedt
#
# 06.01.2023
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing all methods to generate tex sources.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, shlex, subprocess, platform, shutil, re, json
import colorama as col
import pypandoc

from GenPackageDoc.CSourceParser import CSourceParser
from GenPackageDoc.CPatterns import CPatterns
from GenPackageDoc.version import VERSION

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
#TM***

class CDocBuilder():
   """
Main class to build tex sources out of docstrings of Python modules and separate text files in rst format.

Depends on a json configuration file, provided by a ``oPackageDocConfig`` object (this includes the
Repository configuration).

Method to execute: ``Build()``
   """

   def __init__(self, oPackageDocConfig=None):
      """
Constructor of class ``CDocBuilder``.

* ``oPackageDocConfig``

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
      self.__dictPlaceholder = {}
      self.__dictPlaceholder['newline'] = ("!N!E!W!L!I!N!E!")
      self.__dictPlaceholder['newpage'] = ("!N!E!W!P!A!G!E!")
      self.__dictPlaceholder['vspace']  = ("!V!S!P!A!C!E!")

      # Python modules may contain methods with same name in several classes. Different Python modules may contain classes or functions
      # with the same name. GenPackageDoc parses the content of Python modules. The outcome is that for every Python module GenPackageDoc
      # creates a temporary rst file (because the content of the docstrings also has to be written in rst format).
      # This rst file is converted to LaTeX format by Pandoc. To support linking Pandoc adds labels to every
      # heading (that are the names of classes and methods) automatically. The names of the labels are the headings - this means: names of classes
      # and methods are used as label. In case of the names of classes and methods are not unique over all files, also the labels will
      # not be unique. The conversion from rst format to LaTeX format happens for every Python module separately (and therefore the scope
      # is not known). At the end all LaTeX files are put together to one LaTeX file. Outcome: In case of ambiguous labels the LaTeX compiler
      # throws a "multiply-defined labels" warning.
      #
      # To avoid these warnings every headline is replaced by a string containing the full scope (starting with the name of the package folder).
      # This is written to the temporary rst file. Pandoc uses now these full scope strings for labels when converting the rst code into LaTeX code.
      # Finally by __PostprocessRST within every 'section' and 'subsection' command in the LaTeX code the full scope string (that must be unique)
      # is replaced by the original headline (that might be ambiguous). The full scope strings together with their original headlines are stored
      # in 'self.__dictScopes'.

      self.__dictScopes = {}

   def __del__(self):
      pass


   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __ConvertToScopeFormat(self, sString=""):
      """Converts a string to 'scope' format.
      """
      sString = sString.replace(' ', '-')
      sString = sString.replace('_', '-')
      sString = sString.replace('.', '-')
      sString = sString.replace('/', '-')
      sString = sString.lower()
      return sString

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __GetModulesList(self, sRootPath=None):
      """Computes a list of all Python modules found recursively within ``sRootPath``.
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
      """Resolves placeholders used in packagedoc configuration (json file)
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
      """Postprocessing of rst text after reading from rst file or parsing from doctrings and after replacement
of placeholders. This covers e.g. the computation of syntax extensions.

Extensions to the syntax of rst (newline, newpage and vspace) will be masked (by replacement strings, that do no contain
characters belonging to syntax of rst and LaTeX.
      """

      listLinesProcessed = []
      for sLine in listLinesRST:
         if sLine == "/":
            sLine = self.__dictPlaceholder['vspace']
         elif sLine == "//":
            sLine = self.__dictPlaceholder['newpage']
         elif ( (len(sLine) > 1) and sLine.endswith('/') and not sLine.endswith('//') ):
            sLine = sLine[:-1] + self.__dictPlaceholder['newline']
         listLinesProcessed.append(sLine)

      return listLinesProcessed

   # eof def __PostprocessRST(self, listLines=[]):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __PostprocessTEX(self, listLinesTEX=[]):
      """Postprocessing of TEX text. This covers e.g. the computation of rst syntax extensions and also
the recovery of the original headlines out of the intermediately used full scope strings.

The masking of newline, newpage and vspace (rst syntax extensions) are replaced by the corresponding LaTeX commands.
      """

      listLinesProcessed = []

      for sLine in listLinesTEX:

         # certain syntax extensions
         sLine = sLine.replace(self.__dictPlaceholder['vspace'], r"\vspace{1ex}")
         sLine = sLine.replace(self.__dictPlaceholder['newpage'], r"\newpage")
         sLine = sLine.replace(self.__dictPlaceholder['newline'], r"\newline")

         # To handle ambiguous names of methods, classes and methods, the original names (= document headlines)
         # are replaced by the full scopes. We will not run into trouble any more when Pandoc creates labels out of the headlines
         # when converting the rst source code to LaTeX code.
         # Here we have to undo this replacement: We replace the full scope string in every section and subsection by the original headline.

         # Pandoc adds ligatures in some cases: '--' -> '-\/-'. We do not need them. They have to be removed before we search for sKey,
         # because sKey does not contain these ligatures.
         if "section{" in sLine:
            sLine = sLine.replace(r'\/', '')

         for sKey in self.__dictScopes:
            # sKey is full scope string
            # value of sKey is original headline (= original name of function, class or method)
            sSearch  = "section{" + sKey + "}" # this includes 'subsection'
            sReplace = "section{" + self.__dictScopes[sKey] + "}"
            sReplace = sReplace.replace('_', r'\_') # LaTeX requires this masking
            sLine = sLine.replace(sSearch, sReplace)

         listLinesProcessed.append(sLine)

      return listLinesProcessed

   # eof def __PostprocessTEX(self, listLinesTEX=[]):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __CleanBuildFolder(self):
      """Cleans the build folder (to a avoid a mixture of current and previous results).
The meaning of clean is: *delete*, followed by *create*.
      """

      sMethod = "CDocBuilder.__CleanBuildFolder"

      bSuccess = None
      sResult  = None

      sBuildFolder = self.__dictPackageDocConfig['OUTPUT']

      if os.path.isdir(sBuildFolder) is True:
         print(f"* Deleting folder '{sBuildFolder}'")
         print()
         try:
            shutil.rmtree(sBuildFolder)
            pass
         except Exception as ex:
            bSuccess = None
            sResult  = str(ex)
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      try:
         os.makedirs(sBuildFolder)
      except Exception as ex:
         bSuccess = None
         sResult  = str(ex)
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      bSuccess = True
      sResult  = f"Build folder '{sBuildFolder}' cleaned"

      return bSuccess, sResult

   # eof def __CleanBuildFolder(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __CopyPictures(self):
      """Copies the pictures folder to the output folder (required to keep relative paths valid also in created tex files)
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

   def __GenDocPDF(self):
      """Executes the LaTeX compiler to create the PDF file out of the generated source tex files
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
               sResult = f"File '{sPDFFileExpected}'\ncopied to\n{sDestinationPDFFile}"
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

   def Build(self):
      """
**Arguments:**

(*no arguments*)

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method ``sMethod`` was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method ``sMethod``.
      """

      sMethod = "CDocBuilder.Build"

      bSuccess, sResult = self.__CleanBuildFolder()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      bSuccess, sResult = self.__CopyPictures()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sBuildFolder = self.__dictPackageDocConfig['OUTPUT']

      oSourceParser = CSourceParser()

      listofdictChapterInfo = [] # needed for TOC of main TeX file

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
            sSourceFilesRootFolderName = os.path.basename(sRootPath) # should be the package name

            listModules, bSuccess, sResult = self.__GetModulesList(sRootPath)
            if bSuccess is not True:
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            print()
            print(sResult)
            print()

            for sModule in listModules:

               print(f"* Module : '{sModule}'")

               listLinesRST = [] # the module/chapter specific subset

               # -- get informations about the source file and derive further information

               oModule = CFile(sModule)
               dModuleFileInfo = oModule.GetFileInfo()
               del oModule
               sModuleFilePath     = dModuleFileInfo['sFilePath']
               sModuleFileNameOnly = dModuleFileInfo['sFileNameOnly']
               sModuleFileSubPath  = sModuleFilePath[len(sRootPath)+1:]

               # -- prepare the scope of the module file (used for labels within LaTeX code and for the names of LaTeX files generated out of rst code)
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

               # -- rst content of all functions

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

               # eof for dictFunction in listofdictFunctions:


               # -- rst content of all classes and methods

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
                  listLinesRST.append("*Imported by*:")
                  listLinesRST.append("")
                  listLinesRST.append(".. code::python")
                  listLinesRST.append("")
                  listLinesRST.append(f"   {sPythonModuleImportFull}")
                  listLinesRST.append("")
                  if sClassDocString is not None:
                     listLinesRST.append(sClassDocString)


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

               # eof for dictClass in listofdictClasses:

               print()

               listLinesResolved, bSuccess, sResult = self.__ResolvePlaceholders(listLinesRST)
               if bSuccess is not True:
                  return listLinesResolved, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

               sRSTCode = "\n".join(listLinesResolved)

               # debug only; sRSTCodeFile not really required
               sRSTCodeFileName = os.path.basename(sModule) + ".rst"
               sRSTCodeFile = f"{sBuildFolder}/{sRSTCodeFileName}"
               oRSTCodeFile = CFile(sRSTCodeFile)
               oRSTCodeFile.Write(sRSTCode)
               del oRSTCodeFile

               # -- convert the complete rst content of the current source file to tex format

               sTEX = pypandoc.convert_text(sRSTCode,
                                            'tex',
                                            format='rst')

               listLinesTEX = sTEX.splitlines() # ensure proper line endings

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

            # eof for sModule in listModules:

         # eof if sDocumentPart.startswith("INTERFACE"):

         else:

            # all other separate files (rst or tex)

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
               sRSTFileNameOnly = sRSTFileNameOnly.replace(" ", "_")
               sTeXFile = f"{sBuildFolder}/{sRSTFileNameOnly}.tex"

               listLinesResolved, bSuccess, sResult = self.__ResolvePlaceholders(listLinesRST)
               if bSuccess is not True:
                  return listLinesResolved, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

               # -- rst postprocessing (extended syntax)
               listLinesProcessed = self.__PostprocessRST(listLinesResolved)

               sRSTCode = "\n".join(listLinesProcessed)

               # -- convert the complete rst content of the current source file to tex format
               sTEX = pypandoc.convert_text(sRSTCode,
                                            'tex',
                                            format='rst')

               listLinesTEX = sTEX.splitlines() # ensure proper line endings

               # -- tex postprocessing (extended syntax and multiply-defined labels)
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

      # -- finally create the main TeX file and the PDF

      # make the styles folder available within the new build folder
      sStylesFolder = self.__dictPackageDocConfig['LATEXSTYLESFOLDER']
      oStylesFolder = CFolder(sStylesFolder)
      bSuccess, sResult = oStylesFolder.CopyTo(sBuildFolder)
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # access to patterns
      oPatterns = CPatterns()

      # 1. autodefined sty file (containing runtime informations)
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

      # 2. main tex file
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
      oMainTexFile.Write(r"   \multicolumn{1}{c}{\textit{by GenPackageDoc v. " + VERSION + r"}}\\ \hline")
      oMainTexFile.Write(r"\end{tabular}")
      oMainTexFile.Write(r"\end{center}")

      sFooter = oPatterns.GetFooter()
      oMainTexFile.Write(sFooter)

      del oMainTexFile

      # -- 3. Dump the complete configuration
      sOutputFolder = self.__dictPackageDocConfig['OUTPUT']
      sPackageName  = self.__dictPackageDocConfig['PACKAGENAME']

      # -- 3.a text format
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

      # -- 3.b json format
      sDumpConfigFileNameJson = f"_CONFIG_{sPackageName}.json"
      sDumpConfigFileJson = f"{sOutputFolder}/{sDumpConfigFileNameJson}"
      try:
         hDumpConfigFile = open(sDumpConfigFileJson, "w", encoding="utf-8")
         json.dump(self.__dictPackageDocConfig, hDumpConfigFile)
         hDumpConfigFile.close()
         del hDumpConfigFile
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason)
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # -- make a backup of the configuration (if configured)
      sConfigDestFolder = self.__dictPackageDocConfig['CONFIGDEST']
      if sConfigDestFolder is not None:
         sDumpConfigFileTxtDest = f"{sConfigDestFolder}/{sDumpConfigFileNameTxt}"
         oDumpConfigFileTxt = CFile(sDumpConfigFileTxt)
         bSuccess, sResult = oDumpConfigFileTxt.CopyTo(sDumpConfigFileTxtDest, bOverwrite=True)
         del oDumpConfigFileTxt
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            sResult = f"File '{sDumpConfigFileTxt}'\ncopied to\n'{sDumpConfigFileTxtDest}'"
            print(COLBY + sResult)
            print()
         sDumpConfigFileJsonDest = f"{sConfigDestFolder}/{sDumpConfigFileNameJson}"
         oDumpConfigFileJson = CFile(sDumpConfigFileJson)
         bSuccess, sResult = oDumpConfigFileJson.CopyTo(sDumpConfigFileJsonDest, bOverwrite=True)
         del oDumpConfigFileJson
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            sResult = f"File '{sDumpConfigFileJson}'\ncopied to\n'{sDumpConfigFileJsonDest}'"
            print(COLBY + sResult)
            print()

      # 4. PDF file
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
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def Build(self):

   # --------------------------------------------------------------------------------------------------------------

# eof class CDocBuilder():

# --------------------------------------------------------------------------------------------------------------
