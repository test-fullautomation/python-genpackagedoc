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


----


any content any content any content any content any content any content any content any content any content any content 
any content any content any content any content any content any content any content any content any content any content 
Some :acontent:`any content`: :acontent:`Configuration ./imports/rf_variables.py` and also :acontent:`1+2+3`
any content any content any content any content any content any content any content any content any content any content 
and :acontent:`b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f'`

And now in entire textblock:

.. anycontent::

   2025-11-21 10:15:05.762468 - INFO - +- START SETUP: tm.Testsuite Setup [ ./config/tsm-test_variants.jsonp ]
   2025-11-21 10:15:05.797731 - INFO - Set suite metadata 'project' to value 'tsm-test_config_default'.
   2025-11-21 10:15:05.797838 - INFO - Set suite metadata 'machine' to value 'HI-C-0044M'.
   2025-11-21 10:15:05.799145 - INFO - Set suite metadata 'tester' to value 'Queckenstedt Holger (XC-HWP/ESC3)'.
   2025-11-21 10:15:05.799342 - INFO - Set suite metadata 'testtool' to value 'Robot Framework 7.3 (Python 3.13.2 on win32)'.
   2025-11-21 10:15:05.799408 - INFO - Set suite metadata 'reference_version' to value '0.14.2.26'.
   2025-11-21 10:15:05.799443 - INFO - Set suite metadata 'reference_app_name' to value 'RobotFramework AIO (original)'.
   2025-11-21 10:15:05.799475 - INFO - Set suite metadata 'version_sw' to value 'None'.
   2025-11-21 10:15:05.799505 - INFO - Set suite metadata 'version_hw' to value 'None'.
   2025-11-21 10:15:05.799535 - INFO - Set suite metadata 'version_test' to value 'None'.
   2025-11-21 10:15:05.799909 - INFO - ${teststring_common} = I am the common teststring valid for all variants and all test benches
   2025-11-21 10:15:05.800166 - INFO - ${teststring_bench} = I am the teststring containing the default value for all test benches
   2025-11-21 10:15:05.800384 - INFO - ${teststring_variant} = I am the 'default' variant configuration of tsm-test
   2025-11-21 10:15:05.800620 - INFO - ${CONFIG} = {'WelcomeString': 'Hello... Robot Framework is running now!', 'Maximum_version': '1.0.0', 'Minimum_version': '0.6.0', 'Project': 'tsm-test_config_default', 'TargetName': 'Device_01', 'params': {}}
   2025-11-21 10:15:05.800652 - INFO - Running with configuration level 2 (variant name in command line)
   2025-11-21 10:15:05.802040 - INFO - RobotFramework AIO (original) version check passed!
   2025-11-21 10:15:05.802097 - INFO - Loaded configuration file 'C:/workplace/ROBFW/components/robotframework-testsuitesmanagement/test/testfiles/config/tsm-test_config_default.jsonp'
   2025-11-21 10:15:05.802118 - INFO - Suite Path: 'C:\workplace\ROBFW\components\robotframework-testsuitesmanagement\test\testfiles\'
   2025-11-21 10:15:05.802136 - INFO - Number of test suites: 1
   2025-11-21 10:15:05.802154 - INFO - Total number of testcases: 1
   2025-11-21 10:15:05.802197 - INFO - +- END SETUP: tm.Testsuite Setup (0.039729 s)

----

listing listing listing listing listing listing listing listing listing listing listing listing listing listing listing
listing listing listing listing listing listing listing listing listing listing listing listing listing listing listing
Some :clog:`Console log`: :clog:`Path to nowhere` and :clog:`Configuration ./imports/rf_variables.py`
and :clog:`b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f'`
and also :clog:`2025-11-21 10:15:05.762468` and also :clog:`tm.Testsuite Setup [ ./config/tsm-test_variants.jsonp ]`
listing listing listing listing listing listing listing listing listing listing listing listing listing listing listing
listing listing listing listing listing listing listing listing listing listing listing listing listing listing listing

And now in entire textblock:

