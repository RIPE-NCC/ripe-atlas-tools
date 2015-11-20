from __future__ import print_function, absolute_import

from ripe.atlas.cousteau import Probe
from ripe.atlas.cousteau.exceptions import APIResponseError

from .base import Command as BaseCommand, MetaDataMixin
from ..exceptions import RipeAtlasToolsException
from ..helpers.colours import colourise


class Command(MetaDataMixin, BaseCommand):

    NAME = "probe"
    DESCRIPTION = "Returns the meta data for one probe"

    def add_arguments(self):
        self.parser.add_argument("id", type=int, help="The probe id")

    def run(self):

        try:
            probe = Probe(id=self.arguments.id)
        except APIResponseError:
            raise RipeAtlasToolsException(
                "That probe does not appear to exist")

        url_template = "https://atlas.ripe.net/probes/{}/"
        keys = (
            ("id", "ID"),
            ("id", "URL", lambda _: colourise(url_template.format(_), "cyan")),
            ("is_public", "Public?", self._prettify_boolean),
            ("is_anchor", "Anchor?", self._prettify_boolean),
            ("country_code", "Country"),
            ("description", "Description"),
            ("asn_v4", "ASN (IPv4)"),
            ("asn_v6", "ASN (IPv6)"),
            ("address_v4", "Address (IPv4)"),
            ("address_v6", "Address (IPv6)"),
            ("prefix_v4", "Prefix (IPv4)"),
            ("prefix_v6", "Prefix (IPv6)"),
            ("geometry", "Coordinates", self._prettify_coordinates),
            # ("tags", "Tags"),
            ("status", "Status"),
        )
        for key in keys:

            value = getattr(probe, key[0])

            if value is None:
                value = "-"
            elif len(key) == 3:
                value = key[2](value)

            self._render_line(key[1], value)

        print(colourise("Tags", "bold"))
        for tag in probe.tags:
            print("  {}".format(tag["slug"]))

    @staticmethod
    def _prettify_coordinates(geometry):
        if geometry and "coordinates" in geometry and geometry["coordinates"]:
            return "{},{}".format(
                geometry["coordinates"][1],
                geometry["coordinates"][0]
            )
