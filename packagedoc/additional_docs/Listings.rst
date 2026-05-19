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

**GenPackageDoc** supports several code listings and console listings. These listings are available as text block and as inline text also.
You can use these listings in reST files and also in LaTeX files immediately. The reST elements for listings are mapped to the corresponding
LaTeX commands when **GenPackageDoc** internally converts the reST files in LaTeX files.

Text blocks are realized by reST directives. Inline text is realized by reST roles./VVS

**Examples:**/VS

This is an reST directive :acontent:`pythoncode` code example:

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

.. hrstar::

This is an reST directive :acontent:`robotcode` code example:

.. robotcode::

   *** Test Cases ***

   Example

       FOR    ${index}    IN RANGE    0    ${max}
           log    index: ${index}    console=yes
       END

/NP
Written in reST format:

.. anycontent::

   .. robotcode::

      *** Test Cases ***

      Example

          FOR    ${index}    IN RANGE    0    ${max}
              log    index: ${index}    console=yes
          END

Written in LaTeX format:

.. anycontent::

   \begin{robotcode}
      *** Test Cases ***

      Example

          FOR    ${index}    IN RANGE    0    ${max}
              log    index: ${index}    console=yes
          END
   \end{robotcode}

.. hrstar::

This is an reST directive :acontent:`jsoncode` code example:

.. jsoncode::

   {
       "param_1" : "ABC",
       "param_2" : true,
       "param_3" : [1,2,3],
       "param_4" : {"A" : 1, "B" : 2}
   }

Written in reST format:

.. anycontent::

   .. jsoncode::

      {
          "param_1" : "ABC",
          "param_2" : true,
          "param_3" : [1,2,3],
          "param_4" : {"A" : 1, "B" : 2}
      }

Written in LaTeX format:

.. anycontent::

   \begin{jsoncode}
      {
          "param_1" : "ABC",
          "param_2" : true,
          "param_3" : [1,2,3],
          "param_4" : {"A" : 1, "B" : 2}
      }
   \end{jsoncode}

.. hrstar::

This is an reST directive :acontent:`anycontent` code example:

.. anycontent::

   Any content, no matter if Python, Robot Framework, JSON or something else.
   Any content, no matter if Python, Robot Framework, JSON or something else.
   Any content, no matter if Python, Robot Framework, JSON or something else.

/NP
Written in reST format:

.. code::

   .. anycontent::

      Any content, no matter if Python, Robot Framework, JSON or something else.
      Any content, no matter if Python, Robot Framework, JSON or something else.
      Any content, no matter if Python, Robot Framework, JSON or something else.

Written in LaTeX format:

.. code::

   \begin{anycontent}
      Any content, no matter if Python, Robot Framework, JSON or something else.
      Any content, no matter if Python, Robot Framework, JSON or something else.
      Any content, no matter if Python, Robot Framework, JSON or something else.
   \end{anycontent}

.. hrstar::

This is an reST directive :acontent:`consolelog` code example:

.. consolelog::

   log index: 0
   log index: 1
   log index: 2

Written in reST format:

.. anycontent::

   .. consolelog::

      log index: 0
      log index: 1
      log index: 2

Written in LaTeX format:

.. anycontent::

   \begin{consolelog}
      log index: 0
      log index: 1
      log index: 2
   \end{consolelog}

.. hrstar::

This is an reST directive :acontent:`filesystem` code example:

.. filesystem::

   C:\folder_1\file_1.txt
   C:\folder_2\file_2.txt
   C:\folder_3\file_3.txt

Written in reST format:

.. anycontent::

   .. filesystem::

      C:\folder_1\file_1.txt
      C:\folder_2\file_2.txt
      C:\folder_3\file_3.txt

/NP
Written in LaTeX format:

.. anycontent::

   \begin{filesystem}
      C:\folder_1\file_1.txt
      C:\folder_2\file_2.txt
      C:\folder_3\file_3.txt
   \end{filesystem}

/VVS
**Hint:** :acontent:`consolelog` *and* :acontent:`filesystem` *currently have the same layout.
Nevertheless, using individual and specific names eases the readability. Maybe later different layouts
will be realized.*

.. hrstar::

This is inline Python code: :pcode:`print("Hello Python")`

Written in reST format:

.. anycontent::

   :pcode:`print("Hello Python")`

Written in LaTeX format:

.. anycontent::

   \pcode{print("Hello Python")}

.. hrstar::

This is inline Robot Framework code: :rcode:`log/IHS/IHS/IHS/IHSHello RobotFramework AIO`

Written in reST format:

.. code::

   :rcode:`log/*IHS/*IHS/*IHS/*IHSHello RobotFramework AIO`

