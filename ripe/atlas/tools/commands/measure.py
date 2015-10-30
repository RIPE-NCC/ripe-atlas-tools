from __future__ import print_function, absolute_import

import re

from ripe.atlas.cousteau import (
    Ping, Traceroute, Dns, Sslcert, Ntp, AtlasSource, AtlasCreateRequest)
from ripe.atlas.sagan.dns import Message

from ..exceptions import RipeAtlasToolsException
from ..helpers.colours import colourise
from ..helpers.validators import ArgumentType
from ..renderers import Renderer
from ..settings import conf
from ..streaming import Stream, CaptureLimitExceeded
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "measure"

    DESCRIPTION = "Create a measurement and optionally wait for the results"

    CREATION_CLASSES = {
        "ping": Ping,
        "traceroute": Traceroute,
        "dns": Dns,
        "ssl": Sslcert,
        "ntp": Ntp
    }

    def __init__(self, *args, **kwargs):
        BaseCommand.__init__(self, *args, **kwargs)
        self._is_oneoff = True

    def add_arguments(self):

        # Required

        self.parser.add_argument(
            "type",
            type=str,
            choices=self.CREATION_CLASSES.keys(),
            help="The type of measurement you want to create"
        )

        # Optional

        self.parser.add_argument(
            "--renderer",
            choices=Renderer.get_available(),
            help="The renderer you want to use. If this isn't defined, an "
                 "appropriate renderer will be selected."
        )
        self.parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not create the measurement, only show its definition."
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
            type=ArgumentType.ip_or_domain,
            help="The target, either a domain name or IP address.  If creating "
                 "a DNS measurement, the absence of this option will imply "
                 "that you wish to use the probe's resolver."
        )
        self.parser.add_argument(
            "--no-report",
            action="store_true",
            help="Don't wait for a response from the measurement, just return "
                 "the URL at which you can later get information about the "
                 "measurement."
        )

        self.parser.add_argument(
            "--interval",
            type=int,
            help="Rather than run this measurement as a one-off (the default), "
                 "create this measurement as a recurring one, with an interval "
                 "of n seconds between attempted measurements. This option "
                 "implies --no-report."
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
            type=ArgumentType.integer_range(1, 2**32),
            metavar="ASN",
            help="The ASN from which you'd like to select your probes. "
                 "Example: --from-asn=3333"
        )
        origins.add_argument(
            "--from-probes",
            type=ArgumentType.comma_separated_integers(minimum=1),
            metavar="PROBES",
            help="A comma-separated list of probe-ids you want to use in your "
                 "measurement. Example: --from-probes=1,2,34,157,10006"
        )
        origins.add_argument(
            "--from-measurement",
            type=ArgumentType.integer_range(minimum=1),
            metavar="MEASUREMENT_ID",
            help="A measurement id which you want to use as the basis for "
                 "probe selection in your new measurement.  This is a handy "
                 "way to re-create a measurement under conditions similar to "
                 "another measurement. Example: --from-measurement=1000192"
        )
        self.parser.add_argument(
            "--probes",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["source"]["requested"],
            help="The number of probes you want to use"
        )
        self.parser.add_argument(
            "--include-tag",
            type=ArgumentType.regex(r"^[a-z_\-]+$"),
            action="append",
            metavar="TAG",
            help="Include only probes that are marked with these tags. "
                 "Example: --include-tag=system-ipv6-works"
        )
        self.parser.add_argument(
            "--exclude-tag",
            type=ArgumentType.regex(r"^[a-z_\-]+$"),
            action="append",
            metavar="TAG",
            help="Exclude probes that are marked with these tags. "
                 "Example: --exclude-tag=system-ipv6-works"
        )

        # Type-specific

        ping_or_trace = self.parser.add_argument_group(
            "Ping and Traceroute Measurements")
        ping_or_trace.add_argument(
            "--packets",
            type=ArgumentType.integer_range(minimum=1),
            help="The number of packets sent"
        )
        ping_or_trace.add_argument(
            "--size",
            type=ArgumentType.integer_range(minimum=1),
            help="The size of packets sent"
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

        ping = self.parser.add_argument_group(
            "Ping Measurements")
        ping.add_argument(
            "--packet-interval",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["types"]["ping"]["packet-interval"],
        )

        traceroute = self.parser.add_argument_group(
            "Traceroute Measurements")
        traceroute.add_argument(
            "--timeout",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["types"]["traceroute"]["timeout"],
            help="The timeout per-packet"
        )
        traceroute.add_argument(
            "--dont-fragment",
            action="store_true",
            default=conf["specification"]["types"]["traceroute"]["dont-fragment"],
            help="Don't Fragment the packet"
        )
        traceroute.add_argument(
            "--paris",
            type=ArgumentType.integer_range(minimum=0, maximum=64),
            default=conf["specification"]["types"]["traceroute"]["paris"],
            help="Use Paris. Value must be between 0 and 64."
                 "If 0, a standard traceroute will be performed"
        )
        traceroute.add_argument(
            "--first-hop",
            type=ArgumentType.integer_range(minimum=1, maximum=255),
            default=conf["specification"]["types"]["traceroute"]["first-hop"],
            help="Value must be between 1 and 255"
        )
        traceroute.add_argument(
            "--max-hops",
            type=ArgumentType.integer_range(minimum=1, maximum=255),
            default=conf["specification"]["types"]["traceroute"]["max-hops"],
            help="Value must be between 1 and 255"
        )
        traceroute.add_argument(
            "--port",
            type=ArgumentType.integer_range(minimum=1, maximum=2**16),
            default=conf["specification"]["types"]["traceroute"]["port"],
            help="Destination port, valid for TCP only"
        )
        traceroute.add_argument(
            "--destination-option-size",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["types"]["traceroute"]["destination-option-size"],
            help="IPv6 destination option header"
        )
        traceroute.add_argument(
            "--hop-by-hop-option-size",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["types"]["traceroute"]["hop-by-hop-option-size"],
            help=" IPv6 hop by hop option header"
        )

        dns = self.parser.add_argument_group("DNS Measurements")
        dns.add_argument(
            "--query-class",
            type=str,
            choices=("IN", "CHAOS"),
            default=conf["specification"]["types"]["dns"]["query-class"],
            help='The query class.  The default is "{}"'.format(
                conf["specification"]["types"]["dns"]["query-class"]
            )
        )
        dns.add_argument(
            "--query-type",
            type=str,
            choices=list(Message.ANSWER_CLASSES.keys()) + ["ANY"],  # The only ones we can parse
            default=conf["specification"]["types"]["dns"]["query-type"],
            help='The query type.  The default is "{}"'.format(
                conf["specification"]["types"]["dns"]["query-type"]
            )
        )
        dns.add_argument(
            "--query-argument",
            type=str,
            default=conf["specification"]["types"]["dns"]["query-argument"],
            help="The DNS label to query"
        )
        dns.add_argument(
            "--set-cd-bit",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["set-cd-bit"],
            help="Set the DNSSEC Checking Disabled flag (RFC4035)"
        )
        dns.add_argument(
            "--set-do-bit",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["set-do-bit"],
            help="Set the DNSSEC OK flag (RFC3225)"
        )
        dns.add_argument(
            "--set-nsid-bit",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["set-nsid-bit"],
            help="Include an EDNS name server ID request with the query"
        )
        dns.add_argument(
            "--set-rd-bit",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["set-rd-bit"],
            help="Set the Recursion Desired flag"
        )
        dns.add_argument(
            "--retry",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["types"]["dns"]["retry"],
            help="Number of times to retry"
        )
        dns.add_argument(
            "--udp-payload-size",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["types"]["dns"]["udp-payload-size"],
            help="May be any integer between 512 and 4096 inclusive"
        )

    def run(self):

        if self.arguments.dry_run:
            return self.dry_run()

        is_success, response = self.create()

        if not is_success:
            self._handle_api_error(response)  # Raises an exception

        pk = response["measurements"][0]
        url = "{0}/measurements/{1}/".format(conf["ripe-ncc"]["endpoint"], pk)

        self.ok(
            "Looking good!  Your measurement was created and details about "
            "it can be found here:\n\n  {0}".format(url)
        )

        if not self.arguments.no_report:
            self.stream(pk, url)

    def dry_run(self):

        print(colourise("\nDefinitions:\n{}".format("=" * 80), "bold"))

        for param, val in self._get_measurement_kwargs().items():
            print(colourise("{:<25} {}".format(param, val), "cyan"))

        print(colourise("\nSources:\n{}".format("=" * 80), "bold"))

        for param, val in self._get_source_kwargs().items():
            if param == "tags":
                print(colourise("tags\n  include{}{}\n  exclude{}{}\n".format(
                    " " * 17,
                    ", ".join(val["include"]),
                    " " * 17,
                    ", ".join(val["exclude"])
                ), "cyan"))
                continue
            print(colourise("{:<25} {}".format(param, val), "cyan"))

    def create(self):
        creation_class = self.CREATION_CLASSES[self.arguments.type]

        return AtlasCreateRequest(
            server=conf["ripe-ncc"]["endpoint"].replace("https://", ""),
            key=self.arguments.auth,
            measurements=[creation_class(**self._get_measurement_kwargs())],
            sources=[AtlasSource(**self._get_source_kwargs())],
            is_oneoff=self._is_oneoff
        ).create()

    def stream(self, pk, url):
        self.ok("Connecting to stream...")
        try:
            Stream(capture_limit=self.arguments.probes, timeout=300).stream(
                self.arguments.renderer, self.arguments.type, pk)
        except (KeyboardInterrupt, CaptureLimitExceeded):
            pass  # User said stop, so we fall through to the finally block.
        finally:
            self.ok("Disconnecting from stream\n\nYou can find details "
                    "about this measurement here:\n\n  {0}".format(url))

    def clean_target(self):

        # DNS measurements are a special case for targets
        if self.arguments.type == "dns":
            return self.arguments.target

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

        # Everything else gets kicked
        else:
            raise RipeAtlasToolsException(
                "Measurements of type \"{}\" have no use for a protocol "
                "value.".format(self.arguments.type))

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
            "af": self._get_af(),
            "description": spec["description"],
        }

        if self.arguments.description:
            r["description"] = self.arguments.description

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

        if target:
            r["target"] = target

        if self.arguments.type == "ping":
            r["packets"] = self.clean_shared_option("ping", "packets")
            r["packet_interval"] = self.arguments.packet_interval
            r["size"] = self.clean_shared_option("ping", "size")

        elif self.arguments.type == "traceroute":
            r["destination_option_size"] = self.arguments.destination_option_size
            r["dont_fragment"] = self.arguments.dont_fragment
            r["first_hop"] = self.arguments.first_hop
            r["hop_by_hop_option_size"] = self.arguments.hop_by_hop_option_size
            r["max_hops"] = self.arguments.max_hops
            r["packets"] = self.clean_shared_option("traceroute", "packets")
            r["paris"] = self.arguments.paris
            r["port"] = self.arguments.port
            r["protocol"] = self.clean_protocol()
            r["size"] = self.clean_shared_option("traceroute", "size")
            r["timeout"] = self.arguments.timeout

        elif self.arguments.type == "dns":
            for opt in ("class", "type", "argument"):
                if not getattr(self.arguments, "query_{0}".format(opt)):
                    raise RipeAtlasToolsException(
                        "At a minimum, DNS measurements require a query "
                        "argument.")
            r["query_class"] = self.arguments.query_class
            r["query_type"] = self.arguments.query_type
            r["query_argument"] = self.arguments.query_argument
            r["set_cd_bit"] = self.arguments.set_cd_bit
            r["set_do_bit"] = self.arguments.set_do_bit
            r["set_rd_bit"] = self.arguments.set_rd_bit
            r["set_nsid_bit"] = self.arguments.set_nsid_bit
            r["protocol"] = self.clean_protocol()
            r["retry"] = self.arguments.retry
            r["udp_payload_size"] = self.arguments.udp_payload_size
            r["use_probe_resolver"] = not target

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
            "exclude": self.arguments.exclude_tag or []
        }

        af = "ipv{}".format(self._get_af())
        kind = self.arguments.type
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

    @staticmethod
    def _handle_api_error(response):

        error_detail = response

        if isinstance(response, dict) and "detail" in response:
            error_detail = response["detail"]

        message = (
            "There was a problem communicating with the RIPE Atlas "
            "infrastructure.  The message given was:\n\n  {}"
        ).format(error_detail)

        raise RipeAtlasToolsException(message)
