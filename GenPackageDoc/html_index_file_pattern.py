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
# 29.05.2026
#
# --------------------------------------------------------------------------------------------------------------

"""
File containing a pattern for the index.html file, that is the entry point for the documentation in HTML format.

The index.html file contains a search function. Therefore the file must be opened on a web server
(otherwise the search results will not be displayed properly).
"""

html_index_file_with_search_pattern = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>###COMPONENTNAME### Documentation</title>
  <style>
    body {
      margin: 0;
      font-family: sans-serif;
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    #header {
      width: 100%;
      background: #1976d2;
      color: #fff;
      padding: 0.5em 1em;
      box-sizing: border-box;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    #header-title {
      font-size: 1.3em;
      font-weight: bold;
      letter-spacing: 1px;
    }
    #header-search {
      display: flex;
      align-items: center;
      gap: 0.5em;
    }
    #searchbox {
      padding: 0.3em 0.7em;
      border-radius: 4px;
      border: 1px solid #ccc;
      font-size: 1em;
      width: 260px;
      color: #222;
    }
    #searchresults {
      position: fixed;
      top: 2.5em;
      right: 10px;
      left: auto;
      transform: none;
      background: #fff;
      color: #222;
      border: 1px solid #ccc;
      border-radius: 4px;
      min-width: 300px;
      max-width: 400px;
      max-height: calc(100vh - 3em);  /* Fill available space from top position to bottom (scrollbar in case of lots of results) */
      overflow-y: auto;
      z-index: 1000;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      list-style: none;
      padding: 0.5em 0.7em;
      margin: 0;
      display: none;
    }
    #searchresults li { margin: 0.2em 0; }
    #container {
      display: flex;
      flex: 1;
      min-height: 0;
    }
    #sidebar {
      width: 220px;
      background: #f5f5f5;
      border-right: 1px solid #ccc;
      padding: 1em 0.5em;
      box-sizing: border-box;
      overflow-y: auto;
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
    }

    /* Type-Filter Dropdown */
    #type-filter {
      padding: 5px 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 14px;
      background: #fff;
      color: #333;
      cursor: pointer;
      height: 32px;               /* same height as search field and clear button */
      vertical-align: middle;
      min-width: 140px;
    }

    #type-filter:focus {
      outline: 2px solid #005691; /* focus-indikator */
      outline-offset: 1px;
    }

    /* Typ-Badge within search results */
    .result-type-badge {
      display: inline-block;
      font-size: 0.75em;
      font-weight: bold;
      color: #fff;
      background: #1976d2;
      border-radius: 3px;
      padding: 1px 5px;
      margin-right: 4px;
      vertical-align: middle;
    }
  </style>

