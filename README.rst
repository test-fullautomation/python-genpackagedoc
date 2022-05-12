.. Copyright 2020-2022 Robert Bosch Car Multimedia GmbH

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Package Description
===================

The Python package ``GenPackageDoc`` generates the documentation of Python modules. The content of this documentation is taken out of the docstrings of
functions, classes and their methods.

It is possible to extend the documentation by the content of additional text files.

The documentation is generated in two steps:

1. The rst sources are converted into LaTeX sources
2. The LaTeX sources are converted into a PDF document. This requires a separately installed LaTeX distribution (recommended: MiKTeX),
   that is **not** part of ``GenPackageDoc``.

How to install
--------------

Firstly clone the **python-genpackagedoc** repository to your machine.

.. code-block::

   git clone https://github.com/test-fullautomation/python-genpackagedoc.git

Use the following command to install this package:

.. code-block::

    setup.py install

Package Documentation
---------------------

A detailed documentation of the GenPackageDoc package can be found here:
`GenPackageDoc.pdf <https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/GenPackageDoc/GenPackageDoc.pdf>`_

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
