.. Copyright 2020-2026 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

.. highlight::

   How do the files and folders listed above relate to each other? What is the flow of information when the documentation is generated?

* The process starts with the execution of :fsystem:`genpackagedoc.py` within the repository root folder.

* :fsystem:`genpackagedoc.py` creates a repository configuration object

     :fsystem:`config/CRepositoryConfig.py`

* The repository configuration object reads the static repository configuration values out of the TOML file

     :fsystem:`pyproject.toml`

  Exception: The component version is taken from the Python source code

     :fsystem:`GenPackageDoc/version.py`

* The repository configuration object adds dynamic values (like operating system specific settings and paths) to the repository configuration.

* The configuration file :fsystem:`packagedoc_config.json` contains settings like

  * Paths to Python packages to be documented
  * Paths and names of additional reST files
  * Path and name of output folder (LaTeX files and output PDF file)
  * User defined parameter (that can be defined here as global runtime variables and can be used in any reST code)
  * Basic settings related to the output PDF file (like document name, name of author, ...)
  * Path to LaTeX compiler/
    (*a LaTeX distribution is not part of* **GenPackageDoc**)

  Be aware of that the within :fsystem:`packagedoc_config.json` specified output folder

     :fsystem:`"OUTPUT" : "./build"`

  **will be deleted** at the beginning of the documentation build process! Make sure that you do not have any files
  inside this folder opened when you start the process. In case of the path is relative, the reference
  is the position of :fsystem:`genpackagedoc.py`. The complete path is created recursively.

  **Further details are explained within the json file itself.**

* :fsystem:`genpackagedoc.py` also creates an own configuration object

     :fsystem:`GenPackageDoc/CPackageDocConfig.py`

  :fsystem:`CPackageDocConfig.py` takes over all repository configuration values, reads in the static **GenPackageDoc**
  configuration (:fsystem:`packagedoc_config.json`) and adds dynamically computed values like the full absolute paths
  belonging to the documentation build process. Also all command line parameters are resolved and checked.

  The reference for all relative paths is the position of :fsystem:`genpackagedoc.py` (that is the repository root folder).

After the execution of :fsystem:`genpackagedoc.py` the resulting PDF document can be found under the specified name
within the specified output folder (:acontent:`"OUTPUT"`). This folder also contains all temporary files generated during the
documentation build process.

Because the output folder is a temporary one, the PDF document is copied to the folder containing the package sources
and therefore is included in the package installation. This is defined in the **GenPackageDoc** configuration,
section :acontent:`"PDFDEST"`.

/NP
