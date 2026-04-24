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
# markdown_extensions.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 23.04.2026
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing markdown extensions:
Markdown directives and markdown roles mapped to LaTeX code listings and console listings.
"""
import re

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.parsers.rst import roles
from docutils.writers.latex2e import Writer
from docutils.writers.latex2e import LaTeXTranslator

from docutils.writers.html5_polyglot import Writer as htmlWriter
from docutils.writers.html5_polyglot import HTMLTranslator

from pygments import highlight
from pygments.lexers.python import PythonLexer
from pygments.lexers.data import JsonLexer
from pygments.lexers.robotframework import RobotFrameworkLexer

from pygments.lexer import RegexLexer
from pygments.formatters import HtmlFormatter

from pygments.token import Keyword, Name, Token, String, Comment, Number, Punctuation, Operator, Text

def latex_inline_escape(text):
    # >>> needs to be verified (characters commented out not accepted by inline literal (LaTeX listings))
    replacements = [
        ('{',  r'\{'),
        ('}',  r'\}'),
        ('$',  r'\$'),
        ('[',  r'{[}'),
        (']',  r'{]}'),
        ('#',  r'\#'),
        ('%',  r'\%'),
        ('&',  r'\&'),
        ('_',  r'\_'),
        # ('^',  r'\^{}')
        # ('~',  r'\~{}')
        # ('\\', r'\textbackslash{}') # must be the last
        # ('\\', r'\texttt{\textbackslash}') # must be the last
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def table_to_latex(table):
    lines = [line.strip() for line in table.strip().splitlines() if line.strip() and not line.strip().startswith('#')]
    rows = [ [cell.strip() for cell in line.split('|')] for line in lines ]
    ncols = max(len(row) for row in rows)

    # LaTeX Tabellenkopf
    latex = []
    latex.append(r'\begin{tabular}{|' + '|'.join(['c']*ncols) + '|}')
    latex.append(r'\hline')

    for row in rows:
        row += [''] * (ncols - len(row))
        colored_row = [r'\cellcolor[HTML]{F5F5F5} ' + cell for cell in row]
        latex.append(' & '.join(colored_row) + r' \\ \hline')

    latex.append(r'\end{tabular}')
    return '\n'.join(latex)



def table_to_html(table, css_class="simpletable"):
    lines = [line.strip() for line in table.strip().splitlines() if line.strip() and not line.strip().startswith('#')]
    rows = [ [cell.strip() for cell in line.split('|')] for line in lines ]

    html = []
    html.append(f'<table class="{css_class}">')
    for row in rows:
        html.append('  <tr>')
        for cell in row:
            html.append(f'    <td>{cell}</td>')
        html.append('  </tr>')
    html.append('</table>')
    return '\n'.join(html)



class CustomJsonLexer(RegexLexer):
    name = 'CustomJson'
    aliases = ['customjson']
    filenames = ['*.json', '*.jsonp']

    tokens = {
        'root': [
            (r'\$\{[^}]+\}', Name.Variable),           # ${...}
            (r"\['[^']+'\]", Name.Attribute),          # ['...']
            (r'"\[import\]"', Keyword.Reserved),       # "[import]"
            (r'<<|>>', Keyword.Declaration),           # << oder >>
            (r'//.*$', Comment.Single),                # Kommentar (einzeilig)
            (r'/\*.*?\*/', Comment.Multiline),         # Inline-Kommentar (Block)
            (r'"(\\\\|\\"|[^"])*"', String),           # Standard-String
            (r'\d+\.\d+', Number.Float),               # Float
            (r'\d+', Number.Integer),                  # Integer
            (r'[{}\[\],:]', Punctuation),              # JSON-Punctuation
            (r'\s+', Text),                            # Whitespace
            (r'.', Text),                              # Sonstiges
        ],
    }


class CustomRobotFrameworkLexer(RobotFrameworkLexer):
    """
CustomRobotFrameworkLexer: extends RobotFrameworkLexer with extra keywords (case-sensitive)
    """
    name    = 'CustomRobotFramework'
    aliases = ['customrobotframework']
    EXTRA_KEYWORDS = {
        'PASS': Token.Pass,
        'FAIL': Token.Fail,
        'UNKNOWN': Token.Unknown,
    }

    def get_tokens_unprocessed(self, text):
        for index, token, value in super().get_tokens_unprocessed(text):
            if token is Name.Function and value in self.EXTRA_KEYWORDS:
                yield index, self.EXTRA_KEYWORDS[value], value
            else:
                yield index, token, value



class CustomLaTeXTranslator(LaTeXTranslator):
    """
Mapping between markdown and LaTeX w.r.t.:

