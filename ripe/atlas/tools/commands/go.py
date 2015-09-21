import webbrowser
from .base import Command as BaseCommand


class Command(BaseCommand):

    DESCRIPTION = "Visit the web page for a specific measurement"
    URL = "https://atlas.ripe.net/measurements/{0}/"

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=int,
            help="The measurement id you want reported"
        )

    def run(self):
        url = self.URL.format(self.arguments.measurement_id)
        if not webbrowser.open(url):
            self.ok(
                "It looks like your system doesn't have a web browser "
                "available.  You'll have to go there manually: {0}".format(url)
            )
