JSON with **pythoncode**


.. pythoncode::

  {
    "WelcomeString"   : "Hello... Robot Framework is running now!",

    [import]

    global

    anything

    // A line commented out

    "comment" : "Something is /* bla bla */ commented out",

    "value" : <<[1,2]>>,
    "bytesequence" : b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f',

    "Maximum_version" : "1.0.0",
    "Minimum_version" : "0.6.0",

    "Project"         : "tsm-test_config_nested.1",
    "TargetName"      : "Device_01",

    "params" : {
                "global" : {
                            "testdictionary_variant" : {},
                            ${params}['global']['testdictionary_variant']['tdv_key_1'] : {},
                            ${params}['global']['testdictionary_variant']['tdv_key_1']['tdv_key_1_1'] : "value_tdv_key_1_1",
                            ${params}['global']['testdictionary_variant']['tdv_key_1']['tdv_key_1_2'] : "value_tdv_key_1_2",
                            "testlist_variant"                                                        : ["A", "B", "C"],
                            //
                            "[import]"                                                                : "./tsm-test_config_common.jsonp",
                            "[import]"                                                                : "./import.1/tsm-test_config_nested.1.1.jsonp",
                            //
                            "teststring_variant"                                                      : "I am the variant 'nested.1' configuration of tsm-test",
                            ${params}['global']['testdictionary_variant']['tdv_key_1']['tdv_key_1_2'] : "value_tdv_key_1_2_after_import",
                            ${params}['global']['testdictionary_variant']['tdv_key_2']['tdv_key_2_1'] : "value_tdv_key_2_1_after_import_new"
                           }
               }
  }

----

JSON with **jsoncode**

.. jsoncode::

  {
    "WelcomeString"   : "Hello... Robot Framework is running now!",

    [import]

    global

    anything

    // A line commented out

    "comment" : "Something is /* bla bla */ commented out",

    "value" : <<[1,2]>>,
    "bytesequence" : b'\x52\x6f\x62\x6f\x74\x46\x72\x61\x6d\x65\x77\x6f\x72\x6b\x20\x41\x49\x4f',

    "Maximum_version" : "1.0.0",
    "Minimum_version" : "0.6.0",

    "Project"         : "tsm-test_config_nested.1",
    "TargetName"      : "Device_01",

    "params" : {
                "global" : {
                            "testdictionary_variant" : {},
                            ${params}['global']['testdictionary_variant']['tdv_key_1'] : {},
                            ${params}['global']['testdictionary_variant']['tdv_key_1']['tdv_key_1_1'] : "value_tdv_key_1_1",
                            ${params}['global']['testdictionary_variant']['tdv_key_1']['tdv_key_1_2'] : "value_tdv_key_1_2",
                            "testlist_variant"                                                        : ["A", "B", "C"],
                            //
                            "[import]"                                                                : "./tsm-test_config_common.jsonp",
                            "[import]"                                                                : "./import.1/tsm-test_config_nested.1.1.jsonp",
                            //
                            "teststring_variant"                                                      : "I am the variant 'nested.1' configuration of tsm-test",
                            ${params}['global']['testdictionary_variant']['tdv_key_1']['tdv_key_1_2'] : "value_tdv_key_1_2_after_import",
                            ${params}['global']['testdictionary_variant']['tdv_key_2']['tdv_key_2_1'] : "value_tdv_key_2_1_after_import_new"
                           }
               }
  }











