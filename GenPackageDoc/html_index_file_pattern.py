# **************************************************************************************************************
#
#  Copyright 2020-2026 Robert Bosch GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# **************************************************************************************************************
#
# html_index_file_pattern.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 22.04.2026
#
# --------------------------------------------------------------------------------------------------------------

"""
File containing a pattern for the index.html file, that is the entry point for the documentation in HTML format.
"""

html_index_file_pattern = """
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>###APP_NAME### Documentation</title>
  <style>
    body { margin: 0; font-family: sans-serif; }
    #container { display: flex; height: 100vh; }
    #sidebar {
      width: 220px;
      background: #f5f5f5;
      border-right: 1px solid #ccc;
      padding: 1em 0.5em;
      box-sizing: border-box;
      overflow-y: auto;
      max-height: 100vh;
    }
    #sidebar ul { list-style: none; padding: 0; }
    #sidebar li { margin: 0.5em 0; }
    #sidebar a {
      color: #333;
      text-decoration: none;
      display: block;
      padding: 0.3em 0.5em;
      border-radius: 4px;
    }
    #sidebar hr {
      border: none;
      border-top: 1.5px solid #0000FF;
      margin: 0.7em 0;
    }
    #sidebar a:hover, #sidebar a.active {
      background: #e0e0e0;
      color: #1976d2;
    }
    #content {
      flex: 1;
      border: none;
      height: 100vh;
    }
  </style>
  <script>
    function showFile(file, el) {
      document.getElementById('content').src = file;
      // Mark active
      document.querySelectorAll('#sidebar a').forEach(a => a.classList.remove('active'));
      if (el) el.classList.add('active');
    }
    window.onload = function() {
      showFile('###ON_OPEN_SHOW_FILE###', document.getElementById('file1link'));
    }
  </script>
</head>
<body>
  <div id="container">
    <nav id="sidebar">
      <strong>###APP_NAME###</strong>
      <ul>
###HTML_FILE_LIST###
      </ul>
    </nav>
    <iframe id="content"></iframe>
  </div>
</body>
</html>
"""

html_list_row = """<li><a href="#" id="###FILE_ID_NAME###" onclick="showFile('###FILE_NAME###', this);return false;">###FILE_NAME_ONLY###</a></li>"""

