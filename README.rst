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

GenPackageDoc Description
=========================

The Python package **GenPackageDoc** generates the documentation of Python modules. The content of this documentation is taken out of the docstrings of
functions, classes and their methods.

It is possible to extend the documentation by the content of additional files either in reStructuredText (RST) format or in LaTeX format.

The documentation is generated in four steps:

1. Files in LaTeX format are taken over immediately.
2. Files in reStructuredText format are converted to LaTeX files.
3. All docstrings of all Python modules in the package are converted to LaTeX files.
4. All LaTeX files together are converted to a single PDF document. This requires a separately installed LaTeX distribution (recommended: TeX Live).
   A LaTeX distribution is **not** part of **GenPackageDoc** and has to be installed separately!

How to install
--------------

**GenPackageDoc** can be installed in two different ways.

1. Installation via PyPi (recommended for users)

   .. code::

      pip install GenPackageDoc

   `GenPackageDoc in PyPi <https://pypi.org/project/GenPackageDoc/>`_

2. Installation via GitHub (recommended for developers)

   Clone the **python-genpackagedoc** repository to your machine.

   .. code::

      git clone https://github.com/test-fullautomation/python-genpackagedoc.git

   `GenPackageDoc in GitHub <https://github.com/test-fullautomation/python-genpackagedoc>`_

   Use the following command to install **GenPackageDoc**:

   .. code::

      setup.py install

How to use
----------

**GenPackageDoc** provides a toolchain to generate documentation out of Python sources that are stored within a repository.
**GenPackageDoc** is also designed to be able to consider setup informations of a repository.

The impact is: There is a deep relationship between the repository containing the sources to be documented, and the sources and the configuration
of **GenPackageDoc** itself. Therefore **GenPackageDoc** needs to be configured to get to know about things like the path to the package sources
and the desired name of the generated documentation PDF file.

**GenPackageDoc** is able to use it's own sources to document itself. Therefore the complete
`GenPackageDoc repository <https://github.com/test-fullautomation/python-genpackagedoc>`_ can be used as example about about writing a package documentation.

At the end of all preparations you will get for your own repository a PDF document that will look like this:
`GenPackageDoc.pdf <https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/GenPackageDoc/GenPackageDoc.pdf>`_
(that is the detailed documentation of **GenPackageDoc**).

Feedback
--------

To give us a feedback, you can send an email to `Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_ 

In case you want to report a bug or request any interesting feature, please don't hesitate to raise a ticket.

Maintainers
-----------

`Holger Queckenstedt <mailto:Holger.Queckenstedt@de.bosch.com>`_

`Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

Contributors
------------

`Holger Queckenstedt <mailto:Holger.Queckenstedt@de.bosch.com>`_

`Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

License
-------

Copyright 2020-2022 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    |License: Apache v2|

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


.. |License: Apache v2| image:: https://img.shields.io/pypi/l/robotframework.svg
   :target: http://www.apache.org/licenses/LICENSE-2.0.html
