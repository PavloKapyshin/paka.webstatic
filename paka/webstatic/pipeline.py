import os
import hashlib

from .manifest import add_hash_to_path
from . import cssmin, jsmin


DEFAULT_ENCODING = "utf-8"


class Input(object):

    def __init__(self, paths, encoding=DEFAULT_ENCODING):
        self._inputs = [InputItem(path) for path in paths]
        self._encoding = encoding

    def map_over_data(self, func):
        for inp in self._inputs:
            inp.map_over_data(func)
        return self


class InputItem(object):

    def __init__(self, path, data=None, encoding=DEFAULT_ENCODING):
        self.path = path
        self._encoding = encoding
        self._data = data
        self._to_read = self.path if data is None else None

    def map_over_data(self, func):
        self._data = func(self.data)
        return self

    def append(self, s):
        self._data = "".join((self._data or "", s))

    @property
    def data(self):
        if not self._data and self._to_read:
            with open(self._to_read, "rb") as f:
                self._data = f.read().decode(self._encoding)
            self._to_read = None
        return self._data


class Output(object):

    def __init__(
        self,
        out_path,
        encoding=DEFAULT_ENCODING,
        manifest=None,
        hasher=lambda contents: hashlib.sha1(contents).hexdigest(),
        makedirs=False,
    ):
        self._out_path = out_path
        self._encoding = encoding
        self._manifest = manifest
        self._hasher = hasher
        self._makedirs = makedirs

    def __call__(self, input_):
        contents = input_.data.encode(self._encoding)
        path = self._out_path
        if self._manifest:
            manifest = self._manifest
            try:  # try to remove old file (path of which has old hash)
                os.remove(add_hash_to_path(path, manifest[path]))
            except (KeyError, OSError):
                pass
            manifest[path] = self._hasher(contents)
            manifest.save()
            path = add_hash_to_path(path, manifest[path])
        if self._makedirs:
            try:
                os.makedirs(os.path.dirname(path))
            except OSError:
                pass
        with open(path, "wb") as f:
            f.write(contents)
        input_.path = path
        return input_


class Concat(object):

    def __call__(self, input_):
        output = InputItem(path=None)
        input_.map_over_data(output.append)
        return output


class CSSMin(object):

    def __call__(self, input_):
        return input_.map_over_data(cssmin.cssmin)


class JSMin(object):

    def __call__(self, input_):
        return input_.map_over_data(jsmin.jsmin)


class Replace(object):

    def __init__(self, consts):
        self._consts = dict(consts)

    def __call__(self, input_):
        return input_.map_over_data(self._replace)

    def _replace(self, data):
        for k, v in self._consts.items():
            data = data.replace(k, v)
        return data


def run(pl):
    pl = tuple(pl)
    input_ = pl[0]
    for proc in pl[1:]:
        input_ = proc(input_)
    return input_

