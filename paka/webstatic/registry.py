import os

from six.moves.urllib.parse import urljoin
from markupsafe import escape

from .manifest import Manifest, add_hash_to_path


def _html_escape(s):
    return str(escape(s))


def _prepare_url_path(path):
    if not path.endswith("/"):
        return "".join((path, "/"))
    return path


class Registry(object):

    def __init__(self, url_path, fs_path, types, domain=None):
        self.url_path = _prepare_url_path(url_path)
        self.domain = domain
        self.fs_path = os.path.abspath(fs_path)
        for name, rtype_obj in types.items():
            self.add_type(name, rtype_obj)
        self.manifest = None

    def add_type(self, name, rtype_obj):
        rtype_obj.bind(registry=self)
        setattr(self, name, rtype_obj)

    def load_manifest(self, path="manifest", data=None, **kwargs):
        fs_path = os.path.join(self.fs_path, path)
        self.manifest = Manifest(fs_path, **kwargs)
        if data:
            for k, v in data.items():
                self.manifest[k] = v
        else:
            with open(fs_path, "rb") as f:
                self.manifest.load(f)


class RType(object):

    class _Wrapper(object):

        def __init__(self, rtype_obj, args, kwargs):
            self._rtype_obj = rtype_obj
            self._args = args
            self._kwargs = kwargs

        def _call(self, name):
            return getattr(self._rtype_obj, name)(*self._args, **self._kwargs)

        def __getattr__(self, name):
            return self._call(name)

    def __init__(self):
        self._registry = None

    def __call__(self, *args, **kwargs):
        return self._Wrapper(self, args, kwargs)

    def bind(self, registry):
        self._registry = registry

    def url(self):
        raise NotImplementedError

    def urls(self):
        raise NotImplementedError

    def url_path(self):
        raise NotImplementedError

    def url_paths(self):
        raise NotImplementedError

    def fs_path(self):
        raise NotImplementedError

    def fs_paths(self):
        raise NotImplementedError

    def html(self):
        raise NotImplementedError


class PathHelpers(object):

    def _get_url(self, *args):
        if not self._registry.domain:
            raise NotImplementedError
        return urljoin(
            "".join(("//", self._registry.domain)),
            self._get_url_path(*args)
        )

    def _get_url_path(self, *args):
        path = urljoin(self._registry.url_path, self._url_path)
        for arg in args:
            path = urljoin(path, arg)
        return path

    def _get_fs_path(self, *args):
        return os.path.normpath(
            os.path.join(
                self._registry.fs_path,
                self._fs_path,
                *args
            )
        )


class PathSpecAcceptingRType(RType, PathHelpers):

    def __init__(self, url_path, fs_path):
        super(PathSpecAcceptingRType, self).__init__()
        self._url_path = _prepare_url_path(url_path)
        self._fs_path = fs_path

    def _dispatch_absolute_url(self, absolute_url):
        if absolute_url:
            return self.url
        return self.url_path

    def url(self, spec):
        return self._get_url(spec)

    def urls(self, *specs):
        return map(self.url, specs)

    def url_path(self, spec):
        return self._get_url_path(spec)

    def url_paths(self, *specs):
        return map(self.url_path, specs)

    def fs_path(self, spec):
        return self._get_fs_path(spec)

    def fs_paths(self, *specs):
        return map(self.fs_path, specs)


class ManifestConsultingPathSpecAcceptingRType(PathSpecAcceptingRType):
    _DEFAULT_ADD_HASH = object()

    def __init__(self, url_path, fs_path, add_hash):
        super(
            ManifestConsultingPathSpecAcceptingRType, self).__init__(
                url_path=url_path, fs_path=fs_path)
        self._add_hash = add_hash

    def _add(self, path, spec, add_hash):
        manifest = self._registry.manifest
        if (
            not self._add_hash or
            not manifest or
            (add_hash is not self._DEFAULT_ADD_HASH and not add_hash)
        ):
            return path
        try:
            return add_hash_to_path(
                path,
                manifest[
                    super(
                        ManifestConsultingPathSpecAcceptingRType,
                        self).fs_path(spec)]
            )
        except KeyError:
            return path

    def url(self, spec, add_hash=_DEFAULT_ADD_HASH):
        return self._add(
            super(
                ManifestConsultingPathSpecAcceptingRType, self).url(
                    spec), spec=spec, add_hash=add_hash)

    def url_path(self, spec, add_hash=_DEFAULT_ADD_HASH):
        return self._add(
            super(
                ManifestConsultingPathSpecAcceptingRType,
                self).url_path(spec),
            spec=spec, add_hash=add_hash)

    def fs_path(self, spec, add_hash=_DEFAULT_ADD_HASH):
        return self._add(
            super(
                ManifestConsultingPathSpecAcceptingRType,
                self).fs_path(spec),
            spec=spec, add_hash=add_hash)


class CSSRType(ManifestConsultingPathSpecAcceptingRType):

    def html(self, spec, media=None, absolute_url=False):
        if not media:
            media_s = ""
        else:
            media_s = " media=\"{}\"".format(_html_escape(media))
        return """<link rel="stylesheet" href="{}"{}>""".format(
            _html_escape(self._dispatch_absolute_url(absolute_url)(spec)),
            media_s,
        )


class JSRType(ManifestConsultingPathSpecAcceptingRType):

    def html(self, spec, defer=False, async=False, absolute_url=False):
        attrs = [""]  # to get " one" or ""
        if defer:
            attrs.append("defer")
        if async:
            attrs.append("async")
        return """<script src="{url_path}"{attrs}></script>""".format(
            url_path=_html_escape(
                self._dispatch_absolute_url(absolute_url)(spec)
            ),
            attrs=" ".join(attrs),
        )


class FileRType(ManifestConsultingPathSpecAcceptingRType):

    def html(self, spec):
        raise NotImplementedError


class FaviconRType(RType, PathHelpers):

    def __init__(self, fs_path, ext="ico"):
        super(FaviconRType, self).__init__()
        self._fs_path = fs_path
        self._ext = ext

    def _get_name(self, ext):
        return ".".join(("favicon", ext or self._ext))

    def url_path(self, ext=None):
        return "".join(("/", self._get_name(ext)))

    def fs_path(self, ext=None):
        return self._get_fs_path(self._get_name(ext))

