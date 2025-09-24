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

import json
import os
import re
import webbrowser

from collections import OrderedDict

from ripe.atlas.cousteau import (
    Ping,
    Traceroute,
    Dns,
    Sslcert,
    Http,
    Ntp,
    AtlasSource,
    AtlasCreateRequest,
)
from ripe.atlas.cousteau.measurement import AtlasMeasurement
from ripe.atlas.cousteau import AtlasStream

from ...exceptions import RipeAtlasToolsException
from ...helpers.colours import colourise
from ...helpers.validators import ArgumentType
from ...renderers import Renderer
from ...settings import conf, aliases, AliasesDB
from ...streaming import StreamWrapper
from ..base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "measure"

    DESCRIPTION = "Create a measurement and optionally wait for the results"

    CREATION_CLASSES = OrderedDict(
        (
            ("ping", Ping),
            ("traceroute", Traceroute),
            ("dns", Dns),
            ("sslcert", Sslcert),
            ("http", Http),
            ("ntp", Ntp),
            ("spec", AtlasMeasurement),
        )
    )

    def __init__(self, *args, **kwargs):

        self._type = None
        self._is_oneoff = True

        BaseCommand.__init__(self, *args, **kwargs)

    def _modify_parser_args(self, args):

        kinds = self.CREATION_CLASSES.keys()
        error = (
            "Usage: ripe-atlas measure <{}> [options]\n"
            "\n"
            "  Example: ripe-atlas measure ping --target example.com"
            "".format("|".join(kinds))
        )

        if not args:
            raise RipeAtlasToolsException(error)

        if args[0] not in self.CREATION_CLASSES.keys():
            raise RipeAtlasToolsException(error)
        self._type = args.pop(0)

        if not args:
            args.append("--help")

        return BaseCommand._modify_parser_args(self, args)

    def add_arguments(self):

        self.parser.add_argument(
            "--renderer",
            choices=Renderer.get_available(),
            help="The renderer you want to use. If this isn't defined, an "
            "appropriate renderer will be selected.",
        )
        self.parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not create the measurement, only show its definition.",
        )

        # Standard for all types

        self.parser.add_argument(
            "--auth",
            type=str,
            default=os.getenv("ATLAS_CREATE_KEY", conf["authorisation"]["create"]),
            help="The API key you want to use to create the measurement. "
            "(Can be defined with `ripe-atlas configure --set authorisation.create` "
            "or the ATLAS_CREATE_KEY environment variable)",
        )
        self.parser.add_argument(
            "--af",
            type=int,
            choices=(4, 6),
            help="The address family, either 4 or 6",
        )
        self.parser.add_argument(
            "--description",
            type=str,
            default=conf["specification"]["description"],
            help="A free-form description",
        )
        self.parser.add_argument(  # Most types
            "--target",
            type=ArgumentType.ip_or_domain,
            help="The target, either a domain name or IP address.  If creating "
            "a DNS measurement, the absence of this option will imply "
            "that you wish to use the probe's resolver.",
        )
        self.parser.add_argument(
            "--no-report",
            action="store_true",
            help="Don't wait for a response from the measurement, just return "
            "the URL at which you can later get information about the "
            "measurement.",
        )
        self.parser.add_argument(
            "--go-web",
            action="store_true",
            help="Open the measurement in a webbrowser immediately.",
        )
        self.parser.add_argument(
            "--set-alias",
            help="After creating the measurement, register an alias for it.",
            type=ArgumentType.alias_is_valid,
            metavar="ALIAS",
        )

        self.parser.add_argument(
            "--interval",
            type=int,
            help="Rather than run this measurement as a one-off (the default), "
            "create this measurement as a recurring one, with an interval "
            "of n seconds between attempted measurements. This option "
            "implies --no-report.",
        )

        origins = self.parser.add_mutually_exclusive_group()
        origins.add_argument(
            "--from-area",
            type=str,
            choices=(
                "WW",
                "West",
                "North-Central",
                "South-Central",
                "North-East",
                "South-East",
            ),
            help="The area from which you'd like to select your probes.",
        )
        origins.add_argument(
            "--from-country",
            type=ArgumentType.country_code,
            metavar="COUNTRY",
            help="The two-letter ISO code for the country from which you'd "
            "like to select your probes. Example: --from-country=GR",
        )
        origins.add_argument(
            "--from-prefix",
            type=str,
            metavar="PREFIX",
            help="The prefix from which you'd like to select your probes. "
            "Example: --from-prefix=82.92.0.0/14",
        )
        origins.add_argument(
            "--from-asn",
            # http://www.iana.org/assignments/as-numbers/as-numbers.xhtml
            type=ArgumentType.integer_range(1, 2**32 - 2),
            metavar="ASN",
            help="The ASN from which you'd like to select your probes. "
            "Example: --from-asn=3333",
        )
        origins.add_argument(
            "--from-probes",
            type=ArgumentType.comma_separated_integers(minimum=1),
            metavar="PROBES",
            help="A comma-separated list of probe-ids you want to use in your "
            "measurement. Example: --from-probes=1,2,34,157,10006",
        )
        origins.add_argument(
            "--from-measurement",
            type=ArgumentType.integer_range(minimum=1),
            metavar="MEASUREMENT_ID",
            help="A measurement id which you want to use as the basis for "
            "probe selection in your new measurement.  This is a handy "
            "way to re-create a measurement under conditions similar to "
            "another measurement. Example: --from-measurement=1000192",
        )
        self.parser.add_argument(
            "--probes",
            type=ArgumentType.integer_range(minimum=1),
            default=None,
            help="The number of probes you want to use.  Defaults to {},"
            "unless --from-probes is invoked, in which case the number of "
            "probes selected is used.".format(
                conf["specification"]["source"]["requested"]
            ),
        )
        self.parser.add_argument(
            "--include-tag",
            type=ArgumentType.tag,
            action="append",
            metavar="TAG",
            help="Include only probes that are marked with these tags. "
            "Example: --include-tag=system-ipv6-works",
        )
        self.parser.add_argument(
            "--exclude-tag",
            type=ArgumentType.tag,
            action="append",
            metavar="TAG",
            help="Exclude probes that are marked with these tags. "
            "Example: --exclude-tag=system-ipv6-works",
        )

        self.parser.add_argument(
            "--group-id",
            type=int,
            help="Add newly created measurement to a group that you own",
        )

        # Validation is too complex because it's based on the interval, so
        # we just accept the round-trip for server-side validation
        self.parser.add_argument(
            "--spread",
            type=int,
            default=conf["specification"]["spread"],
            help="Specify the spread of probes within a single measurement interval",
        )
        self.add_flag(
            parser=self.parser,
            name="resolve-on-probe",
            default=conf["specification"]["resolve_on_probe"],
            help="Resolve the target on each probe instead of once by the server",
            no_help="Resolve the target once on the server instead of on each probe",
        )
        self.parser.add_argument(
            "--measurement-tags",
            help="Comma-separated list of tags to apply to the new measurement",
        )
        self.parser.add_argument(
            "--stream-limit",
            type=int,
            help="The maximum number of results you want to stream, "
            "defaults to number of requested probes",
        )
        self.parser.add_argument(
            "--stream-timeout",
            type=float,
            default=300,
            help="Stop streaming new measurements after this number of seconds",
        )

        Renderer.add_arguments_for_available_renderers(self.parser)

    def run(self) -> None:

        self._account_for_selected_probes()

        if self.arguments.dry_run:
            return self.dry_run()

        is_success, response = self.create()

        if not is_success:
            self._handle_api_error(response)  # Raises an exception

        msm_id = response["measurements"][0]
        url = "{0}/measurements/{1}/".format(conf["website-url"], msm_id)

        self.ok(
            f"Looking good! Measurement {msm_id} was created and details about "
            f"it can be found here:\n\n  {url}"
        )
        if self.arguments.go_web:
            self.ok("Opening the url in the browser\n\n ")
            if not webbrowser.open(url):
                self.ok(
                    "It looks like your system doesn't have a web browser "
                    "available.  You'll have to go there manually: {0}".format(url)
                )

        if self.arguments.set_alias:
            alias = self.arguments.set_alias
            aliases["measurement"][alias] = msm_id
            AliasesDB.write(aliases)

        if not self.arguments.no_report:
            self.stream(msm_id)

    def dry_run(self):

        print(colourise("\nDefinitions:\n{}".format("=" * 80), "bold"))

        for param, val in self._get_measurement_kwargs().items():
            print(colourise("{:<25} {}".format(param, val), "cyan"))

        print(colourise("\nSources:\n{}".format("=" * 80), "bold"))

        for param, val in self._get_source_kwargs().items():
            if param == "tags":
                print(
                    colourise(
                        "tags\n  include{}{}\n  exclude{}{}\n".format(
                            " " * 17,
                            ", ".join(val["include"]),
                            " " * 17,
                            ", ".join(val["exclude"]),
                        ),
                        "cyan",
                    )
                )
                continue
            print(colourise("{:<25} {}".format(param, val), "cyan"))

    def create(self):
        creation_class = self.CREATION_CLASSES[self._type]

        return AtlasCreateRequest(
            server=conf["api-server"],
            key=self.arguments.auth,
            user_agent=self.user_agent,
            measurements=[creation_class(**self._get_measurement_kwargs())],
            sources=[AtlasSource(**self._get_source_kwargs())],
            is_oneoff=self._is_oneoff,
        ).create()

    def stream(self, msm_id: int) -> None:
        stream = AtlasStream(base_url=conf["stream-base-url"])
        stream.connect()
        self.ok("Subscribing to stream...")
        stream.subscribe("result", msm=msm_id, sendBacklog=True)
        capture_limit = self.arguments.stream_limit or self.arguments.probes
        renderer = Renderer.get_renderer(name=self.arguments.renderer, kind=self._type)(
            arguments=self.arguments
        )
        renderer.render(
            StreamWrapper(
                stream,
                capture_limit=capture_limit,
                timeout=self.arguments.stream_timeout,
            )
        )
        stream.disconnect()
        self.ok("Disconnected from stream")

    def clean_target(self):

        if not self.arguments.target:
            raise RipeAtlasToolsException(
                "You must specify a target for that kind of measurement"
            )

        return self.arguments.target

    def clean_description(self):
        if self.arguments.description:
            return self.arguments.description
        if conf["specification"]["description"]:
            return conf["specification"]["description"]
        return "{} measurement to {}".format(
            self._type.capitalize(), self.arguments.target
        )

    def _get_measurement_kwargs(self):

        # This is kept apart from the r = {} because dns measurements don't
        # require a target attribute
        target = self.clean_target()

        r = {
            "af": self._get_af(),
            "description": self.clean_description(),
        }

        spec = conf["specification"]  # Shorter names are easier to read
        if self.arguments.interval or spec["times"]["interval"]:
            r["interval"] = self.arguments.interval
            self._is_oneoff = False
            self.arguments.no_report = True
        elif not spec["times"]["one-off"]:
            raise RipeAtlasToolsException(
                "Your configuration file appears to be setup to not create "
                "one-offs, but also offers no interval value.  Without one of "
                "these, a measurement cannot be created."
            )

        if self.arguments.measurement_tags:
            tags = self.arguments.measurement_tags.split(",")
            r["tags"] = tags

        if target:
            r["target"] = target

        if self.arguments.group_id:
            r["group_id"] = self.arguments.group_id

        if self.arguments.spread is not None:
            r["spread"] = self.arguments.spread

        if self.arguments.resolve_on_probe is not None:
            r["resolve_on_probe"] = self.arguments.resolve_on_probe

        return r

    def _get_source_kwargs(self):

        r = conf["specification"]["source"]

        r["requested"] = self.arguments.probes
        if self.arguments.from_country:
            r["type"] = "country"
            r["value"] = self.arguments.from_country
        elif self.arguments.from_area:
            r["type"] = "area"
            r["value"] = self.arguments.from_area
        elif self.arguments.from_prefix:
            r["type"] = "prefix"
            r["value"] = self.arguments.from_prefix
        elif self.arguments.from_asn:
            r["type"] = "asn"
            r["value"] = self.arguments.from_asn
        elif self.arguments.from_probes:
            r["type"] = "probes"
            r["value"] = ",".join([str(_) for _ in self.arguments.from_probes])
        elif self.arguments.from_measurement:
            r["type"] = "msm"
            r["value"] = self.arguments.from_measurement

        r["tags"] = {
            "include": self.arguments.include_tag or [],
            "exclude": self.arguments.exclude_tag or [],
        }

        af = "ipv{}".format(self._get_af())
        kind = self._type
        spec = conf["specification"]
        for clude in ("in", "ex"):
            clude += "clude"
            if not r["tags"][clude]:
                r["tags"][clude] += spec["tags"][af][kind][clude]
                r["tags"][clude] += spec["tags"][af]["all"][clude]

        return r

    def _get_af(self):
        """
        Returns the specified af, or a guessed one, or the configured one.  In
        that order.
        """
        if self.arguments.af:
            return self.arguments.af
        if self.arguments.target:
            if ":" in self.arguments.target:
                return 6
            if re.match(r"^\d+\.\d+\.\d+\.\d+$", self.arguments.target):
                return 4
        return conf["specification"]["af"]

    def _account_for_selected_probes(self):
        """
        If the user has used --from-probes, there's a little extra magic we
        need to do.
        """

        # We can't use argparse's mutually_exclusive_group() method here because
        # that library doesn't allow partial overlap.
        if self.arguments.from_probes and self.arguments.probes:
            raise RipeAtlasToolsException(
                "Explicit probe selection (--from-probes) in incompatible with "
                "a --probes argument."
            )

        configured = conf["specification"]["source"]["requested"]
        if not self.arguments.probes:
            self.arguments.probes = configured
            if self.arguments.from_probes:
                self.arguments.probes = len(self.arguments.from_probes)

    @staticmethod
    def _handle_api_error(response):

        message = "There was a problem communicating with the RIPE Atlas API."

        if isinstance(response, dict):
            if response.get("error", {}).get("status") == 403:
                message += (
                    "\n\nThe status is 403 so you probably need an API key.\n\n"
                    "Go to https://atlas.ripe.net/keys/ and create a key with the "
                    "permission 'Create a new user defined measurement' and install "
                    "using:\n\n"
                    " ripe-atlas configure --set authorisation.create=MY_API_KEY\n"
                )

        message += f"\n\n{json.dumps(response, indent=2)}"

        raise RipeAtlasToolsException(message)