* Python code listings
* Robot code listings
* Json code listings
* Python log listings
* Robot log listings
    """
    # markdown directives
    def visit_literal_block(self, node):
        # code listings
        if node.get('custom_code') == 'pythoncode':
            self.body.append('\\begin{pythoncode}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{pythoncode}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'pythonscode':
            self.body.append('\\begin{pythonscode}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{pythonscode}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'jsoncode':
            self.body.append('\\begin{jsoncode}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{jsoncode}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'jsonscode':
            self.body.append('\\begin{jsonscode}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{jsonscode}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotcode':
            self.body.append('\\begin{robotcode}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{robotcode}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotscode':
            self.body.append('\\begin{robotscode}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{robotscode}\n')
            raise nodes.SkipNode
        # log listings and file system paths (new)
        elif node.get('custom_code') == 'consolelog':
            self.body.append('\\begin{consolelog}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{consolelog}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'consoleslog':
            self.body.append('\\begin{consoleslog}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{consoleslog}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'filesystem':
            self.body.append('\\begin{filesystem}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{filesystem}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'filessystem':
            self.body.append('\\begin{filessystem}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{filessystem}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'anycontent':
            self.body.append('\\begin{anycontent}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{anycontent}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'anyscontent':
            self.body.append('\\begin{anyscontent}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{anyscontent}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'highlight':
            self.body.append('\\begin{highlight}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{highlight}\n')
            raise nodes.SkipNode
        # log listings and file system paths
        elif node.get('custom_code') == 'pythonlog': # DEPRECATED, mapping: old name -> new name
            self.body.append('\\begin{consolelog}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{consolelog}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'pythonslog': # DEPRECATED, mapping: old name -> new name
            self.body.append('\\begin{consoleslog}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{consoleslog}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotlog': # DEPRECATED, mapping: old name -> new name
            self.body.append('\\begin{consolelog}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{consolelog}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotslog': # DEPRECATED, mapping: old name -> new name
            self.body.append('\\begin{consoleslog}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{consoleslog}\n')
            raise nodes.SkipNode
        # under construction
        elif node.get('custom_code') == 'simpletable':
            self.body.append('\n')
            self.body.append(table_to_latex(node.astext()))
            self.body.append('\n')
            raise nodes.SkipNode
        else:
            super().visit_literal_block(node)
    # markdown roles
    def visit_literal(self, node):
        # code listings
        if node.get('custom_code') == 'pcode':
            self.body.append('\\pcode{' + latex_inline_escape(node.astext()) + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'rcode':
            self.body.append('\\rcode{' + latex_inline_escape(node.astext()) + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'jcode':
            self.body.append('\\jcode{' + latex_inline_escape(node.astext()) + '}')
            raise nodes.SkipNode
        # log listings and file system paths (new)
        elif node.get('custom_code') == 'clog':
            self.body.append('\\clog{' + latex_inline_escape(node.astext()) + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'fsystem':
            self.body.append('\\fsystem{' + latex_inline_escape(node.astext()) + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'acontent':
            self.body.append('\\acontent{' + latex_inline_escape(node.astext()) + '}')
            raise nodes.SkipNode
        # log listings and file system paths
        elif node.get('custom_code') == 'plog': # DEPRECATED, mapping: old name -> new name
            self.body.append('\\clog{' + latex_inline_escape(node.astext()) + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'rlog': # DEPRECATED, mapping: old name -> new name
            self.body.append('\\clog{' + latex_inline_escape(node.astext()) + '}')
            raise nodes.SkipNode
        else:
            super().visit_literal(node)

    # raw stuff
    def visit_raw(self, node):
        if node.get('format') == 'hrstar':
            self.body.append(r'\hrstar')
            raise nodes.SkipNode

    # 'visit_raw' counterpart; required - even if empty
    def depart_raw(self, node):
        pass


class CustomLaTeXWriter(Writer):
    def __init__(self):
        super().__init__()
        self.translator_class = CustomLaTeXTranslator


# markdown directives

class PythonCodeDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'python'     # name must be supported by Pygments
        node['custom_code'] = 'pythoncode' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('pythoncode', PythonCodeDirective)

class PythonSCodeDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'python'      # name must be supported by Pygments
        node['custom_code'] = 'pythonscode' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('pythonscode', PythonSCodeDirective)

class JsonCodeDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'json'     # name must be supported by Pygments
        node['custom_code'] = 'jsoncode' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('jsoncode', JsonCodeDirective)

class JsonSCodeDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'json'      # name must be supported by Pygments
        node['custom_code'] = 'jsonscode' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('jsonscode', JsonSCodeDirective)

class RobotCodeDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'robot'     # name must be supported by Pygments
        node['custom_code'] = 'robotcode' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('robotcode', RobotCodeDirective)

class RobotSCodeDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'robot'      # name must be supported by Pygments
        node['custom_code'] = 'robotscode' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('robotscode', RobotSCodeDirective)

class PythonLogDirective(Directive): # DEPRECATED; successor: ConsoleLogDirective
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'python'    # name must be supported by Pygments
        node['custom_code'] = 'pythonlog' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('pythonlog', PythonLogDirective)

class PythonSLogDirective(Directive): # DEPRECATED; successor: ConsoleSLogDirective
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'python'     # name must be supported by Pygments
        node['custom_code'] = 'pythonslog' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('pythonslog', PythonSLogDirective)

class RobotLogDirective(Directive): # DEPRECATED; successor: ConsoleLogDirective
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'robot'    # name must be supported by Pygments
        node['custom_code'] = 'robotlog' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('robotlog', RobotLogDirective)

class RobotSLogDirective(Directive): # DEPRECATED; successor: ConsoleSLogDirective
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'robot'     # name must be supported by Pygments
        node['custom_code'] = 'robotslog' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('robotslog', RobotSLogDirective)

class ConsoleLogDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'text'       # name must be supported by Pygments
        node['custom_code'] = 'consolelog' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('consolelog', ConsoleLogDirective)

class ConsoleSLogDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'text'        # name must be supported by Pygments
        node['custom_code'] = 'consoleslog' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('consoleslog', ConsoleSLogDirective)

class FileSystemDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'text'       # name must be supported by Pygments
        node['custom_code'] = 'filesystem' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('filesystem', FileSystemDirective)

class FileSSystemDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'text'        # name must be supported by Pygments
        node['custom_code'] = 'filessystem' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('filessystem', FileSSystemDirective)

class AnyContentDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'text'       # name must be supported by Pygments
        node['custom_code'] = 'anycontent' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('anycontent', AnyContentDirective)

class AnySContentDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'text'        # name must be supported by Pygments
        node['custom_code'] = 'anyscontent' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('anyscontent', AnySContentDirective)

class HighlightDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'text'      # name must be supported by Pygments
        node['custom_code'] = 'highlight' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('highlight', HighlightDirective)


# under construction
class SimpleTable(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'text'        # name must be supported by Pygments
        node['custom_code'] = 'simpletable' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('simpletable', SimpleTable)

# >> orig version
# # class HrStarDirective(Directive):
    # # has_content = False
    # # def run(self):
        # # node = nodes.raw('', '', format='html')
        # # node['latex'] = r'\hrstar'
        # # node['html'] = (
            # # '<div class="hrstar">'
            # # '<span class="hrstar-line"></span>'
            # # '<span class="hrstar-star">&#9733;</span>'
            # # '<span class="hrstar-line"></span>'
            # # '</div>'
        # # )
        # # return [node]

class HrStarDirective(Directive):
    has_content = False
    def run(self):
        node = nodes.raw('', '', format='hrstar')
        return [node]

directives.register_directive('hrstar', HrStarDirective)

# markdown roles (inline)

def pcode_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'pcode'
    return [node], []

roles.register_local_role('pcode', pcode_role)

def rcode_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'rcode'
    return [node], []

roles.register_local_role('rcode', rcode_role)

def jcode_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'jcode'
    return [node], []

roles.register_local_role('jcode', jcode_role)

# DEPRECATED; successor: clog_role
def plog_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'plog'
    return [node], []

roles.register_local_role('plog', plog_role)

# DEPRECATED; successor: clog_role
def rlog_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'rlog'
    return [node], []

roles.register_local_role('rlog', rlog_role)

def clog_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'clog'
    return [node], []

roles.register_local_role('clog', clog_role)

def fsystem_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'fsystem'
    return [node], []

roles.register_local_role('fsystem', fsystem_role)

def acontent_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'acontent'
    return [node], []

roles.register_local_role('acontent', acontent_role)

# --------------------------------------------------------------------------------------------------------------

class CustomHTMLTranslator(HTMLTranslator):
    """
