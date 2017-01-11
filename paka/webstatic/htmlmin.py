from __future__ import unicode_literals

import io
import re
import sys


_HTMLMIN_RE = re.compile(r">[ \t\n\r\f\v]+<")

_PRE_RE = re.compile(r"(<pre[^>]*?>.*?</pre>)", re.IGNORECASE | re.DOTALL)
_PRE_START = "<pre"


def _get_fragments(input_):
    for fragment in _PRE_RE.split(input_):
        minify = not fragment.startswith(_PRE_START)
        yield fragment, minify


def htmlmin(input_):
    buf = io.StringIO()
    for fragment, minify in _get_fragments(input_.strip()):
        if minify:
            fragment = _HTMLMIN_RE.sub("><", fragment).strip()
        buf.write(fragment)
    return buf.getvalue()


def main():
    sys.stdout.write(htmlmin(sys.stdin.read()))


if __name__ == "__main__":
    main()