.. !!! /*IHS is the masked version of /IHS and will not be replaced by a single blank in output !!!

Written in LaTeX format:

.. code::

   \rcode{log\ \ \ \ Hello RobotFramework AIO}

/VVS
**Hint:** *Blanks must be announced explicitly in inline code, because under normal circumstances multiple blanks are collapsed
to a single blank (in LaTeX and in HTML also).*

.. hrstar::

This is inline JSON code: :jcode:`"param" : [1,2,3]`

Written in reST format:

.. anycontent::

   :jcode:`"param" : [1,2,3]`

Written in LaTeX format:

.. anycontent::

   \jcode{"param" : [1,2,3]}

.. hrstar::

This is any inline content: :acontent:`any content`

Written in reST format:

.. anycontent::

   :acontent:`any content`

Written in LaTeX format:

.. anycontent::

   \acontent{any content}

.. hrstar::

The horizontal separator line with the star in the middle can be inserted with the reST directive :acontent:`.. hrstar::`.
This is a nice possibility to separate smaller parts of the documentation from each other - without introducing a new headline for every part.

/NP

**When we use all of these reST syntax elements to realize a concrete documentation - how does this look like?**
**The following is a full example:**

.. anycontent::

   In the system configuration file, the parameter :acontent:`aparam` and :acontent:`bparam` are defined in the following way:

   .. jsoncode::

      {
          // system parameter
          "aparam" : 1,
          "bparam" : "hello world"
      }

   This configuration file can be found here:

   .. filesystem::

      ${systemroot}/packages/labels/alabel/config.jsonp

   Make sure to select the proper label: :acontent:`alabel`.

   The **Robot Framework** keyword :acontent:`compute_system_parameter` computes these system parameters in the following way:

   * The parameter :acontent:`aparam` is increased by value :acontent:`1`.
   * The parameter :acontent:`bparam` is concatenated with string :acontent:`today` (with a blank in between).

   This is the corresponding Python implementation of the keyword :acontent:`compute_system_parameter`:

   .. pythoncode::

      system_config = system.get_config()
      system_config['aparam'] = system_config['aparam'] + 1
      system_config['bparam'] = system_config['bparam'] + " today"
      number_of_parameters = len(system_config)
      return system_config, number_of_parameters

   Additionally to the system configuration :acontent:`system_config`, another variable :acontent:`number_of_parameters`
   containing the number of system parameters, is returned.

   Within a **Robot Framework** test you call the keyword :acontent:`compute_system_parameter` in the following way:

   .. robotcode::

      *** Test Cases ***

      SystemTest

          ${system_config}    ${number_of_parameters}    compute_system_parameter
          log    Number of parameters: ${number_of_parameters}
          log    aparam..............: ${system_config}[aparam]

   In the log file it can be observed that the value of parameter :acontent:`aparam` is :acontent:`2` now.
   The value of parameter :acontent:`bparam` is :acontent:`hello world today` now.
   With 2 parameters in total.

/VVS/NP
**Result:**

.. hrstar::

In the system configuration file, the parameter :acontent:`aparam` and :acontent:`bparam` are defined in the following way:

.. jsoncode::

   {
       // system parameter
       "aparam" : 1,
       "bparam" : "hello world"
   }
 
This configuration file can be found here:

.. filesystem::

   ${systemroot}/packages/labels/alabel/config.jsonp

Make sure to select the proper label: :acontent:`alabel`.

The **Robot Framework** keyword :acontent:`compute_system_parameter` computes these system parameters in the following way:

* The parameter :acontent:`aparam` is increased by value :acontent:`1`.
* The parameter :acontent:`bparam` is concatenated with string :acontent:`today` (with a blank in between).

This is the corresponding Python implementation of the keyword :acontent:`compute_system_parameter`:

.. pythoncode::

   system_config = system.get_config()
   system_config['aparam'] = system_config['aparam'] + 1
   system_config['bparam'] = system_config['bparam'] + " today"
   number_of_parameters = len(system_config)
   return system_config, number_of_parameters

Additionally to the system configuration :acontent:`system_config`, another variable :acontent:`number_of_parameters`
containing the number of system parameters, is returned.

Within a **Robot Framework** test you call the keyword :acontent:`compute_system_parameter` in the following way:

.. robotcode::

   *** Test Cases ***

   SystemTest

       ${system_config}    ${number_of_parameters}    compute_system_parameter
       log    Number of parameters: ${number_of_parameters}
       log    aparam..............: ${system_config}[aparam]

In the log file it can be observed that the value of parameter :acontent:`aparam` is :acontent:`2` now.
The value of parameter :acontent:`bparam` is :acontent:`hello world today` now.
With 2 parameters in total.

.. hrstar::

/NP


