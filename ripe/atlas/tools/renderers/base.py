# Copyright (c) 2015 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import importlib
import os
import pkgutil
import sys

from ..exceptions import RipeAtlasToolsException


class Renderer(object):

    TYPE_PING = "ping"
    TYPE_TRACEROUTE = "traceroute"
    TYPE_DNS = "dns"
    TYPE_SSLCERT = "sslcert"
    TYPE_HTTP = "http"
    TYPE_NTP = "ntp"

    RENDERS = ()

    SHOW_DEFAULT_HEADER = True
    SHOW_DEFAULT_FOOTER = True

    @staticmethod
    def get_available():
        """
        Return a list of renderers available to be used.
        """

        paths = [os.path.dirname(__file__)]
        if "HOME" in os.environ:
            path = os.path.join(
                os.environ["HOME"], ".config", "ripe-atlas-tools")
            sys.path.append(path)
            paths += [os.path.join(path, "renderers")]

        r = [package_name for _, package_name, _ in pkgutil.iter_modules(paths)]
        r.remove("base")

        return r

    @staticmethod
    def render(template, **kwargs):
        """
        A crude templating engine.
        """

        template = os.path.join(
            os.path.dirname(__file__), "templates", template)

        with open(template) as f:
            return str(f.read()).format(**kwargs)

    @classmethod
    def get_renderer(cls, name=None, kind=None):
        """
        Using the name if you've asked for it specifically, or attempting to
        guess the appropriate renderer based on the kind of measurement, this
        will return a Renderer subclass or None if nothing can be found.
        """

        renderer = None

        if name:
            renderer = cls.get_renderer_by_name(name)

        if not renderer and kind:
            renderer = cls.get_renderer_by_kind(kind)

        if kind:
            cls._test_renderer_accepts_kind(renderer, kind)

        return renderer

    @classmethod
    def get_renderer_by_name(cls, name):
        error_message = (
            'The renderer you selected, "{}" could not be found.'
        ).format(name)

        try:  # User-defined, user-supplied
            r = cls.import_renderer("renderers", name)
        except ImportError:
            try:  # User-defined, officially-supported
                r = cls.import_renderer("ripe.atlas.tools.renderers", name)
            except ImportError:
                raise RipeAtlasToolsException(error_message)

        return r

    @classmethod
    def get_renderer_by_kind(cls, kind):
        error_message = (
            'The selected renderer, "{}" could not be found.'
        ).format(kind)

        try:
            r = cls.import_renderer("ripe.atlas.tools.renderers", kind)
        except ImportError:
            raise RipeAtlasToolsException(error_message)

        return r

    @staticmethod
    def import_renderer(package, name):
        return getattr(
            importlib.import_module("{}.{}".format(package, name)),
            "Renderer"
        )

    @staticmethod
    def header(*args, **kwargs):
        """
        Override this to add an additional header.
        """
        pass

    @staticmethod
    def additional(*args, **kwargs):
        """
        Override this for summary logic.
        """
        pass

    @staticmethod
    def footer(*args, **kwargs):
        """
        Override this to add an additional footer.
        """
        pass

    @staticmethod
    def _test_renderer_accepts_kind(renderer, kind):
        if kind not in renderer.RENDERS:
            raise RipeAtlasToolsException(
                'The renderer selected does not appear to support measurements '
                'of type "{}"'.format(kind)
            )

    def on_result(self, result):
        """
        This must be defined in the subclass, and must return a string, even if
        that string is "".
        """
        raise NotImplementedError()


class Result(str):
    """
    A string-like object that we can use to render results, but that contains
    enough information to be used by the aggregators if need be.
    """
    def __new__(cls, value, probe_id):
        obj = str.__new__(cls, value)
        obj.probe_id = probe_id
        return obj
