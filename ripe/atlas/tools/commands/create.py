from __future__ import print_function, absolute_import

import argparse
import re

from ripe.atlas.cousteau import (
    Ping, Traceroute, Dns, Sslcert, Ntp, AtlasSource, AtlasCreateRequest)

from ..exceptions import RipeAtlasToolsException
from ..settings import conf
from .base import Command as BaseCommand


class ArgumentType(object):

    @staticmethod
    def country_code(string):
        if not re.match(r"^[a-zA-Z][a-zA-Z]$", string):
            raise argparse.ArgumentTypeError(
                "Countries must be defined with a two-letter ISO code")
        return string.upper()


class Command(BaseCommand):

    DESCRIPTION = "Create a measurement and optionally wait for the results"
    URLS = {
        "create": "/api/v2/measurements.json"
    }

    CREATION_CLASSES = {
        "ping": Ping,
        "traceroute": Traceroute,
        "dns": Dns,
        "ssl": Sslcert,
        "ntp": Ntp
    }

    def add_arguments(self):

        # Required

        self.parser.add_argument(
            "type",
            type=str,
            choices=self.CREATION_CLASSES.keys(),
            help="The type of measurement you want to create"
        )

        # Standard for all types

        self.parser.add_argument(
            "--auth",
            type=str,
            default=conf["authorisation"]["create"],
            help="The API key you want to use to create the measurement"
        )
        self.parser.add_argument(
            "--af",
            type=int,
            default=conf["specification"]["af"],
            help="The address family, either 4 or 6"
        )
        self.parser.add_argument(
            "--description",
            type=str,
            default=conf["specification"]["description"],
            help="A free-form description"
        )
        self.parser.add_argument(  # Most types
            "--target",
            type=str,
            help="The target, either a domain name or IP address"
        )
        self.parser.add_argument(
            "--probes",
            type=int,
            default=conf["specification"]["source"]["requested"],
            help="The number of probes you want to use"
        )

        origins = self.parser.add_mutually_exclusive_group()
        origins.add_argument(
            "--from-area",
            type=str,
            choices=("WW", "West", "North-Central", "South-Central",
                     "North-East", "South-East"),
            help="The area from which you'd like to select your probes."
        )
        origins.add_argument(
            "--from-country",
            type=ArgumentType.country_code,
            help="The two-letter ISO code for the country from which you'd "
                 "like to select your probes."
        )

        # Type-specific

        # We do an early parse here so we can know the measurement type
        arguments = self.parser.parse_args()

        if arguments.type == "ping":
            self.parser.add_argument(
                "--packets",
                type=int,
                default=conf["specification"]["types"]["ping"]["packets"],
                help="The number of packets per result"
            )
            self.parser.add_argument(
                "--size",
                type=int,
                default=conf["specification"]["types"]["ping"]["size"],
                help="The size of packets sent"
            )
        elif arguments.type == "traceroute":
            self.parser.add_argument(
                "--protocol",
                type=str,
                default=conf["specification"]["types"]["traceroute"]["protocol"],
                choices=("ICMP", "UDP", "TCP"),
                help="A free-form description"
            )

    def run(self):
        """
        Main function that collects all users information from stdin, and
        creates a new UDM.
        """

        klass = self.CREATION_CLASSES[self.arguments.type]

        source = self._get_source()
        target = self.clean_target()

        (is_success, response) = AtlasCreateRequest(
            server=conf["ripe-ncc"]["endpoint"].replace("https://", ""),
            key=self.arguments.auth,
            measurements=[klass(
                af=self.arguments.af,
                target=target,
                description=self.arguments.description,
                packets=self.arguments.packets,
                size=self.arguments.size
            )],
            sources=[AtlasSource(
                type=source["type"],
                value=source["value"],
                requested=source["requested"]
            )]
        ).create()

        if is_success:
            self.ok(
                "Looking good!  Your measurement was created and details about "
                "it can be found here:\n\n  {}/measurements/{}/".format(
                    conf["ripe-ncc"]["endpoint"],
                    response["measurements"][0]
                )
            )

    def clean_target(self):

        # DNS measurements are a special case for targets
        if self.arguments.type == "dns":
            if self.arguments.use_probes_resolver:
                if self.arguments.target:
                    raise RipeAtlasToolsException(
                        "You may not specify a target for a DNS measurement "
                        "that uses the probe's resolver"
                    )
                return None

        # All other measurement types require it
        if not self.arguments.target:
            raise RipeAtlasToolsException(
                "You must specify a target for that kind of measurement"
            )

        return self.arguments.target

    def _get_source(self):

        r = conf["specification"]["source"]
        if self.arguments.from_country:
            r["type"] = "country"
            r["value"] = self.arguments.from_country
        elif self.arguments.from_area:
            r["type"] = "area"
            r["value"] = self.arguments.from_area

        return r