Mapping between markdown and HTML w.r.t.:

* Python code listings
* Robot code listings
* Json code listings
* Python log listings
* Robot log listings
    """

    # markdown directives
    def visit_literal_block(self, node):
        """
Description of method ``visit_literal_block``
        """
        if node.get('custom_code') == 'pythoncode':
            code = node.astext()
            highlighted = highlight(code, PythonLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="pythoncode"><code class="pythoncode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'pythonscode':
            # no decrease of font size in HTML (pythonscode is for PDF output only)
            code = node.astext()
            highlighted = highlight(code, PythonLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="pythoncode"><code class="pythoncode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotcode':
            code = node.astext()
            highlighted = highlight(code, CustomRobotFrameworkLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="robotcode"><code class="robotcode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotscode':
            # no decrease of font size in HTML (robotscode is for PDF output only)
            code = node.astext()
            highlighted = highlight(code, CustomRobotFrameworkLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="robotcode"><code class="robotcode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'jsoncode':
            code = node.astext()
            highlighted = highlight(code, CustomJsonLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="jsoncode"><code class="jsoncode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'jsonscode':
            # no decrease of font size in HTML (jsonscode is for PDF output only)
            code = node.astext()
            highlighted = highlight(code, CustomJsonLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="jsoncode"><code class="jsoncode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'pythonlog': # DEPRECATED, mapping: old name -> new name
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'consolelog'
            self.body.append(f'<pre class="consolelog"><code class="consolelog">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'pythonslog': # DEPRECATED, mapping: old name -> new name
            # no decrease of font size in HTML (consoleslog is for PDF output only, here mapped to consolelog)
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'consolelog'
            self.body.append(f'<pre class="consolelog"><code class="consolelog">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotlog': # DEPRECATED, mapping: old name -> new name
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'consolelog'
            self.body.append(f'<pre class="consolelog"><code class="consolelog">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotslog': # DEPRECATED, mapping: old name -> new name
            # no decrease of font size in HTML (consoleslog is for PDF output only, here mapped to consolelog)
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'consolelog'
            self.body.append(f'<pre class="consolelog"><code class="consolelog">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'consolelog':
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'consolelog'
            self.body.append(f'<pre class="consolelog"><code class="consolelog">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'consoleslog':
            # no decrease of font size in HTML (consoleslog is for PDF output only, here mapped to consolelog)
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'consolelog'
            self.body.append(f'<pre class="consolelog"><code class="consolelog">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'filesystem':
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'filesystem'
            self.body.append(f'<pre class="filesystem"><code class="filesystem">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'filessystem':
            # no decrease of font size in HTML (filessystem is for PDF output only, here mapped to filesystem)
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'filesystem'
            self.body.append(f'<pre class="filesystem"><code class="filesystem">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'anycontent':
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'anycontent'
            self.body.append(f'<pre class="anycontent"><code class="anycontent">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'anyscontent':
            # no decrease of font size in HTML (filessystem is for PDF output only, here mapped to anycontent)
            code = node.astext()
            # no syntax highlighting, box background and border still defined by 'anycontent'
            self.body.append(f'<pre class="anycontent"><code class="anycontent">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'highlight':
            code = node.astext()
            self.body.append(f'<pre class="highlight"><code class="highlight">{code}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'simpletable':
            code = table_to_html(node.astext())
            self.body.append(f'<pre class="highlight"><code class="highlight">{code}</code></pre>')
            raise nodes.SkipNode
        else:
            super().visit_literal_block(node)

    # markdown roles
    def visit_literal(self, node):
        code = node.astext()
        if node.get('custom_code') == 'pcode':
            # without syntax highlighting
            self.body.append(f'<code class="pcode">{code}</code>')
            # with syntax highlighting
            # highlighted = highlight(code, PythonLexer(), HtmlFormatter(nowrap=True))
            # self.body.append(f'<code class="pcode">{highlighted}</code>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'rcode':
            # without syntax highlighting
            self.body.append(f'<code class="rcode">{code}</code>')
            # with syntax highlighting
            # highlighted = highlight(code, CustomRobotFrameworkLexer()(), HtmlFormatter(nowrap=True))
            # self.body.append(f'<code class="rcode">{highlighted}</code>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'jcode':
            # without syntax highlighting
            self.body.append(f'<code class="jcode">{code}</code>')
            # with syntax highlighting
            # highlighted = highlight(code, CustomJsonLexer(), HtmlFormatter(nowrap=True))
            # self.body.append(f'<code class="jcode">{highlighted}</code>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'plog': # DEPRECATED, mapping: old name -> new name
            self.body.append(f'<code class="consolelog">{code}</code>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'rlog': # DEPRECATED, mapping: old name -> new name
            self.body.append(f'<code class="consolelog">{code}</code>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'clog':
            self.body.append(f'<code class="consolelog">{code}</code>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'fsystem':
            self.body.append(f'<code class="filesystem">{code}</code>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'acontent':
            self.body.append(f'<code class="anycontent">{code}</code>')
            raise nodes.SkipNode
        else:
            super().visit_literal(node)

    # raw stuff
    def visit_raw(self, node):
        if node.get('format') == 'hrstar':
            self.body.append(
                '<div class="hrstar">'
                '<span class="hrstar-line"></span>'
                '<span class="hrstar-star">&#9733;</span>'
                '<span class="hrstar-line"></span>'
                '</div>'
            )
            raise nodes.SkipNode

    # 'visit_raw' counterpart; required - even if empty
    def depart_raw(self, node):
        pass


class CustomHTMLWriter(htmlWriter):
    """
Description of class ``CustomHTMLWriter``
    """
    def __init__(self):
        super().__init__()
        self.translator_class = CustomHTMLTranslator


