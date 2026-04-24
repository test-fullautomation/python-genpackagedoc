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

   What is the structure of the application repository?

* Folder :fsystem:`GenPackageDoc`

  Contains the package code.

  *This folder is specific for the package.*

* Folder :fsystem:`packagedoc`

  Contains all package documentation related files, e.g. the **GenPackageDoc** configuration, additional input files
  and the generated documentation itself.

  *This folder is specific for the documentation.*

* Repository root folder

  - :fsystem:`genpackagedoc.py`

    Python script to start the documentation build

  - :fsystem:`build_backend.py`

    Custom build backend to execute additional installation steps. Currently this is a pattern only reserved for future development.

  - :fsystem:`pyproject.toml`

    Main configuration file for the installation of the component

  - :fsystem:`dump_repository_config.py`

    Little helper to dump the repository configuration to console

/NP
