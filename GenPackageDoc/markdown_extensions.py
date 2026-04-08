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
# 07.04.2026
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
from pygments.lexer import RegexLexer
from pygments.lexers import PythonLexer
from pygments.lexers import JsonLexer
from pygments.lexers import RobotFrameworkLexer

from pygments.formatters import HtmlFormatter

from pygments.token import Keyword, Name, String, Comment, Number, Punctuation, Operator, Text

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


# TODO: CustomRobotFrameworkLexer (because of RobotFramework AIO syntax extensions)


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
        else:
            super().visit_literal_block(node)
    # markdown roles
    def visit_literal(self, node):
        # code listings
        if node.get('custom_code') == 'pcode':
            self.body.append('\\pcode{' + node.astext() + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'rcode':
            self.body.append('\\rcode{' + node.astext() + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'jcode':
            self.body.append('\\jcode{' + node.astext() + '}')
            raise nodes.SkipNode
        # log listings and file system paths (new)
        elif node.get('custom_code') == 'clog':
            self.body.append('\\clog{' + node.astext() + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'fsystem':
            self.body.append('\\fsystem{' + node.astext() + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'acontent':
            self.body.append('\\acontent{' + node.astext() + '}')
            raise nodes.SkipNode
        # log listings and file system paths
        elif node.get('custom_code') == 'plog': # DEPRECATED, mapping: old name -> new name
            self.body.append('\\clog{' + node.astext() + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'rlog': # DEPRECATED, mapping: old name -> new name
            self.body.append('\\clog{' + node.astext() + '}')
            raise nodes.SkipNode
        else:
            super().visit_literal(node)

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
            highlighted = highlight(code, RobotFrameworkLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="robotcode"><code class="robotcode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotscode':
            # no decrease of font size in HTML (robotscode is for PDF output only)
            code = node.astext()
            highlighted = highlight(code, RobotFrameworkLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
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
            # highlighted = highlight(code, RobotFrameworkLexer()(), HtmlFormatter(nowrap=True))
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


class CustomHTMLWriter(htmlWriter):
    """
Description of class ``CustomHTMLWriter``
    """
    def __init__(self):
        super().__init__()
        self.translator_class = CustomHTMLTranslator


