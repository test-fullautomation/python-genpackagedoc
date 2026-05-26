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
# 26.05.2026
#
# --------------------------------------------------------------------------------------------------------------

"""
File containing a pattern for the index.html file, that is the entry point for the documentation in HTML format.

The index.html file contains a search function. Therefore the file must be opened on a web server
(otherwise the search results will not be displayed properly).
"""

html_index_file_with_search_pattern = """
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>###COMPONENTNAME### Documentation</title>
  <style>
    body { margin: 0; font-family: sans-serif; }
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
      max-height: 70vh;        /* Scrollbar bei vielen Ergebnissen */
      overflow-y: auto;
      z-index: 1000;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      list-style: none;
      padding: 0.5em 0.7em;
      margin: 0;
      display: none;
    }
    #searchresults li { margin: 0.2em 0; }
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

    /* Type-Filter Dropdown */
    #type-filter {
      padding: 5px 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 14px;
      background: #fff;
      color: #333;
      cursor: pointer;
      height: 32px;               /* gleiche Höhe wie Suchfeld / Clear-Button  */
      vertical-align: middle;
      min-width: 140px;
    }

    #type-filter:focus {
      outline: 2px solid #005691; /* Fokus-Indikator */
      outline-offset: 1px;
    }

    /* Typ-Badge in den Suchergebnissen */
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
  // populateTypeFilter(): Befüllt das Dropdown mit allen vorhandenen Typen
  // Wird einmalig beim Laden aufgerufen (DOMContentLoaded / window.onload).
  // -----------------------------------------------------------------------
  function populateTypeFilter() {
    const select = document.getElementById('type-filter');

    // Alle eindeutigen Typen aus dem Index sammeln und alphabetisch sortieren
    const types = [...new Set(searchIndex.map(e => e.type))].sort();

    // Erste Option: "Alle Typen" (kein Filter)
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
  // showFile(): Wird vom Sidebar-Menü aufgerufen (ohne Highlight-Bedarf)
  // -----------------------------------------------------------------------
  function showFile(file, el, searchText) {
    const iframe = document.getElementById('content');
    iframe.src = file;
    document.querySelectorAll('#sidebar a').forEach(a => a.classList.remove('active'));
    if (el) el.classList.add('active');
    if (searchText) {
      iframe.onload = function() {
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
  // searchDocs(): Durchsucht den searchIndex und zeigt Ergebnisse an.
  //
  //   Drei Betriebsmodi:
  //   1. Kein Suchbegriff, kein Typ-Filter  → Ergebnisliste ausblenden.
  //   2. Kein Suchbegriff, Typ-Filter aktiv → alle Einträge des Typs zeigen.
  //   3. Suchbegriff (+ optionaler Typ-Filter) → gefilterte Namenssuche.
  // -----------------------------------------------------------------------
  function searchDocs() {
    const query      = document.getElementById('searchbox').value.trim().toLowerCase();
    const typeFilter = document.getElementById('type-filter').value; // "" = alle
    const results    = document.getElementById('searchresults');
    results.innerHTML = "";

    // Modus 1: nichts eingegeben, kein Typ gewählt → ausblenden
    if (!query && !typeFilter) {
      results.style.display = 'none';
      return;
    }

    let found = 0;
    for (const entry of searchIndex) {
      // Typ-Filter anwenden
      if (typeFilter && entry.type !== typeFilter) continue;

      // Modus 2: nur Typ-Filter (kein Suchbegriff) → alle Treffer des Typs
      // Modus 3: Suchbegriff muss im Namen vorkommen
      if (query && !entry.name.toLowerCase().includes(query)) continue;

      const li = document.createElement('li');
      li.innerHTML =
        `<span class="result-type-badge">${entry.type}</span>` +
        `<a href='#' onclick="showFileWithScroll('${entry.file}', this, '${entry.name}');` +
        `document.getElementById('searchresults').style.display='none';return false;">` +
        `${entry.name}</a>`;
      results.appendChild(li);
      found++;
    }

    if (found === 0) {
      results.innerHTML = "<li><i>No results found.</i></li>";
    }
    results.style.display = 'block';
  }

  // -----------------------------------------------------------------------
  // showFileWithScroll(): Lädt die Zieldatei im iframe, hebt den
  // Suchbegriff hervor und scrollt zum ersten Treffer.
  // -----------------------------------------------------------------------
  function showFileWithScroll(file, el, searchText) {
    const iframe = document.getElementById('content');

    // Aktiven Link markieren
    document.querySelectorAll('#sidebar a').forEach(a => a.classList.remove('active'));
    if (el) el.classList.add('active');

    // Zuverlässiger Dateinamen-Vergleich via URL-Objekt
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

      // 1. Vorherige Hervorhebungen entfernen und DOM normalisieren
      doc.querySelectorAll('span.__highlight__').forEach(span => {
        const text = doc.createTextNode(span.textContent);
        span.parentNode.replaceChild(text, span);
      });
      doc.body.normalize();

      if (!searchText) return;

      // 2. Alle passenden Textnodes sammeln (kein DOM-Eingriff während des Walkens!)
      const searchLower = searchText.toLowerCase();
      const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null, false);
      const matchingNodes = [];
      let node;
      while (node = walker.nextNode()) {
        if (node.nodeValue.toLowerCase().includes(searchLower)) {
          matchingNodes.push(node);
        }
      }

      // 3. DOM manipulieren (außerhalb des Walkers)
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
          // Originalschreibweise aus dem Dokument verwenden
          span.textContent = current.nodeValue.substr(idx, searchText.length);

          const after = current.splitText(idx);
          after.nodeValue = after.nodeValue.substr(searchText.length);
          current.parentNode.insertBefore(span, after);

          if (!firstSpan) firstSpan = span;
          current = after;
        }
      }

      // 4. Scrollen via contentWindow.scrollTo() mit setTimeout für
      //    einen Render-Zyklus nach der DOM-Mutation
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

    // Gleiche Datei bereits geladen → direkt ausführen, kein onload nötig
    // Neue Datei → erst laden, dann in onload ausführen
    const currentFile = getFilename(iframe.src);
    if (currentFile === file) {
      doHighlightAndScroll();
    } else {
      iframe.onload = function() {
        iframe.onload = null; // Handler nach einmaligem Aufruf entfernen
        doHighlightAndScroll();
      };
      iframe.src = file;
    }
  }

  // -----------------------------------------------------------------------
  // Enter-Taste im Suchfeld öffnet das erste Suchergebnis
  // -----------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function() {
    // Dropdown mit Typen befüllen
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

    // Typ-Filter-Änderung löst sofort eine neue Suche aus
    document.getElementById('type-filter').addEventListener('change', searchDocs);
  });

  // -----------------------------------------------------------------------
  // window.onload: Startseite laden + UI-Event-Handler registrieren
  // -----------------------------------------------------------------------
  window.onload = function() {
    showFile('###ONLOADFILENAME###', document.getElementById('###ONLOADHTMLID###'));

    // Suchergebnisse ausblenden beim Klick außerhalb
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

    // Suchergebnisse wieder einblenden beim Fokus auf das Suchfeld
    document.getElementById('searchbox').addEventListener('focus', function() {
      const results = document.getElementById('searchresults');
      if (results.innerHTML.trim() !== '') results.style.display = 'block';
    });

    // Clear-Button: Suchfeld, Filter und Ergebnisse zurücksetzen
    document.getElementById('clearsearch').onclick = function() {
      const searchbox  = document.getElementById('searchbox');
      const results    = document.getElementById('searchresults');
      const typeFilter = document.getElementById('type-filter');
      searchbox.value   = "";
      typeFilter.value  = "";        // Filter auf "All types" zurücksetzen
      results.innerHTML = "";
      results.style.display = 'none';
      searchbox.focus();
    };
  };
</script>

</head>
<body>
  <div id="header">
    <span id="header-title">###COMPONENTNAME###</span>
    <span id="header-search">
      <input id="searchbox" type="text"
             placeholder="Search class, method, function..."
             oninput="searchDocs()">
      <select id="type-filter">
        <!-- Wird dynamisch per populateTypeFilter() befüllt -->
      </select>
      <button id="clearsearch" title="Suche zurücksetzen"
              style="margin-left:4px;padding:0 8px;font-size:1.1em;line-height:1.5em;cursor:pointer;">
        &#10006;
      </button>
      <ul id="searchresults"></ul>
    </span>
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

search_index_row_pattern = """{type: "###SITYPE###", name: "###SINAME###", file: "###SIFILE###"},"""

html_files_row_pattern = """<li><a href="#" id="###HTMLID###" onclick="showFile('###FILENAME###', this);return false;">###FILESHORTNAME###</a></li>"""