.. consolelog::

   2025-11-21 10:15:05.762468 - INFO - +- START SETUP: tm.Testsuite Setup [ ./config/tsm-test_variants.jsonp ]
   2025-11-21 10:15:05.797731 - INFO - Set suite metadata 'project' to value 'tsm-test_config_default'.
   2025-11-21 10:15:05.797838 - INFO - Set suite metadata 'machine' to value 'HI-C-0044M'.
   2025-11-21 10:15:05.799145 - INFO - Set suite metadata 'tester' to value 'Queckenstedt Holger (XC-HWP/ESC3)'.
   2025-11-21 10:15:05.799342 - INFO - Set suite metadata 'testtool' to value 'Robot Framework 7.3 (Python 3.13.2 on win32)'.
   2025-11-21 10:15:05.799408 - INFO - Set suite metadata 'reference_version' to value '0.14.2.26'.
   2025-11-21 10:15:05.799443 - INFO - Set suite metadata 'reference_app_name' to value 'RobotFramework AIO (original)'.
   2025-11-21 10:15:05.799475 - INFO - Set suite metadata 'version_sw' to value 'None'.
   2025-11-21 10:15:05.799505 - INFO - Set suite metadata 'version_hw' to value 'None'.
   2025-11-21 10:15:05.799535 - INFO - Set suite metadata 'version_test' to value 'None'.
   2025-11-21 10:15:05.799909 - INFO - ${teststring_common} = I am the common teststring valid for all variants and all test benches
   2025-11-21 10:15:05.800166 - INFO - ${teststring_bench} = I am the teststring containing the default value for all test benches
   2025-11-21 10:15:05.800384 - INFO - ${teststring_variant} = I am the 'default' variant configuration of tsm-test
   2025-11-21 10:15:05.800620 - INFO - ${CONFIG} = {'WelcomeString': 'Hello... Robot Framework is running now!', 'Maximum_version': '1.0.0', 'Minimum_version': '0.6.0', 'Project': 'tsm-test_config_default', 'TargetName': 'Device_01', 'params': {}}
   2025-11-21 10:15:05.800652 - INFO - Running with configuration level 2 (variant name in command line)
   2025-11-21 10:15:05.802040 - INFO - RobotFramework AIO (original) version check passed!
   2025-11-21 10:15:05.802097 - INFO - Loaded configuration file 'C:/workplace/ROBFW/components/robotframework-testsuitesmanagement/test/testfiles/config/tsm-test_config_default.jsonp'
   2025-11-21 10:15:05.802118 - INFO - Suite Path: 'C:\workplace\ROBFW\components\robotframework-testsuitesmanagement\test\testfiles\'
   2025-11-21 10:15:05.802136 - INFO - Number of test suites: 1
   2025-11-21 10:15:05.802154 - INFO - Total number of testcases: 1
   2025-11-21 10:15:05.802197 - INFO - +- END SETUP: tm.Testsuite Setup (0.039729 s)







----

text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
Some :rcode:`Robot Framework code`: :rcode:`*** Settings ***` and :rcode:`Variables    ./imports/rf_variables.py`
and :rcode:`b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f'`
and also :rcode:`\\${robot\\_file\\_param\\_1}    robot file param 1 value`
text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 

And now in entire textblock:

.. robotcode::

   *** Settings ***

   Library    Collections
   Library    BuiltIn

   Resource    ./imports/rf_test.resource
   Variables   ./imports/rf_variables.py

   Documentation    Simple quicktest suite

   Metadata    TEST_FILE_METADATA_1       test file metadata 1 value
   Metadata    TEST_FILE_METADATA_2       test file metadata 2 value

   Suite Setup    tm.testsuite_setup    ./config/variants_config.json

   *** Keywords ***

   test-keyword
       ${is_extended_rfcore}    rf.utils.is_extended_rfcore
       IF    ${is_extended_rfcore} == ${False}
           Log    Test not supported by this Robot Framework installation    ERROR
           FAIL
       END

   *** Variables ***

   @{robot_file_param_2}    123
   ...                      456
   ...                      789

   &{robot_file_param_3}    kVal_1=Val_1
   ...                      kVal_2=Val_2
   ...                      kVal_3=Val_3

   QuickTest

       set_test_variable    ${COUNTER1}    ${0}


----

text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
Some :pcode:`Python code`: :pcode:`"LIBRARY_SCOPE" = 'GLOBAL'` and :pcode:`[1,2]`
and :pcode:`b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f'`
and also :pcode:`dictInfo = {}`
text text text text text text text text text text text text text text text text text text 
and also :pcode:`def get_version(self):` with :pcode:`@keyword`
text text text text text text text text text text text text text text text text text text 

And now in entire textblock:

