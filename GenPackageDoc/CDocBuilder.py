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
# 31.08.2022
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

  GenPackageDoc configuration containing static and dynamic configuration values.
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

      # -- multiply-defined labels fix

      self.__sPattern_hypertarget = r"(hypertarget{.+?})"
      self.__regex_hypertarget    = re.compile(self.__sPattern_hypertarget)

      self.__sPattern_label = r"(label{.+?})"
      self.__regex_label    = re.compile(self.__sPattern_label)

      sPattern_Name     = r"{(.+?)}"
      self.__regex_Name = re.compile(sPattern_Name)

      # A Python module may contain more than one class. Every class contains a constructor and a destructor
      # that have the same name in every class. In case of private methods are included this causes an
      # "multiply-defined labels" warning (LaTeX). In case of several classes within the same module have methods
      # with the same common name like "Run" or "Execute", this also causes "multiply-defined labels".
      # A possibility to heal this is to add the name of the class to the label. But unfortunately when __PostprocessTEX()
      # is being executed, the class name is not available any more - and it would cause a lot of effort to add this name.
      # Therefore we prefer another solution that is quite simpler: We add a counter to every name. This makes sure,
      # that every name is unique (names of hypertargets and labels).
      self.__nCntNamesHypertarget = 0
      self.__nCntNamesLabel = 0

   def __del__(self):
      pass

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

   def __PostprocessTEX(self, listLinesTEX=[], sNamePrefix_1=None, sNamePrefix_2=None, bAddNameCounter=False):
      """Postprocessing of TEX text. This covers e.g. the computation of syntax extensions.
Also multiply-defined labels (erroneously generated by pandoc) are resolved.

The masking of newline, newpage and vspace (rst syntax extensions) are replaced by the corresponding LaTeX commands.
      """

      if sNamePrefix_1 is not None:
         sNamePrefix_1 = f"{sNamePrefix_1}"
         sNamePrefix_1 = sNamePrefix_1.replace("_","-")
         sNamePrefix_1 = sNamePrefix_1.replace(".","-")
         sNamePrefix_1 = sNamePrefix_1.replace(":","-")
         sNamePrefix_1 = sNamePrefix_1.replace(" ","-")
         sNamePrefix_1 = sNamePrefix_1.lower()

      if sNamePrefix_2 is not None:
         sNamePrefix_2 = f"{sNamePrefix_2}"
         sNamePrefix_2 = sNamePrefix_2.replace("_","-")
         sNamePrefix_2 = sNamePrefix_2.replace(".","-")
         sNamePrefix_2 = sNamePrefix_2.replace(":","-")
         sNamePrefix_2 = sNamePrefix_2.replace(" ","-")
         sNamePrefix_2 = sNamePrefix_2.lower()

      listLinesProcessed = []

      for sLine in listLinesTEX:
         sLine = sLine.replace(self.__dictPlaceholder['vspace'], r"\vspace{1ex}")
         sLine = sLine.replace(self.__dictPlaceholder['newpage'], r"\newpage")
         sLine = sLine.replace(self.__dictPlaceholder['newline'], r"\newline")
         listLinesProcessed.append(sLine)

      sTEXCode = "\n".join(listLinesProcessed)

      for sHypertarget in self.__regex_hypertarget.findall(sTEXCode):
         listNames = self.__regex_Name.findall(sHypertarget)
         if len(listNames) == 1:
            sName = f"{listNames[0]}"
            listNameNew = []
            if sNamePrefix_1 is not None:
               listNameNew.append(sNamePrefix_1)
            if sNamePrefix_2 is not None:
               listNameNew.append(sNamePrefix_2)
            listNameNew.append(sName)
            if bAddNameCounter is True:
               self.__nCntNamesHypertarget = self.__nCntNamesHypertarget + 1
               listNameNew.append(f"{self.__nCntNamesHypertarget}")
            if len(listNameNew) > 0:
               sName_new        = "-".join(listNameNew)
               sHypertarget_new = sHypertarget.replace(sName, sName_new)
               sTEXCode         = sTEXCode.replace(sHypertarget, sHypertarget_new)
      # eof for sHypertarget in self.__regex_hypertarget.findall(sCode):

      for sLabel in self.__regex_label.findall(sTEXCode):
         listNames = self.__regex_Name.findall(sLabel)
         if len(listNames) == 1:
            sName = f"{listNames[0]}"
            listNameNew = []
            if sNamePrefix_1 is not None:
               listNameNew.append(sNamePrefix_1)
            if sNamePrefix_2 is not None:
               listNameNew.append(sNamePrefix_2)
            listNameNew.append(sName)
            if bAddNameCounter is True:
               self.__nCntNamesLabel = self.__nCntNamesLabel + 1
               listNameNew.append(f"{self.__nCntNamesLabel}")
            if len(listNameNew) > 0:
               sName_new = "-".join(listNameNew)
               sLabel_new = sLabel.replace(sName, sName_new)
               sTEXCode = sTEXCode.replace(sLabel, sLabel_new)
      # eof for sLabel in self.__regex_label.findall(sTEXCode):

      listLinesProcessed = sTEXCode.splitlines()

      return listLinesProcessed

   # eof def __PostprocessTEX(self, listLinesTEX=[], sNamePrefix_1=None, sNamePrefix_2=None, bAddNameCounter=False):

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

      listoftuplesChaptersInfo = [] # needed for TOC of main TeX file

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
               sModuleFilePath = dModuleFileInfo['sFilePath']
               sModuleFileNameOnly = dModuleFileInfo['sFileNameOnly']
               sModuleFileSubPath = sModuleFilePath[len(sRootPath)+1:]
               sModuleTeXFileName = ""
               if sModuleFileSubPath == "":
                  sModuleTeXFileName = f"{sModuleFileNameOnly}"
               else:
                  sModuleTeXFileName = f"{sModuleFileSubPath}_{sModuleFileNameOnly}"
               sModuleTeXFileName = sModuleTeXFileName.replace(' ', '_')
               sModuleTeXFileName = sModuleTeXFileName.replace('-', '_')
               sModuleTeXFileName = sModuleTeXFileName.replace('.', '_')
               sModuleTeXFileName = sModuleTeXFileName.replace('/', '_')
               sModuleTeXFileName = f"{sModuleTeXFileName}.tex"
               sModuleTeXFile = f"{sBuildFolder}/{sModuleTeXFileName}"

               sSourceFilesRootFolderName = os.path.basename(sRootPath)
               sPythonModuleImport = ""
               if sModuleFileSubPath == "":
                  sPythonModuleImport = f"{sSourceFilesRootFolderName}.{sModuleFileNameOnly}"
               else:
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
                  sFunctionName      = dictFunction['sFunctionName']
                  sFunctionDocString = dictFunction['sFunctionDocString']

                  print(f"    > Function : '{sFunctionName}'")

                  sFunctionHeadline1 = f"Function: {sFunctionName}"
                  listLinesRST.append(sFunctionHeadline1)
                  sFunctionHeadline2 = len(sFunctionHeadline1)*"="
                  listLinesRST.append(sFunctionHeadline2)
                  listLinesRST.append("")
                  if sFunctionDocString is not None:
                     listLinesRST.append(sFunctionDocString)

               # eof for dictFunction in listofdictFunctions:


               # -- rst content of all classes and methods

               for dictClass in listofdictClasses:
                  sClassName        = dictClass['sClassName']
                  sClassDocString   = dictClass['sClassDocString']
                  listofdictMethods = dictClass['listofdictMethods']

                  print(f"  > Class : '{sClassName}'")

                  sPythonModuleImportFull = f"from {sPythonModuleImport} import {sClassName}"

                  sClassHeadline1 = f"Class: {sClassName}"
                  listLinesRST.append(sClassHeadline1)
                  sClassHeadline2 = len(sClassHeadline1)*"="
                  listLinesRST.append(sClassHeadline2)
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
                     sMethodDocString = dictMethod['sMethodDocString']

                     print(f"    - Method : '{sMethodName}'")

                     sMethodHeadline1 = f"Method: {sMethodName}"
                     listLinesRST.append(sMethodHeadline1)
                     sMethodHeadline2 = len(sMethodHeadline1)*"-"
                     listLinesRST.append(sMethodHeadline2)
                     listLinesRST.append("")
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
               listLinesProcessed = self.__PostprocessTEX(listLinesTEX, sNamePrefix_1=sPythonModuleImport, bAddNameCounter=True)

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
               sModuleName = dModuleFileInfo['sFileName']
               listoftuplesChaptersInfo.append((sModuleName, sModuleTeXFileName))

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
               listLinesProcessed = self.__PostprocessTEX(listLinesTEX, sNamePrefix_1=sRSTFileNameOnly, bAddNameCounter=False)

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
               listoftuplesChaptersInfo.append((sChaptername, f"{sRSTFileNameOnly}.tex"))

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
               listoftuplesChaptersInfo.append((sChaptername, f"{sTEXFileNameOnly}.tex"))

            # eof else - if sDocumentPartPath.lower().endswith('rst'):
         # eof else - if sDocumentPart.startswith("INTERFACE"):
      # eof for sDocumentPart in listDocumentParts:

      print()

      # -- finally create the main TeX file and the PDF
      sStylesFolder = self.__dictPackageDocConfig['LATEXSTYLESFOLDER']
      oStylesFolder = CFolder(sStylesFolder)
      bSuccess, sResult = oStylesFolder.CopyTo(sBuildFolder)
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # 2. main tex file
      oPatterns = CPatterns()
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
      for sHeadline, sTeXFileName in listoftuplesChaptersInfo:
         sChapter = oPatterns.GetChapter(sHeadline=sHeadline, sDocumentName=sTeXFileName)
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
