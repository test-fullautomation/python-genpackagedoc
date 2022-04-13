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
# CPatterns.py
#
# XC-CT/ECA3-Queckenstedt
#
# 12.04.2022
#
# --------------------------------------------------------------------------------------------------------------

import os, sys


# --------------------------------------------------------------------------------------------------------------

class CPatterns():

   def __init__(self):
      pass

   def __del__(self):
      pass

   def GetHeader(self, sAuthor="", sTitle="", sDate=""):
      """CPatterns method GetHeader
      """
      sHeader = r"""
\documentclass[a4paper,10pt]{report}

\usepackage[bookmarksopen, bookmarksdepth=subsubchapter]{hyperref}
\hypersetup{
    colorlinks,
    citecolor=blue,
    filecolor=blue,
    linkcolor=blue,
    urlcolor=blue,
    final=true
}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage{multirow}
\usepackage{array}
\usepackage{booktabs}
\usepackage{framed}

\setlength{\parindent}{0em}
\setlength{\parskip}{1ex}

% see: https://tex.stackexchange.com/questions/257418/error-tightlist-converting-md-file-into-pdf-using-pandoc
\def\tightlist{}

\begin{document}

\author{###AUTHOR###}
\title{###TITLE###}
\date{###DATE###}

\maketitle

\tableofcontents
      """
      sReturn = sHeader.replace('###AUTHOR###', sAuthor)
      sReturn = sReturn.replace('###TITLE###', sTitle)
      sReturn = sReturn.replace('###DATE###', sDate)
      return sReturn

   # eof def GetHeader(self, sAuthor="", sTitle="", sDate=""):

   # --------------------------------------------------------------------------------------------------------------

   def GetChapter(self, sHeadline="", sDocumentName=""):
      """CPatterns method GetChapter
      """
      sChapter = """
\chapter{###HEADLINE###}
\input{./###DOCUMENTNAME###}
      """
      sHeadline = sHeadline.replace('_', r'\_') # because '_' has special meaning in LaTeX
      sReturn = sChapter.replace('###HEADLINE###', sHeadline)
      sReturn = sReturn.replace('###DOCUMENTNAME###', sDocumentName)
      return sReturn
   # eof def GetChapter(self, sHeadline="", sDocumentName=""):

   # --------------------------------------------------------------------------------------------------------------

   def GetFooter(self):
      """CPatterns method GetFooter
      """
      return "\end{document}"
   # eof def GetFooter(self):

   # --------------------------------------------------------------------------------------------------------------

# eof class CPatterns():

# --------------------------------------------------------------------------------------------------------------