.. pythoncode::

   dictInfo = {}
   dictInfo['file_name'] = THISMODULENAME
   parameter = dictInfo['file_name']

   def convert_to_int_or_float(self, value):
      """Little helper to convert a string value to an integer or a float
      """
      try:
         converted_value = int(value)
         return converted_value # is int
      except ValueError:
         pass
      try:
         converted_value = float(value)
         return converted_value # is float
      except ValueError:
         pass
      return None # not int and not float

----

The **JsonPreprocessor** supports JSON files with standard extension and standard content:

*Example*:

.. jsonscode::

   {
      "param1" : "value1",
      "param2" : "value2"
   }

In this JSON content two keys are defined: :jcode:`"param1"` and :jcode:`"param2"`.
The value of :jcode:`"param1"` is :jcode:`"value1"`. The value of :jcode:`"param2"` is :jcode:`"value2"`.

The JSONP format supports all standard JSON data types:

.. jsonscode::

   {
      "param_01" : "string",
      "param_02" : 123,
      "param_03" : 4.56,
      "param_04" : ["A", "B", "C"],
      "param_05" : {"A" : 1, "B" : 2, "C" : 3}
   }

You import another JSON file by using the reserved key :jcode:`[import]`:

.. jsonscode::

   "[import]" : "${common_config_dir}/common.jsonp",




:jcode:``

----

text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
text text text text text text text text text text text text text text text text text text 
Some :jcode:`JSONP code`: :jcode:`"Maximum_version" : "1.0.0"` and :jcode:`<<[1,2]>>`
and :jcode:`b'\\x52\\x6f\\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f'`
and also :jcode:`${params}['global']['test_dict']['tdv_key_1'] : {}`
text text text text text text text text text text text text text text text text text text 
and also :jcode:`"[import]" : "./folder2/file2.jsonp"`
text text text text text text text text text text text text text text text text text text 

And now in entire textblock:

.. jsoncode::

   {
     // A line commented out
     /* Another line commented out */

     "WelcomeString"   : "Hello... Robot Framework is running now!",

     "Maximum_version" : "1.0.0",
     "Minimum_version" : "0.6.0",

     "Project"         : "JSONP test example",
     "TargetName"      : "JSONP",

     "params" : {
                 "global" : {
                             "comment"      : "Something is /* bla bla */ commented out",
                             "inline_code"  : <<[1,2]>>,
                             "bytesequence" : b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f',
                             //
                             "test_dict"    : {},
                             ${params}['global']['test_dict']['tdv_key_1'] : {},
                             ${params}['global']['test_dict']['tdv_key_1']['tdv_key_1_1'] : <<{"A" : 1, "B" : 2}>>,
                             ${params}['global']['test_dict']['tdv_key_1']['tdv_key_1_2'] : ${params}['global']['test_dict']['tdv_key_1'],
                             "value_1" : ${params.global.test_dict.tdv_key_1},
                             "value_2" : [${params.global.test_dict.tdv_key_1}, ${params.global.test_dict.tdv_key_1}],
                             //
                             "[import]" : "./folder1/file1.jsonp",
                             "[import]" : "./folder2/file2.jsonp"
                            }
                }
   }





----

Much with :pcode:`pcode` and :pcode:`pythoncode`

That is :pcode:`for x in range(5):` and :pcode:`print(x)`

.. pythoncode::

   for x in range(5):
      print(x)

----

This is a :clog:`consolelog` example

