from __future__ import print_function

import json

from ripe.atlas.cousteau import AtlasRequest
from ripe.atlas.sagan import Result, ResultError

from ..exceptions import RipeAtlasToolsException
from ..helpers.validators import ArgumentType
from ..reports import Report
from .base import Command as BaseCommand


class Command(BaseCommand):

    DESCRIPTION = "Report the results of a measurement"
    URLS = {
        "detail": "/api/v2/measurements/{0}.json",
        "latest": "/api/v2/measurements/{0}/latest.json",
    }

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=int,
            help="The measurement id you want reported"
        )
        self.parser.add_argument(
            "--probes",
            type=ArgumentType.comma_separated_integers,
            help="A comma-separated list of probe ids you want to see "
                 "exclusively"
        )

    def get_probes(self):
        if self.arguments.probes:
            return [int(i) for i in self.arguments.probes.split(",")]
        return []

    def run(self):

        pk = self.arguments.measurement_id
        probes = self.get_probes()

        latest_url = self.URLS["latest"].format(pk)
        if self.arguments.probes:
            latest_url += "?probes={0}".format(self.arguments.probes)

        detail = AtlasRequest(url_path=self.URLS["detail"].format(pk)).get()[1]
        latest = AtlasRequest(url_path=latest_url).get()[1]

        if not latest:
            raise RipeAtlasToolsException(
                "There aren't any results available for that measurement")

        formatter_instance = Report.get_formatter(detail["type"]["name"])()

        payload = ""
        for result in latest:
            result = Result.get(result)
            try:
                payload += formatter_instance.format(result, probes=probes)
            except ResultError:
                payload += json.dumps(result) + "\n"

        description = detail["description"] or ""
        if description:
            description = "\n{0}\n\n".format(description)

        print(formatter_instance.render(
            "reports/base.txt",
            measurement_id=self.arguments.measurement_id,
            description=description,
            payload=payload
        ), end="")
