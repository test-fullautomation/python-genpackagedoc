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
# 13.04.2022
#
# --------------------------------------------------------------------------------------------------------------

import os, sys

# --------------------------------------------------------------------------------------------------------------

class CPatterns():
   """
Class: CPatterns
================

The ``CPatterns`` class provides a set of LaTeX source patterns used to generate the tex file output.

All source patterns are accessible by corresponding ``Get`` methods. Some source patterns contain placeholder
that will be replaced by input parameter of the ``Get`` method.
   """

   def GetHeader(self, sAuthor="", sTitle="", sDate=""):
      """
Method: GetHeader
-----------------

Defines the header of the main tex file.

**Arguments:**

* ``sAuthor``

  / *Condition*: required / *Type*: str /

  The author of the package

* ``sTitle``

  / *Condition*: required / *Type*: str /

  The title of the output document

* ``sDate``

  / *Condition*: required / *Type*: str /

  The date of the output document

**Returns:**

* ``sHeader``

  / *Type*: str /

  LaTeX code containing the header of main tex file.
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
      """
Method: GetChapter
------------------

Defines single chapter of the main tex file.

A single chapter is equivalent to an additionally imported text file in rst format or equivalent to a single Python module
within a Python package.

**Arguments:**

* ``sHeadline``

  / *Condition*: required / *Type*: str /

  The chapter headline (that is either the name of an additional rst file or the name of a Python module).

* ``sDocumentName``

  / *Condition*: required / *Type*: str /

  The name of a single tex file containing the chapter content. This file is imported in the main text file after the chapter headline
  that is set by ``sHeadline``.

**Returns:**

* ``sHeader``

  / *Type*: str /

  LaTeX code containing the headline and the input of a single tex file.
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
      """
Method: GetFooter
-----------------

Defines the footer of the main tex file.

**Arguments:**

(*no arguments*)

**Returns:**

* ``sFooter``

  / *Type*: str /

  LaTeX code containing the footer of the main tex file.
      """

      sFooter = r"\end{document}"
      return sFooter
   # eof def GetFooter(self):

   # --------------------------------------------------------------------------------------------------------------

# eof class CPatterns():

# --------------------------------------------------------------------------------------------------------------

