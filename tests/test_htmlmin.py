# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import contextlib


class HTMLMinTest(unittest.TestCase):
    maxDiff = None

    if not hasattr(unittest.TestCase, "subTest"):
        @contextlib.contextmanager
        def subTest(self, **kwargs):
            yield

    def setUp(self):
        from paka.webstatic.htmlmin import htmlmin
        self.func = htmlmin

    def check(self, input_, expected):
        self.assertEqual(self.func(input_), expected)

    def check_inputs(self, inputs, expected):
        for input_ in inputs:
            with self.subTest(input_=input_):
                self.check(input_, expected)

    def test_empty(self):
        self.check("", "")

    def test_whitespace(self):
        self.check("  ", "")
        self.check(" \n ", "")

    def test_list(self):
        self.check(
            """<ol some="thing"> <li>Item 1</li><li>Item 2</li>
<li class="other"> Item 3
</li>
 </ol>
""",
            (
                '<ol some="thing"><li>Item 1</li><li>Item 2</li>'
                '<li class="other"> Item 3\n</li></ol>'))

    def test_single_pre(self):
        expected = "<body><pre>\nHello!\n</pre></body>"
        inputs = (
            """<body>
<pre>
Hello!
</pre>
</body>""",
            """<body><pre>
Hello!
</pre></body>""",
            """<body> <pre>
Hello!
</pre> </body>""")
        self.check_inputs(inputs, expected)

    def test_multiple_pres(self):
        expected = (
            "<body><pre>\n1 2\n3\n</pre><p>tst "
            "tst</p><pre>4\n4\n5</pre></body>")
        inputs = (
            """<body>
    <pre>
1 2
3
</pre>
<p>tst tst</p>
<pre>4
4
5</pre>
   </body>""",
            """<body>
<pre>
1 2
3
</pre><p>tst tst</p> <pre>4
4
5</pre>       </body>

""")
        self.check_inputs(inputs, expected)

    def test_code_in_pre(self):
        expected = (
            '<pre><code class="language-whitespace">    \n \n  \n     '
            '</code></pre><p><em>More</em> <code>code</code>?</p><pre>'
            '<code> something different\n</code></pre>')
        inputs = (
            """<pre><code class="language-whitespace">    
 
  
     </code></pre><p><em>More</em> <code>code</code>?</p><pre><code> something different
</code></pre>""", )
        self.check_inputs(inputs, expected)

    def test_tags_in_pre(self):
        expected = input_ = """<body><pre><code class="language-pycon"><span class="co-go">Python 3 (build, date, time) </span>
<span class="co-go">[compiler version] on os</span>
<span class="co-go">Type &quot;help&quot;, &quot;copyright&quot;, &quot;credits&quot; or &quot;license&quot; for more information.</span>
<span class="hll"><span class="co-gp">&gt;&gt;&gt; </span><span class="co-n">s</span> <span class="co-o">=</span> <span class="co-s">&quot;</span>
</span>  File <span class="co-nb">&quot;&lt;stdin&gt;&quot;</span>, line <span class="co-m">1</span>
    <span class="co-n">s</span> <span class="co-o">=</span> <span class="co-s">&quot;</span>
        <span class="co-o">^</span>
<span class="co-gr">SyntaxError</span>: <span class="co-n">EOL while scanning string literal</span>
<span class="co-gp">&gt;&gt;&gt; </span><span class="co-n">s</span> <span class="co-o">=</span> <span class="co-s">&quot; </span><span class="co-se">\</span>
<span class="co-gp">... </span><span class="co-s">sdfsdf&quot;</span>
<span class="co-gp">&gt;&gt;&gt; </span><span class="co-n">s</span>
<span class="hll"><span class="co-go">&#39; sdfsdf&#39;</span>
</span><span class="co-gp">&gt;&gt;&gt; </span><span class="co-nb">print</span><span class="co-p">(</span><span class="co-n">S</span><span class="co-p">)</span>
<span class="co-gt">Traceback (most recent call last):</span>
  File <span class="co-nb">&quot;&lt;stdin&gt;&quot;</span>, line <span class="co-m">1</span>, in <span class="co-n">&lt;module&gt;</span>
<span class="co-gr">NameError</span>: <span class="co-n">name &#39;S&#39; is not defined</span>
<span class="co-gp">&gt;&gt;&gt; </span><span class="co-nb">print</span><span class="co-p">(</span><span class="co-n">s</span><span class="co-p">)</span>
<span class="co-go"> sdfsdf</span>
<span class="co-gp">&gt;&gt;&gt; </span><span class="co-nb">vars</span><span class="co-p">()</span>
<span class="co-go">{&#39;__spec__&#39;: None, &#39;__builtins__&#39;: &lt;module &#39;builtins&#39; (built-in)&gt;, &#39;__name__&#39;: &#39;__main__&#39;, &#39;s&#39;: &#39; sdfsdf&#39;, &#39;__package__&#39;: None, &#39;__doc__&#39;: None, &#39;__loader__&#39;: &lt;class &#39;_frozen_importlib.BuiltinImporter&#39;&gt;}</span>
</code></pre></body>"""
        self.check(input_, expected)
        self.check(input_ * 2, expected * 2)
