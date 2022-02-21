# Copyright (c) 2016 RIPE NCC
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
from ..helpers import xdg


class Renderer(object):

    TYPE_PING = "ping"
    TYPE_TRACEROUTE = "traceroute"
    TYPE_DNS = "dns"
    TYPE_SSLCERT = "sslcert"
    TYPE_HTTP = "http"
    TYPE_NTP = "ntp"

    RENDERS = ()

    def __init__(self, *args, **kwargs):
        """
        If "arguments" is in kwargs it can be used to gather renderer's
        optional arguments which have been passed via CLI.
        See also add_arguments().
        """
        self.show_header = True
        self.show_footer = True
        if "arguments" in kwargs:
            self.show_header = kwargs["arguments"].show_header
            self.show_footer = kwargs["arguments"].show_footer

    @classmethod
    def get_available(cls):
        """
        Return a list of renderers available to be used.
        """

        paths = [os.path.dirname(__file__)]
        if "HOME" in os.environ:
            path = xdg.get_config_home()
            sys.path.append(path)
            paths += [os.path.join(path, "renderers")]

        names = []

        for _, module_name, _ in pkgutil.iter_modules(paths):
            if module_name == "base":
                continue
            # Check that we can actually use this renderer, otherwise drop it
            try:
                cls.get_renderer_by_name(module_name)
            except Exception:
                continue
            names.append(module_name)

        return names

    @staticmethod
    def add_common_arguments(parser):
        group = parser.add_argument_group(title="Optional arguments for all renderers")
        group.add_argument(
            "--no-header",
            dest="show_header",
            action="store_false",
            help="Don't show a header/title before rendering results",
        )
        group.add_argument(
            "--no-footer",
            dest="show_footer",
            action="store_false",
            help="Don't show a footer/summary after rendering results",
        )

    @staticmethod
    def add_arguments_for_available_renderers(parser):
        Renderer.add_common_arguments(parser)
        for renderer_name in Renderer.get_available():
            renderer_cls = Renderer.get_renderer_by_name(renderer_name)
            renderer_cls.add_arguments(parser)

    @staticmethod
    def render_template(template, **kwargs):
        """
        A crude templating engine.
        """

        template = os.path.join(os.path.dirname(__file__), "templates", template)

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
        error_message = f'The renderer you selected, "{name}" could not be found.'

        # User-defined, user-supplied
        r = cls.import_renderer("renderers", name)
        if not r:
            r = cls.import_renderer("ripe.atlas.tools.renderers", name)
        if not r:
            raise RipeAtlasToolsException(error_message)

        return r

    @classmethod
    def get_renderer_by_kind(cls, kind):
        error_message = (
            f'A default renderer for "{kind}" measurements could not be found.'
        )

        r = cls.import_renderer("ripe.atlas.tools.renderers", kind)
        if not r:
            raise RipeAtlasToolsException(error_message)

        return r

    @staticmethod
    def import_renderer(package, name):
        """
        Return the Renderer class from package.name, or None if either package
        or package.name don't exist.
        """
        full_name = f"{package}.{name}"
        try:
            spec = importlib.util.find_spec(full_name)
        except ModuleNotFoundError:
            return
        if not spec:
            return
        return getattr(importlib.import_module(full_name), "Renderer")

    @staticmethod
    def add_arguments(parser):
        """
        Add renderer's optional arguments here.

        Suggested format:

        group = parser.add_argument_group(
            title="Optional arguments for XXX renderer"
        )
        group.add_argument(
            ...
        )
        """
        pass

    def render(self, results, sample=None):
        """
        Render the given iterable of RIPE Atlas JSON results.
        """
        # Put aggregated and unaggregated results in the same format
        normalized = dict(results) if isinstance(results, dict) else {"": results}

        header_shown = False
        last_key = None

        for key, results in normalized.items():
            for sagan in results:
                # Possibly show render header
                if self.show_header and not header_shown:
                    print(self.header(sagan), end="")
                    header_shown = True

                if key:
                    indent = " "
                    if key != last_key:
                        # Show aggregation group header
                        print("\n" + key)
                        last_key = key
                else:
                    indent = ""

                line = Result(self.on_result(sagan), sagan.probe_id)

                print(indent + line, end="")

        if self.show_footer:
            print(self.footer(), end="")

    def header(self, sample):
        """
        Override this to add a header.

        `sample` is a single parsed result from the result set (probably the
        first one). It can be used to infer metadata about the measurement
        without having to do an extra API call.
        """
        return ""

    def footer(self):
        """
        Override this to add a footer.

        To provide a summary here, statistics should be gathered in the
        `on_result` callback, ideally without storing all results in memory.
        """
        return ""

    @staticmethod
    def _test_renderer_accepts_kind(renderer, kind):
        if kind not in renderer.RENDERS:
            raise RipeAtlasToolsException(
                "The renderer selected does not appear to support measurements "
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
