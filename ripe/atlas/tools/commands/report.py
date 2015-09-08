import json

from ripe.atlas.cousteau import AtlasRequest
from ripe.atlas.sagan import Result, ResultError

from ..exceptions import RipeAtlasToolsException
from ..reports import Report
from .base import Command as BaseCommand


class Command(BaseCommand):

    DESCRIPTION = "Report the results of a measurement"
    URLS = {
        "detail": "/api/v2/measurements/{}.json",
        "latest": "/api/v2/measurements/{}/latest.json",
    }

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=int,
            help="The measurement id you want reported"
        )

    def run(self):

        pk = self.arguments.measurement_id

        detail = AtlasRequest(url_path=self.URLS["detail"].format(pk)).get()[1]
        latest = AtlasRequest(url_path=self.URLS["latest"].format(pk)).get()[1]

        if not latest:
            raise RipeAtlasToolsException(
                "There aren't any results available for that measurement")

        formatter = Report.get_formatter(detail["type"]["name"])

        payload = ""
        for result in latest:
            result = Result.get(result)
            try:
                payload += formatter.format(result)
            except ResultError:
                payload += json.dumps(result) + "\n"

        formatter.render(
            "reports/base.txt",
            measurement_id=self.arguments.measurement_id,
            description=detail.get("description") or "",
            payload=payload
        )
