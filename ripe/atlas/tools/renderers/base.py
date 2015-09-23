import importlib
import os
import pkgutil
import sys

from ..exceptions import RipeAtlasToolsException


class Renderer(object):

    TYPE_PING = "ping"
    TYPE_TRACEROUTE = "traceroute"
    TYPE_DNS = "dns"
    TYPE_TLS = "sslcert"
    TYPE_HTTP = "http"
    TYPE_NTP = "ntp"

    RENDERS = ()

    # def __init__(self, parser):
    #     self.parser = parser

    @staticmethod
    def get_available():

        paths = [os.path.dirname(__file__)]
        if "HOME" in os.environ:
            path = os.path.join(
                os.environ["HOME"], ".config", "ripe-atlas-tools", "renderers")
            sys.path.append(path)
            paths += [path]

        r = [package_name for _, package_name, _ in pkgutil.iter_modules(paths)]
        r.remove("base")

        return r

    def add_arguments(self):
        pass

    @staticmethod
    def render(template, **kwargs):
        """
        A crude templating engine.
        """

        template = os.path.join(
            os.path.dirname(__file__), "templates", template)

        with open(template) as f:
            return f.read().format(**kwargs)

    @classmethod
    def get_renderer(cls, name=None, kind=None):

        error_message = 'The renderer you selected, "{}" could not be found.'.format(name)

        try:  # User-defined, user-supplied
            r = cls.import_renderer("renderers", name)
        except ImportError:
            try:  # User-defined, officially-supported
                r = cls.import_renderer("ripe.atlas.tools.renderers", name)
            except ImportError:
                try:  # Type-determined, officially-supported
                    r = cls.import_renderer("ripe.atlas.tools.renderers", kind)
                except ImportError:
                    raise RipeAtlasToolsException(error_message)
        return r

    @staticmethod
    def import_renderer(package, name):
        return getattr(
            importlib.import_module(".{0}".format(name), package=package),
            "Renderer"
        )

    @staticmethod
    def _test_renderer_accepts_kind(renderer, kind):
        if kind not in renderer.RENDERS:
            raise RipeAtlasToolsException(
                'The renderer selected does not appear to support measurements'
                'of type "{}"'.format(kind)
            )

    def on_start(self):
        """
        This is called before any results are parsed and should always return a
        string, even if that string is "".
        """
        return ""

    def on_result(self, result, probes=None):
        """
        This must be defined in the subclass, and must return a string, even if
        that string is "".
        """
        raise NotImplementedError()

    def on_finish(self):
        """
        This is called after a report is finished looping over the available
        results, or when a stream is stopped (for whatever reason).  It should
        return a string, even if that string is "".
        """
        return ""
