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
# 19.05.2022
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

\usepackage[bookmarksopen, bookmarksnumbered, bookmarksdepth=3]{hyperref}
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
\usepackage{fvextra}
\usepackage{courier}
\usepackage{amssymb}
\usepackage{xcolor}

\setlength{\parindent}{0em}
\setlength{\parskip}{1ex}

% see: https://tex.stackexchange.com/questions/257418/error-tightlist-converting-md-file-into-pdf-using-pandoc
\def\tightlist{}

% enable Python syntax highlighting:

\usepackage{color}
\usepackage{fancyvrb}
\newcommand{\VerbBar}{|}
\newcommand{\VERB}{\Verb[commandchars=\\\{\}]}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}
% Add ',fontsize=\small' for more characters per line
\usepackage{framed}
\definecolor{shadecolor}{RGB}{248,248,248}
\newenvironment{Shaded}{\begin{snugshade}}{\end{snugshade}}
\newcommand{\KeywordTok}[1]{\textcolor[rgb]{0.13,0.29,0.53}{\textbf{#1}}}
\newcommand{\DataTypeTok}[1]{\textcolor[rgb]{0.13,0.29,0.53}{#1}}
\newcommand{\DecValTok}[1]{\textcolor[rgb]{0.00,0.00,0.81}{#1}}
\newcommand{\BaseNTok}[1]{\textcolor[rgb]{0.00,0.00,0.81}{#1}}
\newcommand{\FloatTok}[1]{\textcolor[rgb]{0.00,0.00,0.81}{#1}}
\newcommand{\ConstantTok}[1]{\textcolor[rgb]{0.00,0.00,0.00}{#1}}
\newcommand{\CharTok}[1]{\textcolor[rgb]{0.31,0.60,0.02}{#1}}
\newcommand{\SpecialCharTok}[1]{\textcolor[rgb]{0.00,0.00,0.00}{#1}}
\newcommand{\StringTok}[1]{\textcolor[rgb]{0.31,0.60,0.02}{#1}}
\newcommand{\VerbatimStringTok}[1]{\textcolor[rgb]{0.31,0.60,0.02}{#1}}
\newcommand{\SpecialStringTok}[1]{\textcolor[rgb]{0.31,0.60,0.02}{#1}}
\newcommand{\ImportTok}[1]{#1}
\newcommand{\CommentTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textit{#1}}}
\newcommand{\DocumentationTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\AnnotationTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\CommentVarTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\OtherTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{#1}}
\newcommand{\FunctionTok}[1]{\textcolor[rgb]{0.00,0.00,0.00}{#1}}
\newcommand{\VariableTok}[1]{\textcolor[rgb]{0.00,0.00,0.00}{#1}}
\newcommand{\ControlFlowTok}[1]{\textcolor[rgb]{0.13,0.29,0.53}{\textbf{#1}}}
\newcommand{\OperatorTok}[1]{\textcolor[rgb]{0.81,0.36,0.00}{\textbf{#1}}}
\newcommand{\BuiltInTok}[1]{#1}
\newcommand{\ExtensionTok}[1]{#1}
\newcommand{\PreprocessorTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textit{#1}}}
\newcommand{\AttributeTok}[1]{\textcolor[rgb]{0.77,0.63,0.00}{#1}}
\newcommand{\RegionMarkerTok}[1]{#1}
\newcommand{\InformationTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\WarningTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\AlertTok}[1]{\textcolor[rgb]{0.94,0.16,0.16}{#1}}
\newcommand{\ErrorTok}[1]{\textcolor[rgb]{0.64,0.00,0.00}{\textbf{#1}}}
\newcommand{\NormalTok}[1]{#1}

% some table layout adaptions
\setlength{\arrayrulewidth}{0.3mm}
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.3}

% --------------------------------------------------------------------------------------------------------------

% admonitions

% --------------------------------------------------------------------------------------------------------------

\usepackage[breakable,skins]{tcolorbox}
\tcbuselibrary{skins}
\tcbuselibrary{breakable}
\usepackage{wasysym} % to enable certain symbols in text mode

\newtcolorbox{boxwarning_template}[1][]{
  enhanced,
  before skip=2mm,
  after skip=3mm,
  boxrule=2pt,
  left=12mm,
  right=2mm,
  top=1mm,
  bottom=1mm,
  colback=red!10,
  colframe=red!70!white,
  underlay={%
    \path[fill=red!70!white,draw=none] (interior.south west) rectangle node[white]{\Huge\bfseries \frownie} ([xshift=10mm]interior.north west);
    },
   , #1}

\newenvironment{boxwarning}[1]
{\begin{boxwarning_template}
{\color{red} \textbf{#1}}
\vspace{5pt}
\\
}{\end{boxwarning_template}}

% --------------------------------------------------------------------------------------------------------------

\newtcolorbox{boxerror_template}[1][]{
  enhanced,
  before skip=2mm,
  after skip=3mm,
  boxrule=2pt,
  left=12mm,
  right=2mm,
  top=1mm,
  bottom=1mm,
  colback=red!30,
  colframe=red!90!white,
  underlay={%
    \path[fill=red!90!white,draw=none] (interior.south west) rectangle node[white]{\Huge\bfseries \lightning} ([xshift=10mm]interior.north west);
    },
   , #1}

\newenvironment{boxerror}[1]
{\begin{boxerror_template}
{\color{red} \textbf{#1}}
\vspace{5pt}
\\
}{\end{boxerror_template}}

% --------------------------------------------------------------------------------------------------------------

\newtcolorbox{boxgoodpractice_template}[1][]{
  enhanced,
  before skip=2mm,
  after skip=3mm,
  boxrule=2pt,
  left=12mm,
  right=2mm,
  top=1mm,
  bottom=1mm,
  colback=green!10,
  colframe=green!60!black,
  underlay={%
    \path[fill=green!60!black,draw=none] (interior.south west) rectangle node[white]{\Huge\bfseries \checkmark} ([xshift=10mm]interior.north west);
    },
   , #1}

\newenvironment{boxgoodpractice}[1]
{\begin{boxgoodpractice_template}
{\color{green!60!black} \textbf{#1}}
\vspace{5pt}
\\
}{\end{boxgoodpractice_template}}

% --------------------------------------------------------------------------------------------------------------

\newtcolorbox{boxhint_template}[1][]{
  enhanced,
  before skip=2mm,
  after skip=3mm,
  boxrule=2pt,
  left=12mm,
  right=2mm,
  top=1mm,
  bottom=1mm,
  colback=orange!10,
  colframe=orange!80!white,
  underlay={%
    \path[fill=orange!80!white,draw=none] (interior.south west) rectangle node[white]{\Huge\bfseries !} ([xshift=10mm]interior.north west);
    },
   , #1}

\newenvironment{boxhint}[1]
{\begin{boxhint_template}
{\color{orange!80!white} \textbf{#1}}
\vspace{5pt}
\\
}{\end{boxhint_template}}

% --------------------------------------------------------------------------------------------------------------

\newtcolorbox{boxtip_template}[1][]{
  enhanced,
  before skip=2mm,
  after skip=3mm,
  boxrule=2pt,
  left=12mm,
  right=2mm,
  top=1mm,
  bottom=1mm,
  colback=blue!10,
  colframe=blue!70!white,
  underlay={%
    \path[fill=blue!70!white,draw=none] (interior.south west) rectangle node[white]{\Huge\bfseries \smiley} ([xshift=10mm]interior.north west);
    },
   , #1}

\newenvironment{boxtip}[1]
{\begin{boxtip_template}
{\color{blue!70!white} \textbf{#1}}
\vspace{5pt}
\\
}{\end{boxtip_template}}

% --------------------------------------------------------------------------------------------------------------

\title{\textbf{###TITLE###}\\
\vspace{2ex}
\textbf{v. ###VERSION###}}

\author{###AUTHOR###}

\date{###DATE###}

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
      sReturn = sHeader.replace('###TITLE###',   sTitle)
      sReturn = sReturn.replace('###VERSION###', sVersion)
      sReturn = sReturn.replace('###AUTHOR###',  sAuthor)
      sReturn = sReturn.replace('###DATE###',    sDate)
      return sReturn

   # eof def GetHeader(self, sTitle="", sVersion="", sAuthor="", sDate=""):

   # --------------------------------------------------------------------------------------------------------------

   def GetChapter(self, sHeadline="", sDocumentName=""):
      """
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

