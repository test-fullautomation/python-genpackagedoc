.. Copyright 2020-2022 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

The Python package **GenPackageDoc** generates the documentation of Python modules. The content of this documentation is taken out of
the docstrings of functions, classes and their methods. All docstrings have to be written in reStructuredText (RST) format, that is a
certain markdown dialect.

It is possible to extend the documentation by the content of additional files either in reStructuredText format or in LaTeX format.

The documentation is generated in four steps:

1. Files in LaTeX format are taken over immediately.
2. Files in reStructuredText format are converted to LaTeX files.
3. All docstrings of all Python modules in the package are converted to LaTeX files.
4. All LaTeX files together are converted to a single PDF document. This requires a separately installed LaTeX distribution (recommended: TeX Live).
   A LaTeX distribution is **not** part of **GenPackageDoc** and has to be installed separately!

The sources of **GenPackageDoc** are available in the following GitHub repository:

   `python-genpackagedoc <https://github.com/test-fullautomation/python-genpackagedoc>`_

The repository **python-genpackagedoc** uses it's own functionality to document itself and the contained Python package **GenPackageDoc**.

**Therefore the complete repository can be used as an example about writing a package documentation.**

It has to be considered, that the main goal of **GenPackageDoc** is to provide a toolchain to generate documentation out of Python sources
that are stored within a repository, and therefore we have dependencies to the structure of the repository. For example: Configuration files with values
that are specific for a repository, should not be installed. Such a specific configuration value is e.g. the name of the package or the name of the PDF document.

The impact is: There is a deep relationship between the repository containing the sources to be documented, and the sources and the configuration
of **GenPackageDoc** itself. Therefore some manual preparations are necessary to use **GenPackageDoc** also in other repositories.

How to do this is explained in detail in the next chapters.

The outcome of all preparations of **GenPackageDoc** in your own repository is a PDF document like the one you are currently reading.
