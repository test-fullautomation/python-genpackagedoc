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

**ToDo list:**

* [01]

  Introduce ``setup.py`` including the execution of ``genpackagedoc.py`` and adding the generated PDF document to the installation./
  Introduce README.rst and README.md.

  10.05.2022: Setup process introduced and README.rst added

* [02]

  Currently it is hard coded, that private functions and methods are skipped. Therefore they are not part of the resulting PDF document./
  A configuration switch might be useful to give the user the ability to control this behavior.

  09.05.2022: Parameter 'INCLUDEPRIVATE' added

* [03]

  Currently it is implemented that also functions, classes and methods without docstrings are part of the resulting PDF document.
  They are listed together with the hint, that a docstring is not available./
  A configuration switch might be useful to give the user the ability to control this behavior.

  09.05.2022: Parameter 'INCLUDEUNDOCUMENTED' added

* [04]

  Currently it is implemented that for Python modules will be searched recursively within the given root folder.
  Maybe the algorithm also catches modules from which the user does not want ``GenPackageDoc`` to include them./
  A configuration exclude filter can be implemented to skip those files. Or maybe other way round: An include filter includes a
  subset of available files only.

  The same filter mechanism can be extended for the content of Python modules (= include/exclude functions, classes and methods).

* [05]

  Currently the configuration parameter for the documentation build proccess are taken from a json file ``packagedoc_config.json``./
  It might be helpful to have the possibility to overwrite them in command line (e.g. for redirecting the path to the output folder
  without changing any code).

  31.05.2022: Implemented in v. 0.15.0

* [06]

  Introduce text boxes for warnings, errors and informations.

  19.05.2022: implemented in v. 0.12.0

* [07]

  The documentation build process allows relative paths only/
  (in ``packagedoc_config.json``)./
  Maybe a mechanism is useful to allow absolute paths and paths based on environment variables also.

  01.06.2022: implemented in v. 0.16.0

* [08]

  Explore further rst syntax elements like the code directive. Some of them produces LaTeX code that requires the include of additional
  LaTeX packages. Sometimes this causes errors that have to be fixed.

  05.05.2022: Python syntax highlighting realized

* [09]

  The documentation has to be extended by a set of rst examples (rst best practices).

* [10]

  A postprocessing for LaTeX code needs to be implemented:

  - Enable proper line breaks
  - Resolve the ambiguity of labels created automatically when the LaTeX code is generated (for every input file separately)

  10.05.2022: Experimental syntax extensions for ``newline``, ``newpage`` and ``vspace``

  17.05.2022: Postprocessing for rst and tex sources added; "multiply-defined labels" fix.

* [11]

  Currently the docstrings of Python modules have to contain a heading for functions, classes and methods. The developer is responsible for that.
  Maybe it is not necessary to maintain these headings manually. It has to be investigated, if these headings can be added automatically
  by ``GenPackageDoc``. 

  06.05.2022: Headings are added automatically.

* [12]

  Currently the documentation of a single Python module starts at *function* or *class* level. This means it is not possible to provide common information
  about the Python module itself (placed **before** the content of the first function or class of the module). A way have to be found to add such content.

  06.05.2022: Implemented in version 0.4.0

* [13]

  The error handling needs to be extended!

  17.06.2022: Implemented in version 0.17.0

* [14]

  Take over the description of

     ``config/repository_config.json``

  from inside this json file (comment blocks) to the main PDF document.

* [15]

  Reference section with useful links

* [16]

  History

  10.05.2022: History added

* [17]

  Debug switch to enable additional output

* [18]

  Parse decorators to identify Robot Framework keyword definitions

* [19]

  Selftest

* [20]

  Introduce a separate folder containing TeX styles - instead of having them hard coded within CPatterns.py.

  24.05.2022: implemented in v. 0.13.0

