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
            print(f.read().format(**kwargs))

    @staticmethod
    def get_formatter(name):

        if name == "ping":
            from .ping import PingReport
            return PingReport

        raise NotImplemented()
