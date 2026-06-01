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


**Version 0.44.0 (29.05.2026)**

    *Added:*

    * Search function

    *Maintenance:*

    * LaTeX preamble (``xcolor`` fix)

**Version 0.43.0 (18.05.2026)**

    *Maintenance:*

    * Usage of **Setuptools** replaced by usage of **PIP/TOML/Setuptools**
    * History reworked (youngest verion on top now) and migrated from LaTeX format to RST format

    *Added:*

    * Possibility to exclude interface files from computation
    * Markdown directives to support Python and **Robot Framework** code listings
    * Markdown directives to support JSONP code listings
    * Markdown directives to support common console and log listings
    * Markdown directives to support listings of file system contents
    * Markdown directives to support a simple highlighting in gray color
    * Syntax extensions for vertical and horizontal distances
    * Support od **async** functions and methods
    * Output of documentation in HTML-Format

**Version 0.42.0 (12.01.2026)**

    *Maintenance:*

    * Usage of **pandoc/pypandoc** replaced by usage of **docutils** (conversion of RST content to LaTeX format)

**Version 0.41.0 (11.07.2023)**

    *Added:*

    * Text macro ``\q{}`` to set double quotes

**Version 0.40.0 (09.05.2023)**

    *Added:*

    * **PlantUML** support

    * Possibility to render diagrams directly from text source code

**Version 0.39.0 (06.01.2023)**

    *Added:*

    * Masking of underlines in case of the content of ``\repo`` or ``\pkg`` contains underlines (masking required by LaTeX)

**Version 0.38.0 (30.11.2022)**

    *Removed:*

    * Harming ligatures that were added by **Pandoc** automatically to LaTeX code in case of multiple minus characters in names


**Version 0.37.0 (21.11.2022)**

    *Added:*

    * LaTeX commands ``pythonlog`` and ``plog``
    * ``keyword`` decorator detection

    *Maintenance:*

    * LaTeX style adaptions
    * ``INCLUDEPRIVATE`` temporarily switched off (requires bugfixes)

**Version 0.36.0 (17.11.2022)**

    *Maintenance:*

    * Brightness of all colors of listings reduced to 45% (both text boxes and inline)

**Version 0.35.0 (16.11.2022)**

    *Maintenance:*

    * Layout settings of some LaTeX commands adapted
    * Repository name and package name in bold
    * Inline code and inline listings in clearer colors

**Version 0.34.0 (07.11.2022)**

    *Added:*

    * Auto defined LaTeX style file containing mnemotechnical commands to type the repository name and the package name

**Version 0.33.0 (19.09.2022)**

    *Maintenance:*

    * Rework of label mechanism (to enable unique links to functions, classes and methods with names
      that are not unique over all Python modules within a package)

**Version 0.32.0 (16.09.2022)**

    *Added:*

    * Labels at ``chapter`` level

    *Maintenance:*

    * Partial rework of label mechanisms

**Version 0.31.0 (12.09.2022)**

    *Fixes:*

    * Import path of a module in PDF file

**Version 0.30.0 (31.08.2022)**

    *Added:*

    * ``simulateonly`` mode (command line switch to skip the PDF generation)

**Version 0.29.0 (24.08.2022)**

    *Changes:*

    * Layout of import path of a module (in PDF file)

**Version 0.28.0 (23.08.2022)**

    *Added:*

    * LaTeX environment variable ``GENDOC_LATEXPATH``

    *Maintenance:*

    * File **robotframeworkaio.sty** aligned to version of this file in **GenMainDoc**

**Version 0.27.0 (17.08.2022)**

    *Added:*

    * LaTeX style definition for Python syntax highlighting

**Version 0.26.0 (27.07.2022)**

    *Maintenance:*

    * History reworked

    *Added:*

    * File **common.sty** (common LaTeX commands e.g. to support the history)

