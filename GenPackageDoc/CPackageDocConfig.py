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
# CPackageDocConfig.py
#
# XC-CT/ECA3-Queckenstedt
#
# 17.03.2023
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing the configuration for **GenPackageDoc**. This includes the repository configurantion
and command line values.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, platform, json, argparse
import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
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

def printerror(sMsg):
    sys.stderr.write(COLBR + f"Error: {sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------

class CPackageDocConfig():

   def __init__(self, oRepositoryConfig=None):
      """
Constructor of class ``CPackageDocConfig``.

Responsible for:

* Take over the repository configuration
* Read the packagedoc configuration from json file
* Resolve placeholders used in packagedoc configuration
* Prepare runtime variables

* ``oRepositoryConfig``

  / *Condition*: required / *Type*: CRepositoryConfig() /

  **GenPackageDoc** configuration containing static and dynamic configuration values (this includes the
  Repository configuration).
      """

      sMethod = "CPackageDocConfig.__init__"

      self.__dictPackageDocConfig = None  # self.__dictConfig

      if oRepositoryConfig is None:
         bSuccess = None
         sResult  = "oRepositoryConfig is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # get repository configuration
      dictRepositoryConfig = oRepositoryConfig.GetConfig()

      # read the documentation build configuration from separate json file
      #    - the path to the folder containing this json file is taken out of the repository configuration
      #    - the name of the json file is fix
      sJsonFileName = "packagedoc_config.json"
      sDocumentationProjectConfigFile = f"{dictRepositoryConfig['PACKAGEDOC']}/{sJsonFileName}"

      # The json file may contain lines that are commented out by a '#' at the beginning of the line.
      # Therefore we read in this file in text format, remove the comments and save the cleaned file within the temp folder.
      # Now it's a valid json file and we read the file from there.

      sTmpPath = None
      sPlatformSystem = platform.system()
      if sPlatformSystem == "Windows":
         sTmpPath = CString.NormalizePath("%TMP%")
      elif sPlatformSystem == "Linux":
         sTmpPath = "/tmp"
      else:
         bSuccess = None
         sResult  = f"Platform system '{sPlatformSystem}' is not supported"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      sJsonFileCleaned = f"{sTmpPath}/{sJsonFileName}"

      oJsonFileSource = CFile(sDocumentationProjectConfigFile)
      listLines, bSuccess, sResult = oJsonFileSource.ReadLines(bSkipBlankLines=True, sComment='#')
      del oJsonFileSource
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      oJsonFileCleaned = CFile(sJsonFileCleaned)
      bSuccess, sResult = oJsonFileCleaned.Write(listLines)
      del oJsonFileCleaned
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      dictJsonValues = {}
      try:
         hDocumentationProjectConfigFile = open(sJsonFileCleaned)
         dictJsonValues = json.load(hDocumentationProjectConfigFile)
         hDocumentationProjectConfigFile.close()
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason) + f" - while reading from '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # check for unexpected keys
      tupleKeysAllowedInPackageDocConfig = ("CONTROL",
                                            "TOC",
                                            "PARAMS",
                                            "DOCUMENT",
                                            "PICTURES",
                                            "OUTPUT",
                                            "PDFDEST",
                                            "CONFIGDEST",
                                            "TEX")

      for sKey in dictJsonValues.keys():
         if sKey not in tupleKeysAllowedInPackageDocConfig:
            bSuccess = None
            sResult  = f"Found not expected key '{sKey}' within '{sDocumentationProjectConfigFile}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # initialize the documentation build configuration including the repository configuration (with placeholders resolved)
      # together with command line parameters. Command overwrites all other values.
      self.__dictPackageDocConfig = {}

      # take over keys and values from repository configuration
      for key, value in dictRepositoryConfig.items():
         self.__dictPackageDocConfig[key] = value

      # add current timestamp
      self.__dictPackageDocConfig['NOW'] = time.strftime('%d.%m.%Y - %H:%M:%S')

      # -- get keys and values from static documentation build configuration (json file),
      #    distingushing between required and optional parameters and checking the
      #    availability of mandatory values
      # TODO: Moo much for a constructor? Move to separate method? Better ways to
      #       validate the content in json file?

      # required
      if 'CONTROL' in dictJsonValues:
         self.__dictPackageDocConfig['CONTROL']  = dictJsonValues['CONTROL']
      else:
         bSuccess = None
         sResult  = f"Missing key 'CONTROL' within '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      # ==============================================================================================================
      # 21.11.2022 Feature 'INCLUDEPRIVATE' switched off. TODO: needs several bugfixes
      self.__dictPackageDocConfig['CONTROL']['INCLUDEPRIVATE'] = False
      # ==============================================================================================================
      bSuccess, sResult = self.__CheckElements(('INCLUDEPRIVATE','INCLUDEUNDOCUMENTED','STRICT'), self.__dictPackageDocConfig['CONTROL'].keys(), "subkey")
      if bSuccess is not True:
         sResult = sResult + f"\nWhile reading from '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # required
      if 'TOC' in dictJsonValues:
         self.__dictPackageDocConfig['TOC'] = dictJsonValues['TOC']
      else:
         bSuccess = None
         sResult  = f"Missing key 'TOC' within '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      if not 'DOCUMENTPARTS' in self.__dictPackageDocConfig['TOC']:
         bSuccess = None
         sResult  = f"Missing subkey 'DOCUMENTPARTS' within '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # optional
      if 'PARAMS' in dictJsonValues:
         self.__dictPackageDocConfig['PARAMS'] = dictJsonValues['PARAMS']
      else:
         self.__dictPackageDocConfig['PARAMS'] = None

      # required
      if 'DOCUMENT' in dictJsonValues:
         self.__dictPackageDocConfig['DOCUMENT'] = dictJsonValues['DOCUMENT']
      else:
         bSuccess = None
         sResult  = f"Missing key 'DOCUMENT' within '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      bSuccess, sResult = self.__CheckElements(('OUTPUTFILENAME','AUTHOR','TITLE','DATE','VERSION'), self.__dictPackageDocConfig['DOCUMENT'].keys(), "subkey")
      if bSuccess is not True:
         sResult = sResult + f"\nWhile reading from '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # optional
      if 'PICTURES' in dictJsonValues:
         self.__dictPackageDocConfig['PICTURES'] = dictJsonValues['PICTURES']
      else:
         self.__dictPackageDocConfig['PICTURES'] = None

      # required
      if 'OUTPUT' in dictJsonValues:
         self.__dictPackageDocConfig['OUTPUT'] = dictJsonValues['OUTPUT']
      else:
         bSuccess = None
         sResult  = f"Missing key 'OUTPUT' within '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # optional
      if 'PDFDEST' in dictJsonValues:
         self.__dictPackageDocConfig['PDFDEST'] = dictJsonValues['PDFDEST']
      else:
         self.__dictPackageDocConfig['PDFDEST'] = None

      # optional
      if 'CONFIGDEST' in dictJsonValues:
         self.__dictPackageDocConfig['CONFIGDEST'] = dictJsonValues['CONFIGDEST']
      else:
         self.__dictPackageDocConfig['CONFIGDEST'] = None

      # required
      if 'TEX' in dictJsonValues:
         self.__dictPackageDocConfig['TEX'] = dictJsonValues['TEX']
      else:
         bSuccess = None
         sResult  = f"Missing key 'TEX' within '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # Now we have all configuration values available in self.__dictPackageDocConfig. Next steps are:
      # - resolve placeholders (possible placeholders are the keys from repository configuration)
      # - normalize paths

      # - check document parts in TOC section
      listDocumentPartsDefined = self.__dictPackageDocConfig['TOC'].keys()
      listDocumentPartsUsed = self.__dictPackageDocConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPartUsed in listDocumentPartsUsed:
         if sDocumentPartUsed not in listDocumentPartsDefined:
            bSuccess = None
            sResult  = f"Document part '{sDocumentPartUsed}' not defined within 'TOC' section of '{sDocumentationProjectConfigFile}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # - placeholder in TOC section
      listDocumentParts = self.__dictPackageDocConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPart in listDocumentParts:
         sDocumentPartPath = self.__dictPackageDocConfig['TOC'][sDocumentPart]
         for repo_key, repo_value in dictRepositoryConfig.items():
            if type(repo_value) == str:
               sDocumentPartPath = sDocumentPartPath.replace(f"###{repo_key}###", repo_value)
         self.__dictPackageDocConfig['TOC'][sDocumentPart] = sDocumentPartPath

      # - placeholder in PARAMS section
      if self.__dictPackageDocConfig['PARAMS'] is not None:
         for doc_key, doc_value in self.__dictPackageDocConfig['PARAMS'].items():
            sResolvedValue = str(doc_value)
            sResolvedValue = sResolvedValue.replace("###NOW###", self.__dictPackageDocConfig['NOW'])
            for repo_key, repo_value in dictRepositoryConfig.items():
               if type(repo_value) == str:
                  sResolvedValue = sResolvedValue.replace(f"###{repo_key}###", repo_value)
            self.__dictPackageDocConfig['PARAMS'][doc_key] = sResolvedValue

      # - placeholder in DOCUMENT section
      for doc_key, doc_value in self.__dictPackageDocConfig['DOCUMENT'].items():
         sResolvedValue = str(doc_value) # TODO: other types required?
         sResolvedValue = sResolvedValue.replace("###NOW###", self.__dictPackageDocConfig['NOW'])
         for repo_key, repo_value in dictRepositoryConfig.items():
            if type(repo_value) == str:
               sResolvedValue = sResolvedValue.replace(f"###{repo_key}###", repo_value)
         self.__dictPackageDocConfig['DOCUMENT'][doc_key] = sResolvedValue

      # the absolute path that is reference for all relative paths
      sReferencePathAbs = self.__dictPackageDocConfig['PACKAGEDOC'] # set initially in repository config and already normalized

      # - normalize paths in 'DOCUMENTPARTS' section
      listDocumentParts = self.__dictPackageDocConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPart in listDocumentParts:
         self.__dictPackageDocConfig['TOC'][sDocumentPart] = CString.NormalizePath(sPath=self.__dictPackageDocConfig['TOC'][sDocumentPart], sReferencePathAbs=sReferencePathAbs)

      # -- set further config keys (to enable the resolve of placeholders and the normalizing of paths running in a loop)
      tupleFurtherConfigKeys = ('PICTURES', 'OUTPUT', 'PDFDEST', 'CONFIGDEST') # values contain paths and can contain placeholders; some of them are optional
      # -- resolve placeholder and normalize paths
      for sConfigKey in tupleFurtherConfigKeys:
         sPackageDocValue = self.__dictPackageDocConfig[sConfigKey]
         if sPackageDocValue is not None:
            # resolve placeholder in further config keys (possible placeholder are the keys from repository configuration)
            for repo_key, repo_value in dictRepositoryConfig.items():
               if type(repo_value) == str:
                  sPackageDocValue = sPackageDocValue.replace(f"###{repo_key}###", repo_value)

            # normalize path and write value back to dict
            self.__dictPackageDocConfig[sConfigKey] = CString.NormalizePath(sPath=sPackageDocValue, sReferencePathAbs=sReferencePathAbs)

      # -- prepare path to LaTeX interpreter
      sLaTeXInterpreter = None
      sKey = sPlatformSystem.upper()
      if sKey in self.__dictPackageDocConfig['TEX']:
         sLaTeXInterpreter = CString.NormalizePath(sPath=self.__dictPackageDocConfig['TEX'][sKey], sReferencePathAbs=sReferencePathAbs)
      else:
         bSuccess = None
         sResult  = f"LaTeX interpreter not defined for current operating system '{sPlatformSystem}' in section 'TEX' of '{sDocumentationProjectConfigFile}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      self.__dictPackageDocConfig['LATEXINTERPRETER'] = sLaTeXInterpreter

      # -- prepare path to additional LaTeX stylesheets (expected to be at a position relative to this module, because these stylesheets are part of the installation!)
      sThisFile = CString.NormalizePath(sPath=__file__, sReferencePathAbs=sReferencePathAbs)
      sThisFilePath = os.path.dirname(sThisFile)
      sStylesFolder = f"{sThisFilePath}/styles"
      if os.path.isdir(sStylesFolder) is False:
         bSuccess = None
         sResult  = f"Missing LaTeX stylesheet folder '{sStylesFolder}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      self.__dictPackageDocConfig['LATEXSTYLESFOLDER'] = sStylesFolder

      # ---- prepare dictionary with all parameter that shall have runtime character (flat list instead of nested dict like in packagedoc configuration)

      dictRuntimeVariables = None

      # -- 1. from repository configuration
      dictRuntimeVariables = oRepositoryConfig.GetConfig()

      # -- 2. current timestamp
      dictRuntimeVariables['NOW'] = self.__dictPackageDocConfig['NOW']

      # -- 3. from packagedoc configuration
      #       a) user defined parameter
      if self.__dictPackageDocConfig['PARAMS'] is not None:
         for key, value in self.__dictPackageDocConfig['PARAMS'].items():
            dictRuntimeVariables[key] = value
      #       b) document related parameter
      for key, value in self.__dictPackageDocConfig['DOCUMENT'].items():
         dictRuntimeVariables[key] = value

      # PrettyPrint(dictRuntimeVariables, sPrefix="RuntimeVariables")

      self.__dictPackageDocConfig['dictRuntimeVariables'] = dictRuntimeVariables

      # parse command line arguments
      bSuccess, sResult = self.__GetCmdLineArgs()
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # PrettyPrint(self.__dictPackageDocConfig, sPrefix="Config")

   # eof def __init__(self, oRepositoryConfig=None):

   def __del__(self):
      del self.__dictPackageDocConfig


   def __CheckElements(self, listExpected=[], listAvailable=[], sElementName="element"):
      """
Cross check:
* Only expected elements available? 
* All expected elements available? 
      """
      sMethod  = "CPackageDocConfig.__CheckElements"
      bSuccess = False
      sResult  = "UNKNOWN"
      if listExpected is None:
         bSuccess = None
         sResult  = "listExpected is None"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      if listAvailable is None:
         bSuccess = None
         sResult  = "listAvailable is None"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      if len(listExpected) == 0:
         bSuccess = False
         sResult  = f"The list of expected {sElementName}s is empty"
         return bSuccess, sResult
      if len(listAvailable) == 0:
         bSuccess = False
         sResult  = f"The list of available {sElementName}s is empty"
         return bSuccess, sResult

      listMissing = []
      for element in listExpected:
         if element not in listAvailable:
            listMissing.append(str(element)) # convert to string because this is only for printing out error messages
      listNotExpected = []
      for element in listAvailable:
         if element not in listExpected:
            listNotExpected.append(str(element)) # convert to string because this is only for printing out error messages

      bSuccess = False
      listResults = []
      if ( (len(listMissing) == 0) and (len(listNotExpected) == 0) ):
         bSuccess = True
         sResult  = f"All expected {sElementName}s available; no unexpected {sElementName} found"
         listResults.append(sResult)
      else:
         if len(listMissing) > 0:
            bSuccess = False
            sResult  = f"The following {sElementName}s are expected but not found: [" + ", ".join(listMissing) + "]"
            listResults.append(sResult)
         if len(listNotExpected) > 0:
            bSuccess = False
            sResult  = f"The following {sElementName}s have been found but are not expected: [" + ", ".join(listNotExpected) + "]"
            listResults.append(sResult)
      sResult = "\n".join(listResults)
      return bSuccess, sResult

   # eof def __CheckElements(self, listAvailable=[], listExpected=[], sElementName="element"):


   def PrintConfig(self):
      """
Prints all cofiguration values to console.
      """
      # -- printing configuration to console
      print()
      PrettyPrint(self.__dictPackageDocConfig, sPrefix="PackageDocConfig")
      print()
   # eof def PrintConfig(self):


   def PrintConfigKeys(self):
      """
Prints all cofiguration key names to console.
      """
      # -- printing configuration keys to console
      print()
      listKeys = self.__dictPackageDocConfig.keys()
      sKeys = "[" + ", ".join(listKeys) + "]"
      print(sKeys)
      print()
   # eof def PrintConfigKeys(self):


   def Get(self, sName=None):
      """
Returns the configuration value belonging to a key name.
      """
      if ( (sName is None) or (sName not in self.__dictPackageDocConfig) ):
         print()
         printerror(f"Configuration parameter '{sName}' not existing")
         # from here it's standard output:
         print()
         print("Use instead one of:")
         self.PrintConfigKeys()
         return None # returning 'None' in case of key is not existing !!!
      else:
         return self.__dictPackageDocConfig[sName]
   # eof def Get(self, sName=None):


   def GetConfig(self):
      """
Returns the complete configuration dictionary.
      """
      return self.__dictPackageDocConfig
   # eof def GetConfig(self):


   def __GetCmdLineArgs(self):
      """
Get values fom command linwe and add them to **GenPackageDoc** configuration. Already existing configuration values will be overwritten.
      """

      sMethod = "CPackageDocConfig.__GetCmdLineArgs"

      bSuccess = False
      sResult  = "UNKNOWN"

      sReferencePathAbs = self.__dictPackageDocConfig['PACKAGEDOC'] # set initially in repository config and already normalized

      oCmdLineParser = argparse.ArgumentParser()

      # -- configuration parameter, that can be overwritten in command line (where it makes sense)
      oCmdLineParser.add_argument('--output', type=str, help='Path and name of folder containing all output files.')
      oCmdLineParser.add_argument('--pdfdest', type=str, help='Path and name of folder in which the generated PDF file will be copied to.')
      oCmdLineParser.add_argument('--configdest', type=str, help='Path and name of folder in which the configuration files will be copied to.')
      oCmdLineParser.add_argument('--strict', help='If True, a missing LaTeX compiler aborts the process, otherwise the process continues.')
      oCmdLineParser.add_argument('--simulateonly', action='store_true', help='If True, the LaTeX compiler is switched off; a syntax check only remains in this case. Default: False')

      oCmdLineArgs = oCmdLineParser.parse_args()

      OUTPUT = None
      if oCmdLineArgs.output != None:
         OUTPUT = oCmdLineArgs.output
         if OUTPUT == "":
            bSuccess = False
            sResult  = "Empty command line argument: -output."
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            OUTPUT = CString.NormalizePath(sPath=OUTPUT, sReferencePathAbs=sReferencePathAbs)
            self.__dictPackageDocConfig['OUTPUT'] = OUTPUT
            print(COLNY + f"<'OUTPUT' redirected to '{OUTPUT}'>\n")

      PDFDEST = None
      if oCmdLineArgs.pdfdest != None:
         PDFDEST = oCmdLineArgs.pdfdest
         if PDFDEST == "":
            bSuccess = False
            sResult  = "Empty command line argument: -pdfdest."
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            PDFDEST = CString.NormalizePath(sPath=PDFDEST, sReferencePathAbs=sReferencePathAbs)
            self.__dictPackageDocConfig['PDFDEST'] = PDFDEST
            print(COLNY + f"<'PDFDEST' redirected to '{PDFDEST}'>\n")

      CONFIGDEST = None
      if oCmdLineArgs.configdest != None:
         CONFIGDEST = oCmdLineArgs.configdest
         if CONFIGDEST == "":
            bSuccess = False
            sResult  = "Empty command line argument: -configdest."
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            CONFIGDEST = CString.NormalizePath(sPath=CONFIGDEST, sReferencePathAbs=sReferencePathAbs)
            self.__dictPackageDocConfig['CONFIGDEST'] = CONFIGDEST
            print(COLNY + f"<'CONFIGDEST' redirected to '{CONFIGDEST}'>\n")

      STRICT = None
      if oCmdLineArgs.strict != None:
         STRICT = oCmdLineArgs.strict
         if ( (STRICT == "true") or (STRICT == "True") ):
            self.__dictPackageDocConfig['CONTROL']['STRICT'] = True
            print(COLNY + "<'STRICT' set to True>\n")
         elif ( (STRICT == "false") or (STRICT == "False") ):
            self.__dictPackageDocConfig['CONTROL']['STRICT'] = False
            print(COLNY + "<'STRICT' set to False>\n")

      bSimulateOnly = False
      if oCmdLineArgs.simulateonly is not None:
         bSimulateOnly = oCmdLineArgs.simulateonly
      self.__dictPackageDocConfig['bSimulateOnly'] = bSimulateOnly
      if bSimulateOnly is True:
         print(COLNY + "<running in simulation mode>\n")


      bSuccess = True
      sResult  = "Done"
      return bSuccess, sResult

   # eof def __GetCmdLineArgs():

# eof class CPackageDocConfig(): 

# **************************************************************************************************************


