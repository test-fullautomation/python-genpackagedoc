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
# 20.03.2026
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing markdown extensions:
Markdown directives and markdown roles mapped to LaTeX code listings and console listings.
"""
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.parsers.rst import roles
from docutils.writers.latex2e import Writer
from docutils.writers.latex2e import LaTeXTranslator

from docutils.writers.html5_polyglot import Writer as htmlWriter
from docutils.writers.html5_polyglot import HTMLTranslator

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers import RstLexer # ??
from pygments.lexers import JsonLexer

from pygments.formatters import HtmlFormatter

# # #  ? from pygments.lexer import bygroups, include, RegexLexer, words
from pygments.token import Keyword

## from pygments.lexer import RegexLexer, bygroups, include, default, this, using, do_insertions
from pygments.token import Keyword, Name, String, Comment, Punctuation, Text, Number, Operator


import re


from pygments.lexer import RegexLexer
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
            (r'//.*$', Comment.Single),                # Kommentar
            (r'"(\\\\|\\"|[^"])*"', String),           # Standard-String
            (r'\d+\.\d+', Number.Float),               # Float
            (r'\d+', Number.Integer),                  # Integer
            (r'[{}\[\],:]', Punctuation),              # JSON-Punctuation
            (r'\s+', Text),                            # Whitespace
            (r'.', Text),                              # Sonstiges
        ],
    }

# # # class CustomJsonLexer(JsonLexer):
    # # # name = 'CustomJson'
    # # # aliases = ['customjson']
    # # # filenames = ['*.json', '*.jsonp']

    # # # EXTRA_KEYWORDS = ('[import]', '<<', '>>', 'global')

    # # # tokens = {
        # # # 'root': [
            # # # # ${...}
            # # # (r'\$\{[^}]+\}', Name.Variable),
            # # # # ['...']
            # # # (r"\['[^']+'\]", Name.Attribute),
            # # # # "[import]"
            # # # (r'"\[import\]"', Keyword.Reserved),
            # # # # << oder >>
            # # # (r'<<|>>', Keyword.Declaration),
            # # # # // Kommentar bis Zeilenende
            # # # (r'//.*$', Comment.Single),
            # # # # Standard-JSON-Tokenisierung
            # # # include('json'),
        # # # ],
        # # # 'json': JsonLexer.tokens['root'],
    # # # }

    # # # def get_tokens_unprocessed(self, text):
        # # # # Nutze die eigene Regex-Logik für die neuen Elemente
        # # # for index, token, value in RegexLexer.get_tokens_unprocessed(self, text):
            # # # yield index, token, value




class CustomLaTeXTranslator(LaTeXTranslator):
    """
Mapping between markdown and LaTeX w.r.t.:

* Python code listings
* Robot code listings
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
        elif node.get('custom_code') == 'jsoncode':
            # # jsoncode currently still mapped to pythoncode !!!
            self.body.append('\\begin{pythoncode}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{pythoncode}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotcode':
            self.body.append('\\begin{robotcode}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{robotcode}\n')
            raise nodes.SkipNode
        # log listings and file system paths
        elif node.get('custom_code') == 'pythonlog':
            self.body.append('\\begin{pythonlog}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{pythonlog}\n')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'robotlog':
            self.body.append('\\begin{robotlog}\n')
            self.body.append(node.astext())
            self.body.append('\n\\end{robotlog}\n')
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
        # log listings and file system paths
        elif node.get('custom_code') == 'plog':
            self.body.append('\\plog{' + node.astext() + '}')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'rlog':
            self.body.append('\\rlog{' + node.astext() + '}')
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


class JsonCodeDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'json'     # name must be supported by Pygments
        node['custom_code'] = 'jsoncode' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('jsoncode', JsonCodeDirective)


class RobotCodeDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'python'    # name must be supported by Pygments
        node['custom_code'] = 'robotcode' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('robotcode', RobotCodeDirective)

class PythonLogDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'python'    # name must be supported by Pygments
        node['custom_code'] = 'pythonlog' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('pythonlog', PythonCodeDirective)

class RobotLogDirective(Directive):
    has_content = True
    def run(self):
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code)
        node['language']    = 'python'   # name must be supported by Pygments
        node['custom_code'] = 'robotlog' # custom environments realized by additional attribute inside node
        return [node]

directives.register_directive('robotlog', RobotCodeDirective)

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

def plog_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'plog'
    return [node], []

roles.register_local_role('plog', plog_role)

def rlog_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(text, text)
    node['custom_code'] = 'rlog'
    return [node], []

roles.register_local_role('rlog', rlog_role)

# --------------------------------------------------------------------------------------------------------------

class CustomHTMLTranslator(HTMLTranslator):
    """
Description of class ``CustomHTMLTranslator``
    """
    def visit_literal_block(self, node):
        """
Description of method ``visit_literal_block``
        """
        if node.get('custom_code') == 'pythoncode':
            code = node.astext()
            highlighted = highlight(code, PythonLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="pythoncode"><code class="pythoncode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        elif node.get('custom_code') == 'jsoncode':
            code = node.astext()
            highlighted = highlight(code, CustomJsonLexer(), HtmlFormatter(full=True, linenos=True, nowrap=True))
            self.body.append(f'<pre class="jsoncode"><code class="jsoncode">{highlighted}</code></pre>')
            raise nodes.SkipNode
        else:
            super().visit_literal_block(node)

class CustomHTMLWriter(htmlWriter):
    """
Description of class ``CustomHTMLWriter``
    """
    def __init__(self):
        super().__init__()
        self.translator_class = CustomHTMLTranslator