.. consolelog::

   ==============================================================================
   2025-11-21 10:15:05.176708 - INFO - + START SUITE: Tsm-Testfile-01
   ==============================================================================
   2025-11-21 10:15:05.316778 - INFO - +- START SETUP: tm.Testsuite Setup [ ]
   2025-11-21 10:15:05.323452 - INFO - Set suite metadata 'project' to value 'RobotFramework Testsuites'.
   2025-11-21 10:15:05.323542 - INFO - Set suite metadata 'machine' to value 'HI-C-0044M'.
   2025-11-21 10:15:05.324876 - INFO - Set suite metadata 'tester' to value 'Queckenstedt Holger (XC-HWP/ESC3)'.
   2025-11-21 10:15:05.325358 - INFO - Set suite metadata 'testtool' to value 'Robot Framework 7.3 (Python 3.13.2 on win32)'.
   2025-11-21 10:15:05.325402 - INFO - Set suite metadata 'reference_version' to value '0.14.2.26'.
   2025-11-21 10:15:05.325436 - INFO - Set suite metadata 'reference_app_name' to value 'RobotFramework AIO (original)'.
   2025-11-21 10:15:05.325469 - INFO - Set suite metadata 'version_sw' to value 'None'.
   2025-11-21 10:15:05.325498 - INFO - Set suite metadata 'version_hw' to value 'None'.
   2025-11-21 10:15:05.325526 - INFO - Set suite metadata 'version_test' to value 'None'.
   2025-11-21 10:15:05.325792 - INFO - ${CONFIG} = {'Project': 'RobotFramework Testsuites', 'WelcomeString': 'Hello... RobotFramework AIO is running now!', 'Maximum_version': '1.0.0', 'Minimum_version': '0.6.0', 'TargetName': 'Device_01'}
   2025-11-21 10:15:05.325823 - WARN - Running with configuration level 4 (default configuration (fallback solution))
   2025-11-21 10:15:05.327120 - INFO - RobotFramework AIO (original) version check passed!
   2025-11-21 10:15:05.327165 - INFO - Loaded configuration file 'C:/workplace/RobotFramework/python3/ Lib/site-packages/RobotFramework_TestsuitesManagement/Config/robot_config.jsonp'
   2025-11-21 10:15:05.327185 - INFO - Suite Path: 'C:\workplace\ROBFW\components\robotframework-testsuitesmanagement\test\testfiles\'
   2025-11-21 10:15:05.327202 - INFO - Number of test suites: 1
   2025-11-21 10:15:05.327216 - INFO - Total number of testcases: 1
   2025-11-21 10:15:05.327252 - INFO - +- END SETUP: tm.Testsuite Setup (0.010474 s)
   ------------------------------------------------------------------------------
   2025-11-21 10:15:05.327338 - INFO - +- START TEST: Test Case tsm-testfile-01
   ------------------------------------------------------------------------------
   2025-11-21 10:15:05.327874 - INFO - +-- START SETUP: tm.Testcase Setup [ ]
   2025-11-21 10:15:05.327951 - INFO - Test Count: 1
   2025-11-21 10:15:05.327984 - INFO - +-- END SETUP: tm.Testcase Setup (0.00011 s)

----

This is a :clog:`consoleslog` example

.. consoleslog::

   ==============================================================================
   2025-11-21 10:15:05.176708 - INFO - + START SUITE: Tsm-Testfile-01
   ==============================================================================
   2025-11-21 10:15:05.316778 - INFO - +- START SETUP: tm.Testsuite Setup [ ]
   2025-11-21 10:15:05.323452 - INFO - Set suite metadata 'project' to value 'RobotFramework Testsuites'.
   2025-11-21 10:15:05.323542 - INFO - Set suite metadata 'machine' to value 'HI-C-0044M'.
   2025-11-21 10:15:05.324876 - INFO - Set suite metadata 'tester' to value 'Queckenstedt Holger (XC-HWP/ESC3)'.
   2025-11-21 10:15:05.325358 - INFO - Set suite metadata 'testtool' to value 'Robot Framework 7.3 (Python 3.13.2 on win32)'.
   2025-11-21 10:15:05.325402 - INFO - Set suite metadata 'reference_version' to value '0.14.2.26'.
   2025-11-21 10:15:05.325436 - INFO - Set suite metadata 'reference_app_name' to value 'RobotFramework AIO (original)'.
   2025-11-21 10:15:05.325469 - INFO - Set suite metadata 'version_sw' to value 'None'.
   2025-11-21 10:15:05.325498 - INFO - Set suite metadata 'version_hw' to value 'None'.
   2025-11-21 10:15:05.325526 - INFO - Set suite metadata 'version_test' to value 'None'.
   2025-11-21 10:15:05.325792 - INFO - ${CONFIG} = {'Project': 'RobotFramework Testsuites', 'WelcomeString': 'Hello... RobotFramework AIO is running now!', 'Maximum_version': '1.0.0', 'Minimum_version': '0.6.0', 'TargetName': 'Device_01'}
   2025-11-21 10:15:05.325823 - WARN - Running with configuration level 4 (default configuration (fallback solution))
   2025-11-21 10:15:05.327120 - INFO - RobotFramework AIO (original) version check passed!
   2025-11-21 10:15:05.327165 - INFO - Loaded configuration file 'C:/workplace/RobotFramework/python3/ Lib/site-packages/RobotFramework_TestsuitesManagement/Config/robot_config.jsonp'
   2025-11-21 10:15:05.327185 - INFO - Suite Path: 'C:\workplace\ROBFW\components\robotframework-testsuitesmanagement\test\testfiles\'
   2025-11-21 10:15:05.327202 - INFO - Number of test suites: 1
   2025-11-21 10:15:05.327216 - INFO - Total number of testcases: 1
   2025-11-21 10:15:05.327252 - INFO - +- END SETUP: tm.Testsuite Setup (0.010474 s)
   ------------------------------------------------------------------------------
   2025-11-21 10:15:05.327338 - INFO - +- START TEST: Test Case tsm-testfile-01
   ------------------------------------------------------------------------------
   2025-11-21 10:15:05.327874 - INFO - +-- START SETUP: tm.Testcase Setup [ ]
   2025-11-21 10:15:05.327951 - INFO - Test Count: 1
   2025-11-21 10:15:05.327984 - INFO - +-- END SETUP: tm.Testcase Setup (0.00011 s)

