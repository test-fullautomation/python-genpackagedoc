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
# 18.05.2022
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing all methods to generate tex sources.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, json, shlex, subprocess, platform, shutil, re
import colorama as col
import pypandoc

from GenPackageDoc.CSourceParser import CSourceParser
from GenPackageDoc.CPatterns import CPatterns

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBW = col.Style.BRIGHT + col.Fore.WHITE

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

class CDocBuilder():
   """
Main class to build tex sources out of docstrings of Python modules and separate text files in rst format.

Depends on a json configuration file, provided by a ``oRepositoryConfig`` object.

Method to execute: ``Build()``
   """

   def __init__(self, oRepositoryConfig=None):
      """
Constructor of class ``CDocBuilder``.

Responsible for:

* Take over the repository configuration
* Read the packagedoc configuration from json file
* Resolve placeholders used in packagedoc configuration
* Prepare runtime variables

* ``oRepositoryConfig``

  / *Condition*: required / *Type*: CRepositoryConfig() /

  Repository configuration containing static and dynamic configuration values.
      """

      sMethod = "CDocBuilder.__init__"

      if oRepositoryConfig is None:
         bSuccess = None
         sResult  = "oRepositoryConfig is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # self.__dictConfig is the documentation build configuration including the repository configuration (placeholders resolved)
      #
      self.__dictConfig = {}
      #
      # get the repository configuration
      dictRepositoryConfig = oRepositoryConfig.GetConfig()
      #
      # read the documentation build configuration from separate json file
      #    - the path to the folder containing this json file is taken out of the repository configuration
      #    - the name of the json file is fix
      sJsonFileName = "packagedoc_config.json"
      sDocumentationProjectConfigFile = f"{dictRepositoryConfig['PACKAGEDOC']}/{sJsonFileName}"
      # print(f"========== sDocumentationProjectConfigFile : '{sDocumentationProjectConfigFile}'")

      # The json file may contain lines that are commented out by a '#' at the beginning of the line.
      # Therefore we read in this file in text format, remove the comments and save the cleaned file within the temp folder.
      # Now it's a valid json file and we read the file from there.

      sTmpPath = None
      sPlatformSystem = platform.system()
      if sPlatformSystem == "Windows":
         sTmpPath = CString.NormalizePath("%TMP%")
      elif sPlatformSystem == "Linux":
         sTmpPath = "/tmp"

      sJsonFileCleaned = f"{sTmpPath}/{sJsonFileName}"
      # print(f"========== sJsonFileCleaned : '{sJsonFileCleaned}'")

      oJsonFileSource = CFile(sDocumentationProjectConfigFile)
      listLines, bSuccess, sResult = oJsonFileSource.ReadLines(bSkipBlankLines=True, sComment='#')
      del oJsonFileSource
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      oJsonFileCleaned = CFile(sJsonFileCleaned)
      bSuccess, sResult = oJsonFileCleaned.Write(listLines)
      del oJsonFileCleaned
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)


      # TODO: try/except
      dictDocConfig = None
      hDocumentationProjectConfigFile = open(sJsonFileCleaned)
      dictDocConfig = json.load(hDocumentationProjectConfigFile)
      hDocumentationProjectConfigFile.close()

      # get keys and values from repository configuration
      for key, value in dictRepositoryConfig.items():
         self.__dictConfig[key] = value

      # add current timestamp
      self.__dictConfig['NOW'] = time.strftime('%d.%m.%Y - %H:%M:%S')

      # get some basic keys and values from documentation build configuration
      # TODO: if key in dict / otherwise error / or make optional?
      self.__dictConfig['CONTROL']  = dictDocConfig['CONTROL']
      self.__dictConfig['PICTURES'] = dictDocConfig['PICTURES']
      self.__dictConfig['OUTPUT']   = dictDocConfig['OUTPUT']
      self.__dictConfig['PDFDEST']  = dictDocConfig['PDFDEST']
      self.__dictConfig['TEX']      = dictDocConfig['TEX']

      # get keys and values from documentation build configuration for values with placeholder (in "TOC", "PARAMS" and "DOCUMENT")
      # and resolve placeholder (possible placeholder are the keys from repository configuration)

      self.__dictConfig['TOC'] = dictDocConfig['TOC']
      listDocumentParts = self.__dictConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPart in listDocumentParts:
         sDocumentPartPath = self.__dictConfig['TOC'][sDocumentPart]
         for repo_key, repo_value in dictRepositoryConfig.items():
            if type(repo_value) == str:
               sDocumentPartPath = sDocumentPartPath.replace(f"###{repo_key}###", repo_value)
         self.__dictConfig['TOC'][sDocumentPart] = sDocumentPartPath

      self.__dictConfig['PARAMS'] = {}
      if 'PARAMS' in dictDocConfig: # option
         for doc_key, doc_value in dictDocConfig['PARAMS'].items():
            # print(f"==================== doc_key : '{doc_key}'")
            # print(f"==================== doc_value : '{doc_value}'")
            sResolvedValue = str(doc_value) # TODO: other types required?
            sResolvedValue = sResolvedValue.replace("###NOW###", self.__dictConfig['NOW'])
            for repo_key, repo_value in dictRepositoryConfig.items():
               # print(f"==================== repo_key : '{repo_key}'")
               # print(f"==================== repo_value : '{repo_value}'")
               if type(repo_value) == str:
                  sResolvedValue = sResolvedValue.replace(f"###{repo_key}###", repo_value)
            self.__dictConfig['PARAMS'][doc_key] = sResolvedValue

      self.__dictConfig['DOCUMENT'] = {}
      if 'DOCUMENT' in dictDocConfig: # required; TODO: error handling
         for doc_key, doc_value in dictDocConfig['DOCUMENT'].items():
            # print(f"==================== doc_key : '{doc_key}'")
            # print(f"==================== doc_value : '{doc_value}'")
            sResolvedValue = str(doc_value) # TODO: other types required?
            sResolvedValue = sResolvedValue.replace("###NOW###", self.__dictConfig['NOW'])
            for repo_key, repo_value in dictRepositoryConfig.items():
               # print(f"==================== repo_key : '{repo_key}'")
               # print(f"==================== repo_value : '{repo_value}'")
               if type(repo_value) == str:
                  sResolvedValue = sResolvedValue.replace(f"###{repo_key}###", repo_value)
            self.__dictConfig['DOCUMENT'][doc_key] = sResolvedValue

      # -- the absolute path that is reference for all relative paths
      sReferencePathAbs = self.__dictConfig['PACKAGEDOC']

      # -- convert relative paths to absolute paths in 'DOCUMENTPARTS' section
      listDocumentParts = self.__dictConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPart in listDocumentParts:
         self.__dictConfig['TOC'][sDocumentPart] = CString.NormalizePath(f"{sReferencePathAbs}/{self.__dictConfig['TOC'][sDocumentPart]}")

      # -- set further config keys
      tupleFurtherConfigKeys = ("PICTURES", "OUTPUT", "PDFDEST")

      # -- resolve placeholder in further config keys (possible placeholder are the keys from repository configuration)
      for sConfigKey in tupleFurtherConfigKeys:
         sPackageDocValue = self.__dictConfig[sConfigKey]
         for repo_key, repo_value in dictRepositoryConfig.items():
            if type(repo_value) == str:
               sPackageDocValue = sPackageDocValue.replace(f"###{repo_key}###", repo_value)
         self.__dictConfig[sConfigKey] = sPackageDocValue

      # -- convert relative paths to absolute paths in further config keys
      for sConfigKey in tupleFurtherConfigKeys:
         self.__dictConfig[sConfigKey] = CString.NormalizePath(f"{sReferencePathAbs}/{self.__dictConfig[sConfigKey]}")

      # PrettyPrint(self.__dictConfig, sPrefix="Config")

      # ---- prepare dictionary with all parameter that shall have runtime character (flat list instead of nested dict like in packagedoc configuration)

      self.__dictRuntimeVariables = None

      # -- 1. from repository configuration
      self.__dictRuntimeVariables = oRepositoryConfig.GetConfig()

      # -- 2. current timestamp
      self.__dictRuntimeVariables['NOW'] = self.__dictConfig['NOW']

      # -- 3. from packagedoc configuration
      #       a) user defined parameter
      if 'PARAMS' in self.__dictConfig: # option
         for key, value in self.__dictConfig['PARAMS'].items():
            self.__dictRuntimeVariables[key] = value
      #       b) document ralated parameter
      if 'DOCUMENT' in self.__dictConfig: # required
         for key, value in self.__dictConfig['DOCUMENT'].items():
            self.__dictRuntimeVariables[key] = value

      # TODO: else: error

      # PrettyPrint(self.__dictRuntimeVariables, sPrefix="Runtime")

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
   def __GetModulesList(self, sRootPath=None):
      """Computes a list of all Python modules found recursively within ``sRootPath``.
      """

      sMethod = "__GetModulesList"

      # TODO: error if sRootPath=None

      tupleSubfoldersToExclude = (".git", "__pycache__") # TODO: make this a configuration parameter

      bSuccess = None
      sResult  = None

      listModules = []

      # print(f"========== sRootPath : '{sRootPath}'")

      for sLocalRootPath, listFolderNames, listFileNames in os.walk(sRootPath):
         # print(f"========== sLocalRootPath : '{sLocalRootPath}'")
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
   def __ResolvePlaceholders(self, listLines=[]):
      """Resolves placeholders used in packagedoc configuration (json file)
      """

      sMethod = "__ResolvePlaceholders"

      bSuccess = None
      sResult  = None

      listLinesResolved = []

      # self.__dictRuntimeVariables
      for sLine in listLines:
         sLineResolved = sLine
         for key, value in self.__dictRuntimeVariables.items():
            if type(value) == str:
               sLineResolved = sLineResolved.replace(f"###{key}###", value)
         listLinesResolved.append(sLineResolved)

      bSuccess = True
      sResult  = "Placeholders resolved"

      return listLinesResolved, bSuccess, sResult

   # eof def __ResolvePlaceholders(self, listLines=[]):

   # --------------------------------------------------------------------------------------------------------------
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
            # print("---------- LINE: '" + sLine + "'")
            sLine = self.__dictPlaceholder['newpage']
         elif ( (len(sLine) > 1) and sLine.endswith('/') and not sLine.endswith('//') ):
            # print("---------- LINE: '" + sLine + "'")
            sLine = sLine[:-1] + self.__dictPlaceholder['newline']
         listLinesProcessed.append(sLine)

      return listLinesProcessed

   # eof def __PostprocessRST(self, listLines=[]):

   # --------------------------------------------------------------------------------------------------------------
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
         # print("---------- LINE in listLinesTEX: '" + sLine + "'")
         sLine = sLine.replace(self.__dictPlaceholder['vspace'], r"\vspace{1ex}")
         sLine = sLine.replace(self.__dictPlaceholder['newpage'], r"\newpage")
         sLine = sLine.replace(self.__dictPlaceholder['newline'], r"\newline")
         listLinesProcessed.append(sLine)

      sTEXCode = "\n".join(listLinesProcessed)

      for sHypertarget in self.__regex_hypertarget.findall(sTEXCode):
         # print(f"==================== sHypertarget : '{sHypertarget}'")
         listNames = self.__regex_Name.findall(sHypertarget)
         if len(listNames) == 1:
            sName = f"{listNames[0]}"
            # print(f"          > sName : '{sName}'")
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
               sName_new = "-".join(listNameNew)
               # print(f"          > sName_new : '{sName_new}'")
               sHypertarget_new = sHypertarget.replace(sName, sName_new)
               # print(f"          > sHypertarget_new : '{sHypertarget_new}'")
               sTEXCode = sTEXCode.replace(sHypertarget, sHypertarget_new)
      # eof for sHypertarget in self.__regex_hypertarget.findall(sCode):

      for sLabel in self.__regex_label.findall(sTEXCode):
         # print(f"==================== sLabel : '{sLabel}'")
         listNames = self.__regex_Name.findall(sLabel)
         if len(listNames) == 1:
            sName = f"{listNames[0]}"
            # print(f"          > sName : '{sName}'")
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
               # print(f"          > sName_new : '{sName_new}'")
               sLabel_new = sLabel.replace(sName, sName_new)
               # print(f"          > sLabel_new : '{sLabel_new}'")
               sTEXCode = sTEXCode.replace(sLabel, sLabel_new)
      # eof for sLabel in self.__regex_label.findall(sTEXCode):

      listLinesProcessed = sTEXCode.splitlines()

      return listLinesProcessed

   # eof def __PostprocessTEX(self, listLinesTEX=[], sNamePrefix_1=None, sNamePrefix_2=None, bAddNameCounter=False):

   # --------------------------------------------------------------------------------------------------------------
   def __CleanBuildFolder(self):
      """Cleans the build folder (to a avoid a mixture of current and previous results).
The meaning of clean is: *delete*, followed by *create*.
      """

      sMethod = "__CleanBuildFolder"

      bSuccess = None
      sResult  = None

      sBuildDir = self.__dictConfig['OUTPUT']

      if os.path.isdir(sBuildDir) is True:
         print(f"* Deleting folder '{sBuildDir}'")
         print()
         try:
            shutil.rmtree(sBuildDir)
            pass
         except Exception as ex:
            bSuccess = None
            sResult  = str(ex)
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      try:
         os.makedirs(sBuildDir)
      except Exception as ex:
         bSuccess = None
         sResult  = str(ex)
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      bSuccess = True
      sResult  = f"Build folder '{sBuildDir}' cleaned"

      return bSuccess, sResult

   # eof def __CleanBuildFolder(self):

   # --------------------------------------------------------------------------------------------------------------
   def __CopyPictures(self):
      """Copies the pictures folder to the output folder (required to keep relative paths valid also in created tex files)
      """

      sMethod = "__CopyPictures"

      bSuccess = None
      sResult  = None

      # PrettyPrint(self.__dictConfig, sPrefix = "__CopyPictures::dictConfig")

      if "PICTURES" in self.__dictConfig:
         sPicturesSourceDir = self.__dictConfig['PICTURES']

         # print(f"========== sPicturesSourceDir : '{sPicturesSourceDir}'")

         if os.path.isdir(sPicturesSourceDir) is True:

            sDirName = os.path.basename(sPicturesSourceDir)
            sPicturesDestinationDir = f"{self.__dictConfig['OUTPUT']}/{sDirName}"
            # print(f"========== sPicturesDestinationDir : '{sPicturesDestinationDir}'")

            try:
               shutil.copytree(sPicturesSourceDir, sPicturesDestinationDir)
            except Exception as ex:
               bSuccess = None
               sResult  = str(ex)
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            bSuccess = True
            sResult  = f"Pictures folder '{sPicturesSourceDir}' copied to build folder"

         else:
            bSuccess = True
            sResult  = f"No pictures defined, nothing to copy"

      else:
         bSuccess = True
         sResult  = f"No pictures defined, nothing to copy"

      return bSuccess, sResult

   # eof def __CopyPictures(self):

   # --------------------------------------------------------------------------------------------------------------
   def __GenDocPDF(self):
      """Executes the LaTeX compiler to create the PDF file out of the generated source tex files
      """

      sMethod = "__GenDocPDF"

      bSuccess = None
      sResult  = None

      sPDFFileExpected = None
      sLaTeXInterpreter = None

      sPlatformSystem = platform.system()
      sKey = sPlatformSystem.upper()
      if sKey in self.__dictConfig['TEX']:
         sLaTeXInterpreter = CString.NormalizePath(self.__dictConfig['TEX'][sKey])
      else:
         bSuccess = False
         sResult  = f"Platform {sPlatformSystem} not supported."
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sBuildDir = self.__dictConfig['OUTPUT']
      sMainTexFile = self.__dictConfig['sMainTexFile']

      # print(f"========== sMainTexFile : '{sMainTexFile}'")
      # print(f"========== sLaTeXInterpreter : '{sLaTeXInterpreter}'")

      listCmdLineParts = []
      listCmdLineParts.append(f"\"{sLaTeXInterpreter}\"")
      listCmdLineParts.append(f"\"{sMainTexFile}\"")

      sCmdLine = " ".join(listCmdLineParts)
      del listCmdLineParts
      listCmdLineParts = shlex.split(sCmdLine)

      # -- debug
      sCmdLine = " ".join(listCmdLineParts)
      print()
      print("Now executing command line:\n" + sCmdLine)
      print()

      for nDummy in range(2): # call LaTeX compiler 2 times to get TOC and index lists updated properly
         cwd = os.getcwd() # we have to save cwd because later we have to change
         nReturn = ERROR
         try:
            os.chdir(sBuildDir) # otherwise LaTeX compiler is not able to find files inside
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
      sPDFFileExpected = self.__dictConfig['sPDFFileExpected']
      if os.path.isfile(sPDFFileExpected) is True:
         sDestinationPDFFile = f"{self.__dictConfig['PDFDEST']}/{self.__dictConfig['sPDFFileName']}"
         oPDFFile = CFile(sPDFFileExpected)
         bSuccess, sResult = oPDFFile.CopyTo(sDestinationPDFFile, bOverwrite=True)
         del oPDFFile
         if bSuccess is True:
            # replacement for sResult without debug info
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

      sMethod = "Build"

      bSuccess, sResult = self.__CleanBuildFolder()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      bSuccess, sResult = self.__CopyPictures()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sBuildDir = self.__dictConfig['OUTPUT']

      oSourceParser = CSourceParser()

      listoftuplesChaptersInfo = [] # needed for TOC of main TeX file

      # -- check existence of document parts and parse the content

      listDocumentParts = self.__dictConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPart in listDocumentParts:
         sDocumentPartPath = self.__dictConfig['TOC'][sDocumentPart]

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
               sModuleTeXFile = f"{sBuildDir}/{sModuleTeXFileName}"
               # print(f"========== sModuleTeXFile : '{sModuleTeXFile}'")

               sSourceFilesRootFolderName = os.path.basename(sRootPath)
               sPythonModuleImport = ""
               if sModuleFileSubPath == "":
                  sPythonModuleImport = f"{sSourceFilesRootFolderName}.{sModuleFileNameOnly}"
               else:
                  sPythonModuleImport = f"{sSourceFilesRootFolderName}.{sModuleFileSubPath}.{sModuleFileNameOnly}"

               # -- get all informations out of the source file
               dictContent, bSuccess, sResult = oSourceParser.ParseSourceFile(sModule,
                                                                              self.__dictConfig['CONTROL']['INCLUDEPRIVATE'],
                                                                              self.__dictConfig['CONTROL']['INCLUDEUNDOCUMENTED'])
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

                  sClassHeadline1 = f"Class: {sClassName}"
                  listLinesRST.append(sClassHeadline1)
                  sClassHeadline2 = len(sClassHeadline1)*"="
                  listLinesRST.append(sClassHeadline2)
                  listLinesRST.append("")
                  listLinesRST.append(".. code::python")
                  listLinesRST.append("")
                  listLinesRST.append(f"   {sPythonModuleImport}")
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

               # print(f"========== listLinesResolved  : '{listLinesResolved}'")

               sRSTCode = "\n".join(listLinesResolved)
               # print(f"========== sRSTCode  : '{sRSTCode}'")

               # debug
               sRSTCodeFileName = os.path.basename(sModule) + ".rst"
               sRSTCodeFile = f"{sBuildDir}/{sRSTCodeFileName}"
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
               oModuleTeXFile.Write(f"% {sModuleTeXFile}")
               # TODO: generated at ... by ....
               oModuleTeXFile.Append(sTEX)
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
               sTeXFile = f"{sBuildDir}/{sRSTFileNameOnly}.tex"

               listLinesResolved, bSuccess, sResult = self.__ResolvePlaceholders(listLinesRST)
               if bSuccess is not True:
                  return listLinesResolved, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

               # -- rst postprocessing (extended syntax)
               listLinesProcessed = self.__PostprocessRST(listLinesResolved)

               sRSTCode = "\n".join(listLinesProcessed)
               # print(f"========== sRSTCode  : '{sRSTCode}'")

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
               oTeXFile.Write(f"% {sTeXFile}")
               # TODO: generated at ... by ....
               oTeXFile.Append(sTEX)
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
               sDestTeXFile = f"{sBuildDir}/{sTEXFileNameOnly}.tex"
               bSucces, sResult = oTEXFile.CopyTo(sDestTeXFile, bOverwrite=True)
               if bSuccess is not True:
                  return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
               del oTEXFile
               # -- save some infos needed for TOC of main tex file
               listoftuplesChaptersInfo.append((sChaptername, f"{sTEXFileNameOnly}.tex"))

            # eof else - if sDocumentPartPath.lower().endswith('rst'):
         # eof else - if sDocumentPart.startswith("INTERFACE"):
      # eof for sDocumentPart in listDocumentParts:


      # -- finally create the main TeX file and the PDF


      # 1. main text file
      oPatterns = CPatterns()
      sDocumentationTeXFileName = self.__dictConfig['DOCUMENT']['OUTPUTFILENAME']
      sMainTexFile = f"{sBuildDir}/{sDocumentationTeXFileName}"
      self.__dictConfig['sMainTexFile'] = sMainTexFile
      # print(f"========== sMainTexFile : '{sMainTexFile}'")
      oMainTexFile = CFile(sMainTexFile)
      dMainTexFileInfo = oMainTexFile.GetFileInfo()
      sMainTexFileNameOnly = dMainTexFileInfo['sFileNameOnly']
      sPDFFileName = f"{sMainTexFileNameOnly}.pdf"
      sPDFFileExpected = f"{sBuildDir}/{sPDFFileName}"
      self.__dictConfig['sPDFFileName']     = sPDFFileName # used later to copy the file to another location
      self.__dictConfig['sPDFFileExpected'] = sPDFFileExpected # used later to verify the build
      sHeader = oPatterns.GetHeader(sAuthor=self.__dictConfig['DOCUMENT']['AUTHOR'], sTitle=self.__dictConfig['DOCUMENT']['TITLE'], sDate=self.__dictConfig['DOCUMENT']['DATE'])
      oMainTexFile.Write(sHeader)

      # -- add modules to main TeX file
      for sHeadline, sTeXFileName in listoftuplesChaptersInfo:
         sChapter = oPatterns.GetChapter(sHeadline=sHeadline, sDocumentName=sTeXFileName)
         oMainTexFile.Write(sChapter)

      # -- add creation date to main TeX file
      oMainTexFile.Write(r"\vfill")
      oMainTexFile.Write(r"\begin{center}")
      oMainTexFile.Write(r"\begin{tabular}{m{18em}}\hline")
      oMainTexFile.Write(r"   \textbf{" + f"{sPDFFileName}" + r"}\newline")
      oMainTexFile.Write(r"   \textit{Date of creation: " + self.__dictConfig['NOW'] + r"}\\ \hline")
      oMainTexFile.Write(r"\end{tabular}")
      oMainTexFile.Write(r"\end{center}")

      sFooter = oPatterns.GetFooter()
      oMainTexFile.Write(sFooter)

      del oMainTexFile

      # 2. PDF file
      bSuccess, sResult = self.__GenDocPDF()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def Build(self):

   # --------------------------------------------------------------------------------------------------------------

# eof class CDocBuilder():

# --------------------------------------------------------------------------------------------------------------
