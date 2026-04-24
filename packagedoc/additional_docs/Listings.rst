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

   How to realize listings of code written in Python, Robot Framework and JSON?
   How to realize listings of console content and log file content?

**GenPackageDoc** supports code listings and console listings. These listings are available as text block and as inline text also.
You can use these listings in reST files and also in LaTeX files immediately. The reST elements for listings are mapped to the corresponding
LaTeX commands when **GenPackageDoc** internally converts the reST files in LaTeX files.

Text blocks are realized by markdown directives. Inline text is realized by markdown rules./VVS

**Examples:**/VS

----

This is a markdown directive :pcode:`pythoncode` code example:

.. pythoncode::

   for index in list:
       print("index")

Written in reST format:

.. anycontent::

   .. pythoncode::

      for index in list:
          print("index")

Written in LaTeX format:

.. anycontent::

   \begin{pythoncode}
       for index in list:
           print("index")
   \end{pythoncode}

----

This is a markdown directive :rcode:`robotcode` code example:

.. robotcode::

   FOR    ${index}    IN RANGE    0    ${max}
       log    index: ${index}    console=yes
   END

Written in reST format:

.. anycontent::

   .. robotcode::

      FOR    ${index}    IN RANGE    0    ${max}
          log    index: ${index}    console=yes
      END

/NP
Written in LaTeX format:

.. anycontent::

   \begin{robotcode}
      FOR    ${index}    IN RANGE    0    ${max}
          log    index: ${index}    console=yes
      END
   \end{robotcode}

This is a markdown directive :pcode:`pythonlog` code example:

.. pythonlog::

   index: 0
   index: 1
   index: 2

Written in reST format:

.. anycontent::

   .. pythonlog::

      index: 0
      index: 1
      index: 2

Written in LaTeX format:

.. anycontent::

   \begin{pythonlog}
      index: 0
      index: 1
      index: 2
   \end{pythonlog}

----

This is a markdown directive :rcode:`robotlog` code example:

.. robotlog::

   index: 0
   index: 1
   index: 2

Written in reST format:

.. anycontent::

   .. robotlog::

      index: 0
      index: 1
      index: 2

Written in LaTeX format:

.. anycontent::

   \begin{robotlog}
      index: 0
      index: 1
      index: 2
   \end{robotlog}

----

/NP

This is inline Python code: :pcode:`print("Hello Python")`

Written in reST format:

.. anycontent::

   :pcode:`print("Hello Python")`

Written in LaTeX format:

.. anycontent::

   \pcode{print("Hello Python")}

----

This is inline Robot code: :rcode:`log/IHS/IHS/IHS/IHSHello RobotFramework AIO`

Written in reST format:

**TODO: Add screenshot with:** log/IHS/IHS/IHS/IHSHello RobotFramework AIO

Written in LaTeX format:

.. anycontent::

   \rcode{log\ \ \ \ Hello RobotFramework AIO}

**Caution: Blanks must be announced explicitly in inline literals, because under normal circumstances multiple blanks are collapsed
to a single blank (in LaTeX and in HTML also).**

----

This is inline Python log: :plog:`Hello Python`

Written in reST format:

.. anycontent::

   :plog:`Hello Python`

Written in LaTeX format:

.. anycontent::

   \plog{Hello Python}

----

This is inline Robot log: :rlog:`Hello RobotFramework AIO`

Written in reST format:

.. anycontent::

   :rlog:`Hello RobotFramework AIO`

Written in LaTeX format:

.. anycontent::

   \rlog{Hello RobotFramework AIO}


**TODO: to be continued**


/NP
