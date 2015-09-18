from __future__ import print_function, absolute_import

import json

from ripe.atlas.cousteau import (
    Ping, Traceroute, Dns, Sslcert, Ntp, AtlasSource, AtlasCreateRequest)
from ripe.atlas.sagan.dns import Message

from ..exceptions import RipeAtlasToolsException
from ..helpers.validators import ArgumentType
from ..settings import conf
from ..streaming import Stream, CaptureLimitExceeded
from .base import Command as BaseCommand


class Command(BaseCommand):

    DESCRIPTION = "Create a measurement and optionally wait for the results"

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
            choices=(4, 6),
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
            "--no-report",
            action="store_true",
            help="Don't wait for a response from the measurement, just return "
                 "the URL at which you can later get information about the "
                 "measurement"
        )

        self.parser.add_argument(
            "--interval",
            type=int,
            help="Rather than run this measurement as a one-off (the default), "
                 "create this measurement as a recurring one, with an interval "
                 "of n seconds between attempted measurements. This option "
                 "implies --no-report"
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
            metavar="COUNTRY",
            help="The two-letter ISO code for the country from which you'd "
                 "like to select your probes. Example: --from-country=GR"
        )
        origins.add_argument(
            "--from-prefix",
            type=str,
            metavar="PREFIX",
            help="The prefix from which you'd like to select your probes. "
                 "Example: --from-prefix=82.92.0.0/14"
        )
        origins.add_argument(
            "--from-asn",
            type=int,
            metavar="ASN",
            help="The ASN from which you'd like to select your probes. "
                 "Example: --from-asn=3265"
        )
        origins.add_argument(
            "--from-probes",
            type=str,
            metavar="PROBES",
            help="A comma-separated list of probe-ids you want to use in your"
                 "measurement. Example: --from-probes=1,2,34,157,10006"
        )
        origins.add_argument(
            "--from-measurement",
            type=ArgumentType.comma_separated_integers,
            metavar="MEASUREMENT_ID",
            help="A measurement id which you want to use as the basis for probe"
                 "selection in your new measurement.  This is a handy way to"
                 "re-create a measurement under conditions similar to another"
                 "measurement. Example: --from-measurement=1000192"
        )
        self.parser.add_argument(
            "--probes",
            type=int,
            default=conf["specification"]["source"]["requested"],
            help="The number of probes you want to use"
        )

        # Type-specific

        ping_or_trace = self.parser.add_argument_group(
            "Ping and Traceroute Measurements")
        ping_or_trace.add_argument(
            "--packets", type=int, help="The number of packets sent"
        )
        ping_or_trace.add_argument(
            "--size", type=int, help="The size of packets sent"
        )

        trace_or_dns = self.parser.add_argument_group(
            "Traceroute or DNS Measurements")
        trace_or_dns.add_argument(
            "--protocol",
            type=str,
            choices=("ICMP", "UDP", "TCP"),
            help="The protocol used.  For DNS measurements, this is limited to "
                 "UDP and TCP, but traceroutes may use ICMP as well"
        )

        traceroute = self.parser.add_argument_group(
            "Traceroute Measurements")
        traceroute.add_argument(
            "--timeout",
            type=int,
            default=conf["specification"]["types"]["traceroute"]["timeout"],
            help="The timeout per-packet"
        )

        dns = self.parser.add_argument_group("DNS Measurements")
        dns.add_argument(
            "--query-class",
            type=str,
            choices=("IN", "CHAOS"),
            default=conf["specification"]["types"]["dns"]["query-class"],
        )
        dns.add_argument(
            "--query-type",
            type=str,
            choices=Message.ANSWER_CLASSES.keys() + ["ANY"],  # The only ones we can parse
            default=conf["specification"]["types"]["dns"]["query-type"],
        )
        dns.add_argument(
            "--query-argument",
            type=str,
            default=conf["specification"]["types"]["dns"]["query-argument"],
        )
        dns.add_argument(
            "--use-probe-resolver",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["use-probe-resolver"],
            help="Use the probe's list of local resolvers instead of "
                 "specifying a target to use as the resolver.  Note that this "
                 "may not be used with --target"
        )
        dns.add_argument(
            "--udp-payload-size",
            type=int,
            default=conf["specification"]["types"]["dns"]["udp-payload-size"],
        )

    def run(self):

        creation_class = self.CREATION_CLASSES[self.arguments.type]

        (is_success, response) = AtlasCreateRequest(
            server=conf["ripe-ncc"]["endpoint"].replace("https://", ""),
            key=self.arguments.auth,
            measurements=[creation_class(**self._get_measurement_kwargs())],
            sources=[AtlasSource(**self._get_source_kwargs())],
        ).create()

        if not is_success:
            self._handle_api_error(response)  # Raises an exception

        pk = response["measurements"][0]
        url = "{}/measurements/{}/".format(conf["ripe-ncc"]["endpoint"], pk)
        self.ok(
            "Looking good!  Your measurement was created and details about "
            "it can be found here:\n\n  {}".format(url)
        )

        if not self.arguments.no_report:
            self.ok("Connecting to stream...")
            try:
                Stream(capture_limit=self.arguments.probes).stream(
                    self.arguments.type, pk)
            except (KeyboardInterrupt, CaptureLimitExceeded):
                pass  # User said stop, so we fall through to the finally block.
            finally:
                self.ok("Disconnecting from stream\n\nYou can find details "
                        "about this measurement here:\n\n  {}".format(url))

    def clean_target(self):

        # DNS measurements are a special case for targets
        if self.arguments.type == "dns":
            if self.arguments.use_probe_resolver:
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

    def clean_protocol(self):

        spec = conf["specification"]["types"]

        # DNS measurements only allow udp/tcp
        if self.arguments.type == "dns":
            if not self.arguments.protocol:
                self.arguments.protocol = spec["dns"]["protocol"]
            if self.arguments.protocol not in ("UDP", "TCP"):
                raise RipeAtlasToolsException(
                    "DNS measurements may only choose a protocol of UDP or TCP"
                )

        # Traceroute allows icmp/udp/tcp
        elif self.arguments.type == "traceroute":
            if not self.arguments.protocol:
                self.arguments.protocol = spec["traceroute"]["protocol"]
            if self.arguments.protocol not in ("ICMP", "UDP", "TCP"):
                raise RipeAtlasToolsException(
                    "Traceroute measurements may only choose a protocol of "
                    "ICMP, UDP or TCP"
                )

        return self.arguments.protocol

    def clean_shared_option(self, kind, argument):
        """
        Some options, like --protocol, are shared across types, and the defaults
        for those types can differ.  This is where we set these options to their
        appropriate default value.
        """
        r = getattr(self.arguments, argument)
        if not getattr(self.arguments, argument):
            r = conf["specification"]["types"][kind][argument.replace("_", "-")]
            setattr(self.arguments, argument, r)
        return r

    def _get_measurement_kwargs(self):

        target = self.clean_target()

        spec = conf["specification"]  # Shorter names are easier to read
        r = {
            "af": spec["af"],
            "description": spec["description"],
        }

        if self.arguments.af:
            r["af"] = self.arguments.af
        if self.arguments.description:
            r["description"] = self.arguments.description

        r["is_oneoff"] = True
        if self.arguments.interval or spec["times"]["interval"]:
            r["is_oneoff"] = False
            r["interval"] = self.arguments.interval
            self.arguments.no_report = True
        elif not spec["times"]["one-off"]:
            raise RipeAtlasToolsException(
                "Your configuration file appears to be setup to not create "
                "one-offs, but also offers no interval value.  Without one of "
                "these, a measurement cannot be created."
            )

        if target:
            r["target"] = target

        if self.arguments.type == "ping":
            r["packets"] = self.clean_shared_option("ping", "packets")
            r["size"] = self.clean_shared_option("ping", "size")

        elif self.arguments.type == "traceroute":
            r["packets"] = self.clean_shared_option("traceroute", "packets")
            r["size"] = self.clean_shared_option("traceroute", "size")
            r["protocol"] = self.clean_protocol()
            r["timeout"] = self.arguments.timeout

        elif self.arguments.type == "dns":
            for opt in ("class", "type", "argument"):
                if not getattr(self.arguments, "query_{}".format(opt)):
                    raise RipeAtlasToolsException(
                        "DNS measurements require a query type, class, and "
                        "argument"
                    )
            r["protocol"] = self.clean_protocol()
            r["query_class"] = self.arguments.query_class
            r["query_type"] = self.arguments.query_type
            r["query_argument"] = self.arguments.query_argument
            r["use_probe_resolver"] = self.arguments.use_probe_resolver
            r["udp_payload_size"] = self.arguments.udp_payload_size

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
            r["value"] = self.arguments.from_probes
        elif self.arguments.from_measurement:
            r["type"] = "msm"
            r["value"] = self.arguments.from_measurement

        return r

    @staticmethod
    def _handle_api_error(response):

        if "HTTP_MSG" in response:

            message = "There was a problem communicating with the RIPE Atlas " \
                      "infrastructure.  The message given was:\n\n  {}".format(
                      response["HTTP_MSG"])

            try:
                message += "\n  " + json.loads(
                    response["ADDITIONAL_MSG"])["error"]["message"]
            except Exception:
                pass  # Too many things can go wrong here and we don't care

            raise RipeAtlasToolsException(message)

        raise RipeAtlasToolsException(
            "There was a problem found in the attempt to create your "
            "measurement.  Please send the command you tried to execute "
            "to atlas@ripe.net and we'll try to address it."
        )