<script>
  const searchIndex = [
###SEARCH_INDEX_ROWS###
  ];

  // -----------------------------------------------------------------------
  // populateTypeFilter(): Fills dropdown with all available types.
  // Called once on load (DOMContentLoaded / window.onload).
  // -----------------------------------------------------------------------
  function populateTypeFilter() {
    const select = document.getElementById('type-filter');

    // Collect all unique types from the index and sort alphabetically
    const types = [...new Set(searchIndex.map(e => e.type))].sort();

    // First option: "All types" (no  filter)
    const allOption = document.createElement('option');
    allOption.value = "";
    allOption.textContent = "All types";
    select.appendChild(allOption);

    for (const t of types) {
      const opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      select.appendChild(opt);
    }
  }

  // -----------------------------------------------------------------------
  // showFile(): Called from Sidebar-Menu (without Highlight-Bedarf)
  // -----------------------------------------------------------------------
  function showFile(file, el, searchText) {
    const iframe = document.getElementById('content');
    iframe.onload = null;
    iframe.src = file;
    document.querySelectorAll('#sidebar a').forEach(a => a.classList.remove('active'));
    if (el) el.classList.add('active');
    if (searchText) {
      iframe.onload = function() {
        iframe.onload = null;
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while (node = walker.nextNode()) {
          if (node.nodeValue.includes(searchText)) {
            node.parentElement.scrollIntoView({behavior: 'smooth', block: 'center'});
            break;
          }
        }
      };
    }
  }

  // -----------------------------------------------------------------------
  // searchDocs(): Searches within searchIndex and displays results.
  //
  //   Three modes of operation:
  //   1. No search term, no type filter -> hide results list.
  //   2. No search term, type filter active -> show all entries of that type.
  //   3. Search term (+ optional type filter) -> filtered name search.
  // -----------------------------------------------------------------------
  function searchDocs() {
    const query = document.getElementById('searchbox').value.trim().toLowerCase();
    const selectedType = document.getElementById('type-filter').value;
    const results = document.getElementById('searchresults');
    results.innerHTML = "";

    if (!query && !selectedType) {
      results.style.display = 'none';
      return;
    }

    let found = 0;
    for (const entry of searchIndex) {
      // Filter nach Typ
      if (selectedType && entry.type !== selectedType) continue;
      // Filter nach Suchbegriff
      if (query && !entry.name.toLowerCase().includes(query)) continue;

      const li = document.createElement('li');

      // Typ-Badge
      const badge = document.createElement('span');
      badge.className = 'result-type-badge';
      badge.textContent = entry.type;
      li.appendChild(badge);

      // Link
      const link = document.createElement('a');
      link.href = '#';
      link.textContent = entry.name;

      // Daten in data-* Attributen speichern
      link.dataset.file = entry.file;
      link.dataset.searchText = entry.name;
      link.dataset.sidebarId = entry.sidebarId;

      // Event-Handler mit addEventListener (sicher)
      link.addEventListener('click', function(e) {
        e.preventDefault();
        showFileWithScroll(
          this.dataset.file,
          this,
          this.dataset.searchText,
          this.dataset.sidebarId
        );
        document.getElementById('searchresults').style.display = 'none';
      });

      li.appendChild(link);
      results.appendChild(li);
      found++;
    }

    if (found === 0) {
      results.innerHTML = "<li><i>No results found.</i></li>";
    }
    results.style.display = 'block';
  }

  // -----------------------------------------------------------------------
  // showFileWithScroll(): Loads the target file in the iframe, highlights the
  // search term and scrolls to the first match.
  // -----------------------------------------------------------------------
  function showFileWithScroll(file, el, searchText, sidebarId) {
    const iframe = document.getElementById('content');

    // mark acrive link
    document.querySelectorAll('#sidebar a').forEach(a => a.classList.remove('active'));

    // activate the corresponding Sidebar-Link
    if (sidebarId) {
      const sidebarLink = document.getElementById(sidebarId);
      if (sidebarLink) {
        sidebarLink.classList.add('active');
      }
    }

    // Reliable filename comparison via URL object
    function getFilename(src) {
      try {
        return new URL(src).pathname.split('/').pop();
      } catch(e) {
        return src.split('/').pop();
      }
    }

    function doHighlightAndScroll() {
      const doc = iframe.contentDocument || iframe.contentWindow.document;
      if (!doc || !doc.body) return;

      // 1. Remove previous highlights and normalize DOM
      doc.querySelectorAll('span.__highlight__').forEach(span => {
        const text = doc.createTextNode(span.textContent);
        span.parentNode.replaceChild(text, span);
      });
      doc.body.normalize();

      if (!searchText) return;

      // 2. Gather all matching text nodes (no DOM changes while walking!)
      const searchLower = searchText.toLowerCase();
      const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null, false);
      const matchingNodes = [];
      let node;
      while (node = walker.nextNode()) {
        if (node.nodeValue.toLowerCase().includes(searchLower)) {
          matchingNodes.push(node);
        }
      }

      // 3. DOM manipulation (outside walker)
      let firstSpan = null;
      for (const textNode of matchingNodes) {
        let current = textNode;
        while (current && current.nodeValue) {
          const idx = current.nodeValue.toLowerCase().indexOf(searchLower);
          if (idx === -1) break;

          const span = doc.createElement('span');
          span.className = '__highlight__';
          span.style.background = '#ffff66';
          span.style.color = '#000';
          span.style.borderRadius = '2px';
          // Use original spelling from the document
          span.textContent = current.nodeValue.slice(idx, idx + searchText.length);

          const after = current.splitText(idx);
          after.nodeValue = after.nodeValue.slice(searchText.length);
          current.parentNode.insertBefore(span, after);

          if (!firstSpan) firstSpan = span;
          current = after;
        }
      }

      // 4. Scroll via contentWindow.scrollTo() with setTimeout for
      //    one render cycle after DOM mutation
      if (firstSpan) {
        setTimeout(function() {
          const rect = firstSpan.getBoundingClientRect();
          const iframeScrollY = iframe.contentWindow.scrollY
                             || iframe.contentWindow.pageYOffset
                             || 0;
          const targetY = rect.top + iframeScrollY - (iframe.clientHeight / 2);
          iframe.contentWindow.scrollTo({ top: targetY, behavior: 'smooth' });
        }, 50);
      }
    }

    // Same file already loaded -> execute directly, no onload needed
    // New file -> load first, then execute in onload
    const currentFile = getFilename(iframe.src);
    if (currentFile === file) {
      doHighlightAndScroll();
    } else {
      iframe.onload = function() {
        iframe.onload = null; // remove handler after call
        doHighlightAndScroll();
      };
      iframe.src = file;
    }
  }

  // -----------------------------------------------------------------------
  // Enter key in search field opens the first search result
  // -----------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function() {
    // fill dropdown with types
    populateTypeFilter();

    const searchbox = document.getElementById('searchbox');
    searchbox.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        const results  = document.getElementById('searchresults');
        const firstLink = results.querySelector('a');
        if (firstLink) {
          firstLink.click();
          results.style.display = 'none';
          searchbox.blur();
          e.preventDefault();
        }
      }
    });

    // Type filter change immediately triggers a new search
    document.getElementById('type-filter').addEventListener('change', searchDocs);
  });

  // -----------------------------------------------------------------------
  // window.onload: load start page + register UI-Event-Handler
  // -----------------------------------------------------------------------
  window.onload = function() {
    showFile('###ONLOADFILENAME###', document.getElementById('###ONLOADHTMLID###'));

    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
      const searchbox  = document.getElementById('searchbox');
      const results    = document.getElementById('searchresults');
      const typeFilter = document.getElementById('type-filter');
      if (
        !searchbox.contains(e.target) &&
        !results.contains(e.target) &&
        !typeFilter.contains(e.target)
      ) {
        results.style.display = 'none';
      }
    });

    // Show search results again when focusing on the search field
    document.getElementById('searchbox').addEventListener('focus', function() {
      const results = document.getElementById('searchresults');
      if (results.innerHTML.trim() !== '') results.style.display = 'block';
    });

    // Clear-Button: reset search field, filter and results
    document.getElementById('clearsearch').onclick = function() {
      const searchbox  = document.getElementById('searchbox');
      const results    = document.getElementById('searchresults');
      const typeFilter = document.getElementById('type-filter');
      const iframe     = document.getElementById('content');

      searchbox.value   = "";
      typeFilter.value  = "";        // reset filter to "All types"
      results.innerHTML = "";
      results.style.display = 'none';

      // Remove all highlights in iframe
      const doc = iframe.contentDocument || iframe.contentWindow.document;
      if (doc) {
        const highlights = doc.querySelectorAll('span.__highlight__');
        highlights.forEach(span => {
          const text = doc.createTextNode(span.textContent);
          span.parentNode.replaceChild(text, span);
        });
        doc.body.normalize();
      }

      searchbox.focus();
    };
  };
</script>

</head>
<body>
  <div id="header">
    <span id="header-title">###COMPONENTNAME###</span>
    <div id="header-search">
      <input id="searchbox" type="text"
             aria-label="Search documentation"
             placeholder="Search class, method, function..."
             oninput="searchDocs()">
      <select id="type-filter" aria-label="Filter by type">
        <!-- Wird dynamisch per populateTypeFilter() befüllt -->
      </select>
      <button id="clearsearch" title="Reset search" aria-label="Clear search"
              style="margin-left:4px;padding:0 8px;font-size:1.1em;line-height:1.5em;cursor:pointer;">
        &#x1F5D1;
      </button>
      <ul id="searchresults"></ul>
    </div>
  </div>

  <div id="container">
    <nav id="sidebar">
      <ul>
###HTML_FILES_ROWS###
      </ul>
    </nav>
    <iframe id="content"></iframe>
  </div>
</body>
</html>
"""

search_index_row_pattern = """{type: "###SITYPE###", name: "###SINAME###", file: "###SIFILE###", sidebarId: "###HTMLID###"},"""

html_files_row_pattern = """<li><a href="#" id="###HTMLID###" onclick="showFile('###FILENAME###', this);return false;">###FILESHORTNAME###</a></li>"""