**Version 0.25.0 (27.07.2022)**

    *Maintenance:*

    * Layout of **RobotFramework AIO** syntax highlighting (in **.sty** files)

**Version 0.24.0 (25.07.2022)**

    *Maintenance:*

    * Line breaks in listings (in **robotframeworkaio.sty**)

**Version 0.23.0 (13.07.2022)**

    *Maintenance:*

    * File **preamble.tex**

**Version 0.22.0 (13.07.2022)**

    *Maintenance:*

    * File **preamble.tex**
    * Folder **styles**

    *Fix:*

    * **setup.py** installs tex files also

**Version 0.21.0 (12.07.2022)**

    *Maintenance:*

    * Separated file **preamble.tex**

**Version 0.20.0 (29.06.2022)**

    *Fix:*

    * Added missing masking of underlines in PDF document title (required for LaTeX)

**Version 0.19.0 (28.06.2022)**

    *Added:*

    * Method ``GetLaTeXStyles``

    *Maintenance:*

    * **PythonExtensionsCollection** updated to version 0.8.0

**Version 0.18.0 (20.06.2022)**

    *Added:*

    * Parameter to define an output folder for a dump of final configuration

**Version 0.17.0 (17.06.2022)**

    *Added:*

    * Possibility to dump the configuration

    *Maintenance:*

    * Code and error handling

**Version 0.16.0 (01.06.2022)**

    *Maintenance:*

    * Path computation reworked

**Version 0.15.0 (31.05.2022)**

    *Added:*

    * **GenPackageDoc** command line
    * Separate **GenPackageDoc** configuration class

**Version 0.14.0 (27.05.2022)**

    *Added:*

    * LaTeX compiler check
    * Control parameter ``STRICT`` added to **GenPackageDoc** configuration

**Version 0.13.0 (24.05.2022)**

    *Maintenance:*

    * LaTeX style definitions moved to a separate folder

**Version 0.12.0 (19.05.2022)**

    *Added:*

    * Admonitions based on LaTeX environment ``tcolorbox``

    *Maintenance:*

    * Layout adaptions in titlepage

    *Fix:*

    * Page numbering in TOC

**Version 0.11.0 (18.05.2022)**

    *Added:*

    * Possibility to import **tex** files

**Version 0.10.0 (17.05.2022)**

    *Added:*

    * Postprocessing for **rst** and **tex** source files added

    *Fix:*

    * ``multiply-defined labels``

**Version 0.9.2 (16.05.2022)**

    *Fix:*

    * Automated line breaks within code blocks

**Version 0.9.1 (11.05.2022)**

    *Maintenance:*

    * Documentation

**Version 0.9.0 (10.05.2022)**

    *Maintenance:*

    * Layout maintenance and syntax extensions for ``newline``, ``newpage`` and ``vspace``

**Version 0.8.0 (10.05.2022)**

    *Changes:*

    * Bugfixes and code maintenance

    *Added:*

    * Version history

**Version 0.7.0 (10.05.2022)**

    *Added:*

    * Setup process and file **README.rst**

    *Maintenance:*

    * Code

**Version 0.6.0 (09.05.2022)**

    *Added:*

    * Parameter ``INCLUDEUNDOCUMENTED``

**Version 0.5.0 (09.05.2022)**

    *Added:*

    * Parameter ``INCLUDEPRIVATE``

**Version 0.4.0 (06.05.2022)**

    *Added:*

    * Possibility to describe complete Python modules

**Version 0.3.0 (06.05.2022)**

    *Added:*

    * Automated headings for functions, classes and methods

**Version 0.2.0 (05.05.2022)**

    *Added:*

    * Python syntax highlighting within code blocks

**Version 0.1.0 (04/2022)**

    **Initial version**

----

`GenPackageDoc in GitHub <https://github.com/test-fullautomation/python-genpackagedoc>`__

`GenPackageDoc in PyPi <https://pypi.org/project/GenPackageDoc/>`__

