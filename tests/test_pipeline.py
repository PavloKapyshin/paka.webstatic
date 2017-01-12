import os
import glob
import shutil
import tempfile
import unittest

from testutils import TEST_FILES_DIR


class PipelineTest(unittest.TestCase):

    def setUp(self):
        from paka.webstatic import pipeline
        self.p = pipeline
        self._to_remove = set()

    def tearDown(self):
        for path in glob.glob(self.pth("*/out*.css")):
            self._to_remove.add(path)
        for path in glob.glob(self.pth("*/out-*")):
            self._to_remove.add(path)
        for path in self._to_remove:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    def tmp(self):
        _handle, path = tempfile.mkstemp(dir=self.pth())
        self._to_remove.add(path)
        return path

    def pth(self, *args):
        return os.path.abspath(
            os.path.join(TEST_FILES_DIR, "pipeline", *args)
        )

    def test_noop(self):
        in_path = self.pth("noop/in.css")
        out_path = self.pth("noop/out.css")
        self.assertFalse(os.path.exists(out_path))
        output = self.p.run((
            self.p.InputItem(in_path),
            self.p.Output(out_path),
        ))
        self.assertEqual(output.path, out_path)
        self.assertTrue(os.path.exists(out_path))
        with open(in_path, "rb") as f:
            in_b = f.read()
        with open(out_path, "rb") as f:
            out_b = f.read()
        self.assertEqual(out_b, in_b)

    def test_noop_makedirs(self):
        in_path = self.pth("noop/in.css")
        out_path = self.pth("noop/out-some/out.css")
        self.assertFalse(os.path.exists(out_path))
        self.assertFalse(os.path.exists(os.path.dirname(out_path)))
        output = self.p.run((
            self.p.InputItem(in_path),
            self.p.Output(out_path, makedirs=True),
        ))
        self.assertEqual(output.path, out_path)
        self.assertTrue(os.path.exists(out_path))
        with open(in_path, "rb") as f:
            in_b = f.read()
        with open(out_path, "rb") as f:
            out_b = f.read()
        self.assertEqual(out_b, in_b)

    def test_noop_makedirs_existing_dir(self):
        in_path = self.pth("noop/in.css")
        out_path1 = self.pth("noop/out-some/out1.css")
        out_path2 = self.pth("noop/out-some/out2.css")
        self.assertFalse(os.path.exists(out_path1))
        self.assertFalse(os.path.exists(out_path2))
        self.assertFalse(os.path.exists(os.path.dirname(out_path1)))
        self.assertFalse(os.path.exists(os.path.dirname(out_path2)))

        def check(out_path):
            output = self.p.run((
                self.p.InputItem(in_path),
                self.p.Output(out_path, makedirs=True)))
            self.assertEqual(output.path, out_path)
            self.assertTrue(os.path.exists(out_path))
            with open(in_path, "rb") as f:
                in_b = f.read()
            with open(out_path, "rb") as f:
                out_b = f.read()
            self.assertEqual(out_b, in_b)

        check(out_path1)
        check(out_path2)

    def test_noop_with_manifest(self):
        from paka.webstatic.manifest import Manifest
        manifest_path = self.tmp()
        manifest = Manifest(manifest_path, hash_length=10)
        in_path = self.pth("noop_with_manifest/in.css")
        out_path = self.pth("noop_with_manifest/out.css")
        actual_out_path = self.pth("noop_with_manifest/out.aac6085ead.css")
        self.assertFalse(os.path.exists(out_path))
        self.assertFalse(os.path.exists(actual_out_path))
        output = self.p.run((
            self.p.InputItem(in_path),
            self.p.Output(out_path, manifest=manifest),
        ))
        self.assertEqual(output.path, actual_out_path)
        self.assertFalse(os.path.exists(out_path))
        self.assertTrue(os.path.exists(actual_out_path))
        with open(in_path, "rb") as f:
            in_b = f.read()
        with open(actual_out_path, "rb") as f:
            out_b = f.read()
        self.assertEqual(out_b, in_b)
        self.assertEqual(manifest[out_path], "aac6085ead")
        with open(manifest_path, "rb") as f:
            manifest_s = f.read().decode("utf-8")
        self.assertEqual(
            manifest_s,
            (
                """aac6085eadc857908214c435b0f02d09782f222f  """
                """noop_with_manifest/out.css"""
            )
        )

    def test_noop_makedirs_with_manifest(self):
        from paka.webstatic.manifest import Manifest
        manifest_path = self.tmp()
        manifest = Manifest(manifest_path, hash_length=10)
        in_path = self.pth("noop_with_manifest/in.css")
        out_path = self.pth("noop_with_manifest/out-some/out.css")
        actual_out_path = self.pth(
            "noop_with_manifest/out-some/out.aac6085ead.css")
        self.assertFalse(os.path.exists(out_path))
        self.assertFalse(os.path.exists(os.path.dirname(out_path)))
        self.assertFalse(os.path.exists(actual_out_path))
        output = self.p.run((
            self.p.InputItem(in_path),
            self.p.Output(out_path, manifest=manifest, makedirs=True)))
        self.assertEqual(output.path, actual_out_path)
        self.assertFalse(os.path.exists(out_path))
        self.assertTrue(os.path.exists(actual_out_path))
        with open(in_path, "rb") as f:
            in_b = f.read()
        with open(actual_out_path, "rb") as f:
            out_b = f.read()
        self.assertEqual(out_b, in_b)
        self.assertEqual(manifest[out_path], "aac6085ead")
        with open(manifest_path, "rb") as f:
            manifest_s = f.read().decode("utf-8")
        self.assertEqual(
            manifest_s,
            (
                """aac6085eadc857908214c435b0f02d09782f222f  """
                """noop_with_manifest/out-some/out.css"""))

    def test_manifest_should_remove_old_file(self):
        from paka.webstatic.manifest import Manifest
        manifest_path = self.tmp()
        manifest = Manifest(manifest_path, hash_length=10)
        in_path = self.pth("manifest_should_remove_old_file/in-1.css")
        out_path = self.pth("manifest_should_remove_old_file/out.css")
        actual_out_path = self.pth(
            "manifest_should_remove_old_file/out.aac6085ead.css"
        )
        self.assertFalse(os.path.exists(out_path))
        self.assertFalse(os.path.exists(actual_out_path))
        output = self.p.run((
            self.p.InputItem(in_path),
            self.p.Output(out_path, manifest=manifest),
        ))
        self.assertEqual(output.path, actual_out_path)
        self.assertFalse(os.path.exists(out_path))
        self.assertTrue(os.path.exists(actual_out_path))
        new_in_path = self.pth("manifest_should_remove_old_file/in-2.css")
        new_actual_out_path = self.pth(
            "manifest_should_remove_old_file/out.9020aa4b98.css"
        )
        self.assertFalse(os.path.exists(new_actual_out_path))
        output = self.p.run((
            self.p.InputItem(new_in_path),
            self.p.Output(out_path, manifest=manifest),
        ))
        self.assertEqual(output.path, new_actual_out_path)
        self.assertFalse(os.path.exists(out_path))
        self.assertTrue(os.path.exists(new_actual_out_path))
        self.assertFalse(os.path.exists(actual_out_path))

    def test_concat(self):
        in_path_1 = self.pth("concat/in-1.css")
        in_path_2 = self.pth("concat/in-2.css")
        out_path = self.pth("concat/out.css")
        self.assertFalse(os.path.exists(out_path))
        output = self.p.run((
            self.p.Input([in_path_1, in_path_2]),
            self.p.Concat(),
            self.p.Output(out_path),
        ))
        self.assertEqual(output.path, out_path)
        self.assertTrue(os.path.exists(out_path))
        in_b = b""
        with open(in_path_1, "rb") as f:
            in_b += f.read()
        with open(in_path_2, "rb") as f:
            in_b += f.read()
        with open(out_path, "rb") as f:
            out_b = f.read()
        self.assertEqual(out_b, in_b)

    def test_cssmin(self):
        output = self.p.run((
            self.p.InputItem(
                path=None,
                data="Hello,cssmin\n* {margin: 0 0 0 0; padding: 0;}",
            ),
            self.p.CSSMin(),
        ))
        self.assertEqual(
            output.data,
            "Hello,cssmin *{margin:0;padding:0}",
        )

    def test_jsmin(self):
        output = self.p.run((
            self.p.InputItem(
                path=None,
                data="""/* some comment */  function () {
                    return 1;
                }
                """,
            ),
            self.p.JSMin(),
        ))
        self.assertEqual(
            output.data,
            "function(){return 1;}",
        )

    def test_replace(self):
        output = self.p.run((
            self.p.InputItem(
                path=None,
                data=(
                    "Do SOMETHING with this THING!\n"
                    "Really, do something with this thing!"
                ),
            ),
            self.p.Replace({
                "SOMETHING": "42",
            }),
        ))
        self.assertEqual(
            output.data,
            (
                "Do 42 with this THING!\n"
                "Really, do something with this thing!"
            ),
        )
