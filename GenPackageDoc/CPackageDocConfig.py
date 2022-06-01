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
# 01.06.2022
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing the configuration for GenPackageDoc. This includes the repository configurantion
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

  GenPackageDoc configuration containing static and dynamic configuration values (this includes the
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
      else:
         bSuccess = None
         sResult  = f"Platform system '{sPlatformSystem}' is not supported"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

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
      dictJsonValues = None # dictDocConfig
      hDocumentationProjectConfigFile = open(sJsonFileCleaned)
      dictJsonValues = json.load(hDocumentationProjectConfigFile)
      hDocumentationProjectConfigFile.close()

      # initialize the documentation build configuration including the repository configuration (with placeholders resolved)
      # together with command line parameters. Command overwrites all other values.
      self.__dictPackageDocConfig = {}

      # take over keys and values from repository configuration
      for key, value in dictRepositoryConfig.items():
         self.__dictPackageDocConfig[key] = value

      # add current timestamp
      self.__dictPackageDocConfig['NOW'] = time.strftime('%d.%m.%Y - %H:%M:%S')

      # get some basic keys and values from documentation build configuration
      # TODO: if key in dict / otherwise error / or make optional?
      self.__dictPackageDocConfig['CONTROL']  = dictJsonValues['CONTROL']
      self.__dictPackageDocConfig['PICTURES'] = dictJsonValues['PICTURES']
      self.__dictPackageDocConfig['OUTPUT']   = dictJsonValues['OUTPUT']
      self.__dictPackageDocConfig['PDFDEST']  = dictJsonValues['PDFDEST']
      self.__dictPackageDocConfig['TEX']      = dictJsonValues['TEX']

      # get keys and values from documentation build configuration for values with placeholder (in 'TOC', 'PARAMS' and 'DOCUMENT')
      # and resolve placeholder (possible placeholder are the keys from repository configuration)

      self.__dictPackageDocConfig['TOC'] = dictJsonValues['TOC']
      listDocumentParts = self.__dictPackageDocConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPart in listDocumentParts:
         sDocumentPartPath = self.__dictPackageDocConfig['TOC'][sDocumentPart]
         for repo_key, repo_value in dictRepositoryConfig.items():
            if type(repo_value) == str:
               sDocumentPartPath = sDocumentPartPath.replace(f"###{repo_key}###", repo_value)
         self.__dictPackageDocConfig['TOC'][sDocumentPart] = sDocumentPartPath

      self.__dictPackageDocConfig['PARAMS'] = {}
      if 'PARAMS' in dictJsonValues: # option
         for doc_key, doc_value in dictJsonValues['PARAMS'].items():
            # print(f"==================== doc_key : '{doc_key}'")
            # print(f"==================== doc_value : '{doc_value}'")
            sResolvedValue = str(doc_value) # TODO: other types required?
            sResolvedValue = sResolvedValue.replace("###NOW###", self.__dictPackageDocConfig['NOW'])
            for repo_key, repo_value in dictRepositoryConfig.items():
               # print(f"==================== repo_key : '{repo_key}'")
               # print(f"==================== repo_value : '{repo_value}'")
               if type(repo_value) == str:
                  sResolvedValue = sResolvedValue.replace(f"###{repo_key}###", repo_value)
            self.__dictPackageDocConfig['PARAMS'][doc_key] = sResolvedValue

      self.__dictPackageDocConfig['DOCUMENT'] = {}
      if 'DOCUMENT' in dictJsonValues: # required; TODO: error handling
         for doc_key, doc_value in dictJsonValues['DOCUMENT'].items():
            # print(f"==================== doc_key : '{doc_key}'")
            # print(f"==================== doc_value : '{doc_value}'")
            sResolvedValue = str(doc_value) # TODO: other types required?
            sResolvedValue = sResolvedValue.replace("###NOW###", self.__dictPackageDocConfig['NOW'])
            for repo_key, repo_value in dictRepositoryConfig.items():
               # print(f"==================== repo_key : '{repo_key}'")
               # print(f"==================== repo_value : '{repo_value}'")
               if type(repo_value) == str:
                  sResolvedValue = sResolvedValue.replace(f"###{repo_key}###", repo_value)
            self.__dictPackageDocConfig['DOCUMENT'][doc_key] = sResolvedValue

      # -- the absolute path that is reference for all relative paths
      sReferencePathAbs = self.__dictPackageDocConfig['PACKAGEDOC'] # set initially in repository config and already normalized

      # -- normalize paths in 'DOCUMENTPARTS' section
      listDocumentParts = self.__dictPackageDocConfig['TOC']['DOCUMENTPARTS']
      for sDocumentPart in listDocumentParts:
         self.__dictPackageDocConfig['TOC'][sDocumentPart] = CString.NormalizePath(sPath=self.__dictPackageDocConfig['TOC'][sDocumentPart], sReferencePathAbs=sReferencePathAbs)

      # -- set further config keys
      tupleFurtherConfigKeys = ('PICTURES', 'OUTPUT', 'PDFDEST')

      # -- resolve placeholder in further config keys (possible placeholder are the keys from repository configuration)
      for sConfigKey in tupleFurtherConfigKeys:
         sPackageDocValue = self.__dictPackageDocConfig[sConfigKey]
         for repo_key, repo_value in dictRepositoryConfig.items():
            if type(repo_value) == str:
               sPackageDocValue = sPackageDocValue.replace(f"###{repo_key}###", repo_value)
         self.__dictPackageDocConfig[sConfigKey] = sPackageDocValue

      # -- normalize paths in further config keys
      for sConfigKey in tupleFurtherConfigKeys:
         self.__dictPackageDocConfig[sConfigKey] = CString.NormalizePath(sPath=self.__dictPackageDocConfig[sConfigKey], sReferencePathAbs=sReferencePathAbs)

      # -- prepare path to LaTeX interpreter
      sLaTeXInterpreter = None
      sKey = sPlatformSystem.upper()
      if sKey in self.__dictPackageDocConfig['TEX']:
         sLaTeXInterpreter = CString.NormalizePath(sPath=self.__dictPackageDocConfig['TEX'][sKey], sReferencePathAbs=sReferencePathAbs)
      self.__dictPackageDocConfig['LATEXINTERPRETER'] = sLaTeXInterpreter

      # -- prepare path to additional LaTeX stylesheets (expected to be at a position relative to this module, because these stylesheets are part of the installation!)
      sThisFile = CString.NormalizePath(sPath=__file__, sReferencePathAbs=sReferencePathAbs)
      sThisFilePath = os.path.dirname(sThisFile)
      sStylesFolder = f"{sThisFilePath}/styles"
      # print(f"============================== sStylesFolder: '{sStylesFolder}'")
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
      if 'PARAMS' in self.__dictPackageDocConfig: # option
         for key, value in self.__dictPackageDocConfig['PARAMS'].items():
            dictRuntimeVariables[key] = value
      #       b) document related parameter
      if 'DOCUMENT' in self.__dictPackageDocConfig: # required
         for key, value in self.__dictPackageDocConfig['DOCUMENT'].items():
            dictRuntimeVariables[key] = value

      # TODO: else: error

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
         printerror(f"Error: Configuration parameter '{sName}' not existing!")
         # from here it's standard output:
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
Get values fom command linwe and add them to GenPackageDoc configuration. Already existing configuration values will be overwritten.
      """

      sMethod = "GetCmdLineArgs"

      bSuccess = False
      sResult  = "UNKNOWN"

      sReferencePathAbs = self.__dictPackageDocConfig['PACKAGEDOC'] # set initially in repository config

      oCmdLineParser = argparse.ArgumentParser()

      # -- configuration parameter, that can be overwritten in command line (where it makes sense)
      oCmdLineParser.add_argument('--output', type=str, help='Path and name of folder containing all output files.')
      oCmdLineParser.add_argument('--pdfdest', type=str, help='Path and name of folder in which the generated PDF file will be copied to.')
      oCmdLineParser.add_argument('--strict', help='If True, a missing LaTeX compiler aborts the process, otherwise the process continues.')

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

      STRICT = None
      if oCmdLineArgs.strict != None:
         STRICT = oCmdLineArgs.strict
         if ( (STRICT == "true") or (STRICT == "True") ):
            self.__dictPackageDocConfig['CONTROL']['STRICT'] = True
            print(COLNY + "<'STRICT' set to True>\n")
         elif ( (STRICT == "false") or (STRICT == "False") ):
            self.__dictPackageDocConfig['CONTROL']['STRICT'] = False
            print(COLNY + "<'STRICT' set to False>\n")

      bSuccess = True
      sResult  = "Done"
      return bSuccess, sResult

   # eof def __GetCmdLineArgs():

# eof class CPackageDocConfig(): 

# **************************************************************************************************************


