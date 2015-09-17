import importlib
import os


class Report(object):

    @staticmethod
    def render(template, **kwargs):
        """
        A crude templating engine.
        """

        template = os.path.join(
            os.path.dirname(__file__), "templates", template)

        with open(template) as f:
            return f.read().format(**kwargs)

    @staticmethod
    def get_formatter(name):
        return getattr(
            importlib.import_module(
                ".{}".format(name),
                package="ripe.atlas.tools.reports"),
            "{}Report".format(name.capitalize())
        )

    @classmethod
    def format(cls, result, probes=None):
        raise NotImplementedError()
