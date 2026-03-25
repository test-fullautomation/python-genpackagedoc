This is a standard Python code example

.. code:: python

   for index in list:
       print("index")

This is a markdown directive :pcode:`pythoncode` code example:

.. pythoncode::

   for index in list:
       print("index")

This is a markdown directive :rcode:`robotcode` code example:

.. robotcode::

   FOR    ${index}    IN RANGE    0    ${nMax}
       set_local_variable    ${sLocalVariable}    ${None}
       log    === values: ${sLocalVariable}    console=yes
   END


This is inline Python code: :pcode:`print("Hello RobotFramework AIO")`

This is inline Robot code (1): :rcode:`log    Hello RobotFramework AIO`

This is inline Robot code (2): :rcode:`log~~~~Hello RobotFramework AIO`



---


This method executes the version check at high level.

The :pcode:`min_version` and the :pcode:`max_version` are checked against the :pcode:`reference_version`.

If the :pcode:`reference_version` is :pcode:`None` (= not defined by user), the internally
defined :pcode:`bundle_version` (either RobotFramework AIO or TestsuitesManagement) will be used as reference instead.

The execution includes error messages and exception handling (in opposite to the low level method :pcode:`verify_version`).
Impact is that this method influences the execution of the application that calls it.

**Arguments:**

* :pcode:`min_version`

  / *Condition*: optional / *Type*: str /

* :pcode:`max_version`

  / *Condition*: optional / *Type*: str /

* :pcode:`reference_version`

  / *Condition*: optional / *Type*: str /

* :pcode:`ext_logger`

  / *Condition*: optional / *Type*: object /

* :pcode:`status_messages`

  / *Condition*: optional / *Type*: dict /

**Returns:**

* :pcode:`True`

  / *Type*: boolean /

  Executed version check passed or check not executed.

* :pcode:`False`

  / *Type*: boolean /

  Executed version check failed.

**Example:**

.. robotcode::

    *** Settings ***

    Library    RobotFramework_TestsuitesManagement    AS    tm

    *** Test Cases ***

    ${result}=    tm.check_version    min_version=0.1.0    max_version=0.20.0
    log    check_version result: ${result}    console=yes


**pythoncode example**

.. pythoncode::

   # some example code

   for index in list:
       print("index")

   # some classes to enable Python code listings in HTML format

   class CustomHTMLTranslator(HTMLTranslator):
       """
   Desvription of class ``CustomHTMLTranslator``
       """
       def visit_literal_block(self, node):
           """
   Desvription of method ``visit_literal_block``
           """
           if node.get('custom_latex_env') == 'pythoncode':
               code = node.astext()
               highlighted = highlight(code, PythonLexer(), HtmlFormatter(style="colorful", full=True, linenos=True, nowrap=True))
               self.body.append(f'<<pre class="pythoncode">>')
               self.body.append(f'<<code class="pythoncode">>{highlighted}<</code>><</pre>>')
               raise nodes.SkipNode
           else:
               super().visit_literal_block(node)

   class CustomHTMLWriter(htmlWriter):
       """
   Desvription of class ``CustomHTMLWriter``
       """
       def __init__(self):
           super().__init__()
           self.translator_class = CustomHTMLTranslator



.. jsoncode::

   {
      // common parameters
      "[import]" : "./common.jsonp",
      //
      // component B parameters
      "componentB_param_1" : "componentB value 1",
      "componentB_param_2" : "componentB value 2",
      // overwrite parameter initialized by imported file
      "common_param_2" : "common componentB value 2"
   }