----

This is a :clog:`filessystem` example

.. filessystem::

   C:/workplace/ROBFW/components/RobotFramework_AIO/test/documentation
   C:/workplace/ROBFW/components/RobotFramework_AIO/test/documentation/RF(AIO)-TestConcept.pptx
   C:/workplace/ROBFW/components/python-jsonpreprocessor/test/pytest/executepytest.bat
   C:/workplace/ROBFW/components/RobotFramework_AIO/test/aio-test-trigger
   C:/workplace/ROBFW/components/RobotFramework_AIO/test/aio-test-trigger/ExecuteTestTrigger_Test.bat
   C:/workplace/ROBFW/components/RobotFramework_AIO/test/aio-test-trigger/config/testtrigger_config_test.json

----

This is a :clog:`jsoncode` example

.. jsoncode::

  {
    // A line commented out
    /* Another line commented out */

    "WelcomeString"   : "Hello... Robot Framework is running now!",

    "Maximum_version" : "1.0.0",
    "Minimum_version" : "0.6.0",

    "Project"         : "JSONP test example",
    "TargetName"      : "JSONP",

    "params" : {
                "global" : {
                            "comment"      : "Something is /* bla bla */ commented out",
                            "inline_code"  : <<[1,2]>>,
                            "bytesequence" : b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f',
                            //
                            "test_dict"    : {},
                            ${params}['global']['test_dict']['tdv_key_1'] : {},
                            ${params}['global']['test_dict']['tdv_key_1']['tdv_key_1_1'] : <<{"A" : 1, "B" : 2}>>,
                            ${params}['global']['test_dict']['tdv_key_1']['tdv_key_1_2'] : ${params}['global']['test_dict']['tdv_key_1'],
                            "value_1" : ${params.global.test_dict.tdv_key_1},
                            "value_2" : [${params.global.test_dict.tdv_key_1}, ${params.global.test_dict.tdv_key_1}],
                            //
                            "[import]" : "./folder1/file1.jsonp",
                            "[import]" : "./folder2/file2.jsonp"
                           }
               }
  }

----

This is a :clog:`jsonscode` example

.. jsonscode::

  {
    // A line commented out
    /* Another line commented out */

    "WelcomeString"   : "Hello... Robot Framework is running now!",

    "Maximum_version" : "1.0.0",
    "Minimum_version" : "0.6.0",

    "Project"         : "JSONP test example",
    "TargetName"      : "JSONP",

    "params" : {
                "global" : {
                            "comment"      : "Something is /* bla bla */ commented out",
                            "inline_code"  : <<[1,2]>>,
                            "bytesequence" : b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f',
                            //
                            "test_dict"    : {},
                            ${params}['global']['test_dict']['tdv_key_1'] : {},
                            ${params}['global']['test_dict']['tdv_key_1']['tdv_key_1_1'] : <<{"A" : 1, "B" : 2}>>,
                            ${params}['global']['test_dict']['tdv_key_1']['tdv_key_1_2'] : ${params}['global']['test_dict']['tdv_key_1'],
                            "value_1" : ${params.global.test_dict.tdv_key_1},
                            "value_2" : [${params.global.test_dict.tdv_key_1}, ${params.global.test_dict.tdv_key_1}],
                            //
                            "[import]" : "./folder1/file1.jsonp",
                            "[import]" : "./folder2/file2.jsonp"
                           }
               }
  }

----

* Role :jcode:`jcode` example
* Role :pcode:`pcode=1+2` example
* Role :plog:`plog` example
* Role :rcode:`rcode` example
* Role :rlog:`rlog` example

