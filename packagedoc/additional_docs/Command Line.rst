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

   Which command line parameters are available to influence the behavior of the application?

Some configuration parameter predefined within :fsystem:`packagedoc_config.json`, can be overwritten in command line./VS

:fsystem:`--output`

  Path and name of folder containing all output files.

  **Caution: GenPackageDoc deletes this folder!**

.. TODO: use admonition

:fsystem:`--pdfdest`

  Path and name of folder in which the generated PDF file will be copied to (after this file has been created within the output folder).

  *Caution*: The generated PDF file will per default be copied to the package folder within the repository. This is defined in :fsystem:`packagedoc_config.json`.
  The version of the PDF file within the package folder will be part of the installation. When you change the PDF destination,
  then you get this file at another location - but this file will not be part of the installation any more. Installed will be the version,
  that is still present within the package folder of the repository.

:fsystem:`--htmldest`

  Path and name of folder in which the generated HTML files will be copied to (after this file has been created within the output folder).

  **Caution: GenPackageDoc deletes this folder!**

.. TODO: use admonition

  *Caution*: The generated HTML files will per default be copied to the package folder within the repository. This is defined in :fsystem:`packagedoc_config.json`.
  The version of the HTML files within the package folder will be part of the installation. When you change the HTML destination,
  then you get this file at another location - but this file will not be part of the installation any more. Installed will be the version,
  that is still present within the package folder of the repository.

:fsystem:`--configdest`

  Path and name of folder in which a dump of the current configuration will be copied to.

  The configuration dump is part of the build output (section :acontent:`'OUTPUT'`) and available in txt and in json format.
  It might be useful for further processes to have access to all details regarding the current
  documentation build.

:fsystem:`--strict`

  If :acontent:`True`, a missing LaTeX compiler aborts the process, otherwise the process continues.

/NP

:fsystem:`--simulateonly`

  If :acontent:`True`, the LaTeX compiler is switched off. No new PDF output will be generated. Already existing PDF output will not be updated.
  This is not handled as error and also not handled as warning. Only the source files will be parsed. This switch is useful
  to do a pre check for possible syntax issues within the source files without spending time for rendering PDF files.

**Example**

.. filesystem::

   genpackagedoc.py --output="../any/other/location" --pdfdest="../any/other/location" --htmldest="../any/other/location" --configdest="../any/other/location" --strict=True

/NP
