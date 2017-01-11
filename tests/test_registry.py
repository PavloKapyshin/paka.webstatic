import os
import unittest

from testutils import TEST_FILES_DIR


class RegistryTest(unittest.TestCase):

    def setUp(self):
        from paka.webstatic.registry import Registry
        self.registry_factory = Registry
        self.url_path = "/static/"
        self.fs_path = "/var/static/"

    def mkreg(self, domain=None, **types):
        return self.registry_factory(
            url_path=self.url_path,
            fs_path=self.fs_path,
            domain=domain,
            types=types,
        )

    def test_manifest_fs_path(self):
        reg = self.registry_factory(
            url_path=self.url_path,
            fs_path=TEST_FILES_DIR,
            types={},
        )
        reg.load_manifest()
        fs_path = os.path.abspath(
            os.path.join(TEST_FILES_DIR, "manifest")
        )
        self.assertEqual(reg.manifest.fs_path, fs_path)

    def test_manifest_load_from_fs_path(self):
        reg = self.registry_factory(
            url_path=self.url_path,
            fs_path=TEST_FILES_DIR,
            types={},
        )
        reg.load_manifest()
        self.assertEqual(reg.manifest["first/path"], "firsth")
        self.assertEqual(reg.manifest["second/path"], "second")

    def test_fs_paths(self):
        from paka.webstatic.registry import FileRType
        reg = self.mkreg(
            f=FileRType(url_path="f", fs_path="z", add_hash=False),
        )
        self.assertEqual(
            list(reg.f("one.file", "two.files").fs_paths),
            ["/var/static/z/one.file", "/var/static/z/two.files"]
        )

    def test_url_paths(self):
        from paka.webstatic.registry import FileRType
        reg = self.mkreg(
            f=FileRType(url_path="f", fs_path="z", add_hash=False),
        )
        self.assertEqual(
            list(reg.f("one.file", "two.files").url_paths),
            ["/static/f/one.file", "/static/f/two.files"]
        )

    def test_favicon_rtype(self):
        from paka.webstatic.registry import FaviconRType
        reg = self.mkreg(favicon=FaviconRType(fs_path="i"))
        self.assertEqual(reg.favicon().fs_path, "/var/static/i/favicon.ico")
        self.assertEqual(reg.favicon().url_path, "/favicon.ico")
        self.assertRaises(NotImplementedError, lambda: reg.favicon().html)

    def test_favicon_rtype_with_custom_ext(self):
        from paka.webstatic.registry import FaviconRType
        reg = self.mkreg(favicon=FaviconRType(fs_path="i", ext="png"))
        self.assertEqual(reg.favicon().fs_path, "/var/static/i/favicon.png")
        self.assertEqual(reg.favicon().url_path, "/favicon.png")
        self.assertRaises(NotImplementedError, lambda: reg.favicon().html)

        reg = self.mkreg(favicon=FaviconRType(fs_path="i"))
        self.assertEqual(reg.favicon(ext="png").fs_path, "/var/static/i/favicon.png")
        self.assertEqual(reg.favicon(ext="png").url_path, "/favicon.png")
        self.assertRaises(NotImplementedError, lambda: reg.favicon().html)

    def test_file_rtype(self):
        from paka.webstatic.registry import FileRType
        reg = self.mkreg(
            i=FileRType(url_path="images", fs_path="i", add_hash=False),
        )
        self.assertEqual(reg.i("test.png").fs_path, "/var/static/i/test.png")
        self.assertEqual(reg.i("test.png").url_path, "/static/images/test.png")
        self.assertRaises(NotImplementedError, lambda: reg.i("test.png").html)

    def test_file_rtype_with_manifest(self):
        from paka.webstatic.registry import FileRType
        reg = self.mkreg(
            i=FileRType(url_path="images", fs_path="i", add_hash=True),
        )
        reg.load_manifest(data={
            "/var/static/i/test2.png": (
                "onetwothreefourfivesixseveneightenoughimtired"
            ),
        })
        self.assertEqual(reg.i("test.png").fs_path, "/var/static/i/test.png")
        self.assertEqual(reg.i("test.png").url_path, "/static/images/test.png")
        self.assertRaises(NotImplementedError, lambda: reg.i("test.png").html)
        self.assertEqual(reg.i("test2.png").fs_path, "/var/static/i/test2.onetwo.png")
        self.assertEqual(reg.i("test2.png").url_path, "/static/images/test2.onetwo.png")
        self.assertRaises(NotImplementedError, lambda: reg.i("test2.png").html)
        self.assertEqual(
            reg.i("test2.png", add_hash=False).fs_path,
            "/var/static/i/test2.png"
        )
        self.assertEqual(
            reg.i("test2.png", add_hash=False).url_path,
            "/static/images/test2.png"
        )

    def test_file_rtype_with_manifest_and_disabled_hashes(self):
        from paka.webstatic.registry import FileRType
        reg = self.mkreg(
            i=FileRType(url_path="img", fs_path="icons", add_hash=False),
        )
        fs_path = "/var/static/icons/test.png"
        reg.load_manifest(data={fs_path: "onetwotheefourfivesixseven"})
        self.assertEqual(reg.i("test.png").fs_path, fs_path)
        self.assertEqual(reg.i("test.png").url_path, "/static/img/test.png")
        self.assertRaises(NotImplementedError, lambda: reg.i("test.png").html)

    def test_css_rtype(self):
        from paka.webstatic.registry import CSSRType
        reg = self.mkreg(
            css=CSSRType(url_path="cssroot", fs_path="cssroot", add_hash=False),
        )
        self.assertEqual(
            reg.css("style<s.css").fs_path,
            "/var/static/cssroot/style<s.css"
        )
        self.assertEqual(
            reg.css("style<s.css").url_path,
            "/static/cssroot/style<s.css"
        )
        self.assertEqual(
            reg.css("style<s.css").html,
            """<link rel="stylesheet" href="/static/cssroot/style&lt;s.css">"""
        )
        self.assertEqual(
            reg.css("style<s.css", media="print").html,
            (
                """<link rel="stylesheet" href="/static/cssroot/"""
                """style&lt;s.css" media="print">"""
            )
        )

    def test_css_rtype_with_manifest(self):
        from paka.webstatic.registry import CSSRType
        reg = self.mkreg(
            css=CSSRType(url_path="cssroot", fs_path="cssroot", add_hash=True),
            domain="example.com"
        )
        reg.load_manifest(data={
            "/var/static/cssroot/style<s.css": "deadbeefbadf00d",
        })
        self.assertEqual(
            reg.css("style<s.css").fs_path,
            "/var/static/cssroot/style<s.deadbe.css"
        )
        self.assertEqual(
            reg.css("style<s.css").url_path,
            "/static/cssroot/style<s.deadbe.css"
        )
        self.assertEqual(
            reg.css("style<s.css").url,
            "//example.com/static/cssroot/style<s.deadbe.css"
        )
        self.assertEqual(
            reg.css("style<s.css").html,
            (
                """<link rel="stylesheet" href="/static/"""
                """cssroot/style&lt;s.deadbe.css">"""
            )
        )
        self.assertEqual(
            reg.css("style<s.css", absolute_url=True).html,
            (
                """<link rel="stylesheet" href="//example.com/static/"""
                """cssroot/style&lt;s.deadbe.css">"""
            )
        )
        self.assertEqual(
            reg.css("style<s.css", media="print").html,
            (
                """<link rel="stylesheet" href="/static/"""
                """cssroot/style&lt;s.deadbe.css" media="print">"""
            )
        )
        self.assertEqual(
            reg.css("style<s.css", add_hash=False).fs_path,
            "/var/static/cssroot/style<s.css"
        )
        self.assertEqual(
            reg.css("style<s.css", add_hash=False).url_path,
            "/static/cssroot/style<s.css"
        )

    def test_js_rtype(self):
        from paka.webstatic.registry import JSRType
        reg = self.mkreg(
            js=JSRType(url_path="j", fs_path="scripts", add_hash=False),
            domain="example.com"
        )
        self.assertEqual(
            reg.js("script>s.js").fs_path,
            "/var/static/scripts/script>s.js"
        )
        self.assertEqual(
            reg.js("script>s.js").url_path,
            "/static/j/script>s.js"
        )
        self.assertEqual(
            reg.js("script>s.js").url,
            "//example.com/static/j/script>s.js"
        )
        self.assertEqual(
            reg.js("script>s.js").html,
            """<script src="/static/j/script&gt;s.js"></script>"""
        )
        self.assertEqual(
            reg.js("script>s.js", absolute_url=True).html,
            (
                """<script src="//example.com/static/j/"""
                """script&gt;s.js"></script>"""
            )
        )
        self.assertEqual(
            reg.js("script>s.js", defer=True).html,
            """<script src="/static/j/script&gt;s.js" defer></script>"""
        )
        self.assertEqual(
            reg.js("script>s.js", async=True).html,
            """<script src="/static/j/script&gt;s.js" async></script>"""
        )

    def test_js_rtype_with_manifest(self):
        from paka.webstatic.registry import JSRType
        reg = self.mkreg(
            js=JSRType(url_path="j", fs_path="scripts", add_hash=True),
            domain="example.com"
        )
        reg.load_manifest(data={
            "/var/static/scripts/script>s.js": "deadbeefbadf00d",
        })
        self.assertEqual(
            reg.js("script>s.js").fs_path,
            "/var/static/scripts/script>s.deadbe.js"
        )
        self.assertEqual(
            reg.js("script>s.js").url_path,
            "/static/j/script>s.deadbe.js"
        )
        self.assertEqual(
            reg.js("script>s.js").url,
            "//example.com/static/j/script>s.deadbe.js"
        )
        self.assertEqual(
            reg.js("script>s.js").html,
            """<script src="/static/j/script&gt;s.deadbe.js"></script>"""
        )
        self.assertEqual(
            reg.js("script>s.js", absolute_url=True).html,
            (
                """<script src="//example.com/static/j"""
                """/script&gt;s.deadbe.js"></script>"""
            )
        )
        self.assertEqual(
            reg.js("script>s.js", defer=True).html,
            """<script src="/static/j/script&gt;s.deadbe.js" defer></script>"""
        )
        self.assertEqual(
            reg.js("script>s.js", async=True).html,
            """<script src="/static/j/script&gt;s.deadbe.js" async></script>"""
        )
        self.assertEqual(
            reg.js("script>s.js", add_hash=False).fs_path,
            "/var/static/scripts/script>s.js"
        )
        self.assertEqual(
            reg.js("script>s.js", add_hash=False).url_path,
            "/static/j/script>s.js"
        )

    def test_some_rtype_roots(self):
        from paka.webstatic.registry import FileRType
        reg = self.mkreg(v=FileRType(url_path="uv", fs_path="fv", add_hash=False))
        self.assertEqual(reg.v("").fs_path, "/var/static/fv")
        self.assertEqual(reg.v("").url_path, "/static/uv/")

    def test_some_rtype_domain(self):
        from paka.webstatic.registry import FileRType
        reg = self.mkreg(
            v=FileRType(url_path="uv", fs_path="fv", add_hash=False)
        )
        self.assertRaises(NotImplementedError, lambda: reg.v("").url)
        self.assertEqual(reg.v("").url_path, "/static/uv/")
        self.assertEqual(reg.v("").fs_path, "/var/static/fv")
        reg = self.mkreg(
            v=FileRType(url_path="uv", fs_path="fv", add_hash=False),
            domain="example.com"
        )
        self.assertEqual(reg.v("").url, "//example.com/static/uv/")
        self.assertEqual(
            list(reg.v("").urls),
            ["//example.com/static/uv/"]
        )
        self.assertEqual(reg.v("").url_path, "/static/uv/")
        self.assertEqual(reg.v("").fs_path, "/var/static/fv")
