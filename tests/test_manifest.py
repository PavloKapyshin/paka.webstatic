import io
import unittest


class ManifestTest(unittest.TestCase):

    def setUp(self):
        from paka.webstatic.manifest import Manifest
        self.manifest_factory = Manifest
        self.fs_path = "/root/manifest"
        self.hash_length = 3

    def mkmanifest(self):
        return self.manifest_factory(
            self.fs_path,
            hash_length=self.hash_length,
        )

    def test_get_set_item(self):
        manifest = self.mkmanifest()
        manifest["some/path.obj"] = "123" * 10
        self.assertEqual(manifest["/root/some/path.obj"], "123")

    def test_load(self):
        buf = io.BytesIO(b"abc  def/obj\nghi  jkl/mn\n\n  \n")
        manifest = self.mkmanifest()
        manifest.load(buf)
        self.assertEqual(manifest["def/obj"], "abc")
        self.assertEqual(manifest["/root/def/obj"], "abc")
        self.assertEqual(manifest["jkl/mn"], "ghi")
        self.assertEqual(manifest["/root/jkl/mn"], "ghi")

    def test_dump(self):
        buf = io.BytesIO()
        manifest = self.mkmanifest()
        one = "12345678903232323323232399292382378126128368291369"
        two = "234892349023840234728346753469863986234782693423649322242"
        manifest["one"] = one
        manifest["two"] = two
        self.assertEqual(manifest["one"], "123")
        self.assertEqual(manifest["two"], "234")
        manifest.dump(buf)
        result = (
            b"12345678903232323323232399292382378126128368291369  one\n"
            b"234892349023840234728346753469863986234782693423649322242  two"
        )
        self.assertEqual(buf.getvalue(), result)

    def test_loads(self):
        manifest = self.mkmanifest()
        manifest.loads("abc  def/obj")
        self.assertEqual(manifest["/root/def/obj"], "abc")
        self.assertEqual(manifest["def/obj"], "abc")
        self.assertRaises(KeyError, lambda: manifest["/def/obj"])

    def test_dumps(self):
        manifest = self.mkmanifest()
        manifest["/root/def"] = "abc"
        self.assertEqual(manifest.dumps(), "abc  def")
