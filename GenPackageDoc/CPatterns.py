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
# 04.11.2022
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing source patterns used to generate the tex file output.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys

# --------------------------------------------------------------------------------------------------------------

class CPatterns():
   """
The ``CPatterns`` class provides a set of LaTeX source patterns used to generate the tex file output.

All source patterns are accessible by corresponding ``Get`` methods. Some source patterns contain placeholder
that will be replaced by input parameter of the ``Get`` method.
   """

   def GetHeader(self, sTitle="", sVersion="", sAuthor="", sDate=""):
      """
Defines the header of the main tex file.

**Arguments:**

* ``sTitle``

  / *Condition*: required / *Type*: str /

  The title of the output document (name of the described package)

* ``sVersion``

  / *Condition*: required / *Type*: str /

  The version of the output document (version of the described package)

* ``sAuthor``

  / *Condition*: required / *Type*: str /

  The author of the output document (author of the described package)

* ``sDate``

  / *Condition*: required / *Type*: str /

  The date of the output document (date of the described package)

**Returns:**

* ``sHeader``

  / *Type*: str /

  LaTeX code containing the header of main tex file.
      """

      sHeader = r"""
\documentclass[a4paper,10pt]{report}

% --------------------------------------------------------------------------------------------------------------
% preamble
% --------------------------------------------------------------------------------------------------------------

\input{./styles/preamble}

% --------------------------------------------------------------------------------------------------------------
% title
% --------------------------------------------------------------------------------------------------------------

\title{\textbf{###TITLE###}\\
\vspace{2ex}
\textbf{v. ###VERSION###}}

\author{###AUTHOR###}

\date{###DATE###}

% --------------------------------------------------------------------------------------------------------------
% document
% --------------------------------------------------------------------------------------------------------------

\begin{document}

\hypersetup{pageanchor=false}

\maketitle

\clearpage
\pagenumbering{Alph}
\tableofcontents

\clearpage
\pagenumbering{arabic}

\hypersetup{pageanchor=true}

      """
      sTitle  = sTitle.replace('_', r'\_') # LaTeX requires this masking
      sReturn = sHeader.replace('###TITLE###',   sTitle)
      sReturn = sReturn.replace('###VERSION###', sVersion)
      sReturn = sReturn.replace('###AUTHOR###',  sAuthor)
      sReturn = sReturn.replace('###DATE###',    sDate)
      return sReturn

   # eof def GetHeader(self, sTitle="", sVersion="", sAuthor="", sDate=""):

   # --------------------------------------------------------------------------------------------------------------

   def GetChapter(self, sHeadline="", sLabel="", sDocumentName=""):
      """
Defines single chapter of the main tex file.

A single chapter is equivalent to an additionally imported text file in rst format or equivalent to a single Python module
within a Python package.

**Arguments:**

* ``sHeadline``

  / *Condition*: required / *Type*: str /

  The chapter headline (that is either the name of an additional rst file or the name of a Python module).

* ``sLabel``

  / *Condition*: required / *Type*: str /

  The chapter label (to enable linking to this chapter)

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
\chapter{###HEADLINE###}\label{###LABEL###}
\input{./###DOCUMENTNAME###}
      """
      sHeadline = sHeadline.replace('_', r'\_') # because '_' has special meaning in LaTeX
      sReturn = sChapter.replace('###HEADLINE###', sHeadline)
      sReturn = sReturn.replace('###LABEL###', sLabel)
      sReturn = sReturn.replace('###DOCUMENTNAME###', sDocumentName)
      return sReturn
   # eof def GetChapter(self, sHeadline="", sLabel="", sDocumentName=""):

   # --------------------------------------------------------------------------------------------------------------

   def GetFooter(self):
      """
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

   def GetAutodefinedHeader(self, sTimestamp=""):
      """
Defines the header of the autodefined LaTeX sty file.

**Arguments:**

(*no arguments*)

**Returns:**

* ``sAutodefinedHeader``

  / *Type*: str /

  LaTeX code containing the header of the autodefined LaTeX sty file.
      """

      sAutodefinedHeader = r"""% --------------------------------------------------------------------------------------------------------------
%
% Copyright 2020-2022 Robert Bosch GmbH

% Licensed under the Apache License, Version 2.0 (the "License");
% you may not use this file except in compliance with the License.
% You may obtain a copy of the License at

% http://www.apache.org/licenses/LICENSE-2.0

% Unless required by applicable law or agreed to in writing, software
% distributed under the License is distributed on an "AS IS" BASIS,
% WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
% See the License for the specific language governing permissions and
% limitations under the License.
%
% --------------------------------------------------------------------------------------------------------------
%
% autodefined.sty
%
% Contains auto generated mnemotechnical commands to type the repository name and the package name.
%
% Generated by GenPackageDoc at ###TIMESTAMP###
%
% --------------------------------------------------------------------------------------------------------------
%
"""

      sAutodefinedHeader = sAutodefinedHeader.replace('###TIMESTAMP###', sTimestamp)
      return sAutodefinedHeader
   # eof def GetAutodefinedHeader(self, sTimestamp=""):

   # --------------------------------------------------------------------------------------------------------------

# eof class CPatterns():

# --------------------------------------------------------------------------------------------------------------

