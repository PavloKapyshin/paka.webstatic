import os
import hashlib
import argparse


SEP = "  "


class Manifest(object):

    def __init__(self, fs_path, hash_length=6, encoding="utf-8"):
        self.fs_path = os.path.abspath(fs_path)
        self._fs_root = os.path.dirname(self.fs_path)
        self._hash_length = hash_length
        self._encoding = encoding
        self._data = {}

    def _get_path(self, name):
        return os.path.relpath(
            os.path.join(self._fs_root, name),
            self._fs_root
        )

    def __getitem__(self, name):
        return self._data[self._get_path(name)][:self._hash_length]

    def __setitem__(self, name, value):
        self._data[self._get_path(name)] = value

    def load(self, fobj):
        self.loads(fobj.read().decode(self._encoding))

    def dump(self, fobj):
        fobj.write(self.dumps().encode(self._encoding))

    def loads(self, text):
        for line in text.splitlines():
            line = line.strip()
            if line:
                full_hash, path = line.split(SEP, 1)
                self[path] = full_hash

    def dumps(self):
        return "\n".join(
            SEP.join((full_hash, path))
            for path, full_hash in sorted(self._data.items())
        )

    def save(self):
        with open(self.fs_path, "wb") as f:
            self.dump(f)


def add_hash_to_path(path, short_hash):
    # Here we assume posix (/-separated fs paths, just like url paths).
    # This may (i.e. will) break on non-posix.
    prefix, ext = os.path.splitext(path)
    if not ext:  # no extension
        return path
    return "{}.{}{}".format(prefix, short_hash, ext)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", required=True, help="path to manifest.in")
    parser.add_argument("--out", required=True, help="path to manifest")
    args = parser.parse_args()
    manifest_dot_in_path = getattr(args, "in")
    manifest_path = getattr(args, "out")
    with open(manifest_dot_in_path) as f:
        paths = f.read().splitlines()
    lines = []
    for path in paths:
        if path:
            with open(
                os.path.join(os.path.dirname(manifest_path), path),
                "rb",
            ) as f:
                s = f.read()
            full_hash = hashlib.sha1(s).hexdigest()
            lines.append("{}{}{}".format(full_hash, SEP, path))
    with open(manifest_path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()

