#!/usr/bin/env python
"""
Compare the CLI measure command options with the fields, limits and defaults
from the API via a call to the OpenAPI (swagger) URL.
"""
from __future__ import print_function

import requests

from ripe.atlas.tools.commands.base import Command

openapi_url = "https://atlas.ripe.net/docs/api/v2/reference/api-docs/api/v2/measurements"

types = [
    ("ping", "Writeping measurement"),
    ("traceroute", "Writetraceroute measurement"),
    ("dns", "WriteDNS measurement"),
    ("sslcert", "SSL cert measurement"),
    ("http", "HTTP measurement"),
    ("ntp", "NTP measurement"),
]

# These are the expected differences from the OpenAPI spec.
# If somethign is defined here it means that an option deliberately has a
# different default, valid range or is not included in the CLI tools.
# e.g. if we want the tools to behave more like their common unix counterparts
# or it makes sense to express things differently on a command-line

common_differences = {
    "is_oneoff": None,  # implied by lack of --interval
    "type": None,  # set as the subcommand
    "start_time": None,  # deliberately unsupported
    "stop_time": None,  # deliberately unsupported
    "is_public": None,  # deliberately unsupported
    "description": {
        "default": "",
    },
    "interval": {
        "default": None,
    },
    "resolve_on_probe": None,  # Not sent explicitly to preserve behaviour
}

type_expected_differences = {
    "ping": dict(common_differences, **{
        "packet_interval": {
            "default": 1000,
        },
        "size": {
            "default": 48,
        },
        "skip_dns_check": None,
    }),
    "traceroute": dict(common_differences, **{
        "max_hops": {
            "default": 255,
        },
        "protocol": {
            "default": "ICMP",
        },
        "skip_dns_check": None,
        "paris": {
            "default": 0,
        },
        "dont_fragment": {
            "default": False,
        },
        "response_timeout": {
            "default": None,
        }
    }),
    "dns": dict(common_differences, **{
        "protocol": {
            "default": "UDP",
        },
        "query_class": {
            "default": "IN",
        },
        "query_type": {
            "default": "A",
        },
        "skip_dns_check": None,
        "set_rd_bit": {
            "default": True,
        },
        "use_probe_resolver": None,  # Implied by missing target
        "include_abuf": None,
        "include_qbuf": None,
        "prepend_probe_id": None,
        "use_macros": None,
    }),
    "sslcert": common_differences.copy(),
    "http": dict(common_differences, **{
        "extended_timing": None,  # "timing_verbosity"
        "more_extended_timing": None,  # "timing_verbosity"
        "max_bytes_read": {
            "alias": "body_bytes",
        },
        "path": {
            "default": "/",
        }
    }),
    "ntp": common_differences.copy(),
}


def compare_type(cmd_name, api_model, expected_differences):
    print(cmd_name)
    cmd = Command.load_command_class("measure")(["measure", cmd_name]).create()
    cmd.add_arguments()

    args = {}

    for arg in cmd.parser._actions:
        args[arg.dest] = arg

    seen_diffs = False

    for field_name, model_field in sorted(api_model["properties"].items()):
        if field_name in expected_differences and expected_differences[field_name] is None:
            continue
        if model_field["readOnly"]:
            continue

        explicit_values = expected_differences.get(field_name, {})

        opt_name = explicit_values.get("alias", field_name)

        if opt_name in args:
            cmd_field = args.get(opt_name)

            expected_default = explicit_values.get("default", model_field.get("defaultValue"))
            if cmd_field.default != expected_default:
                print("\t", field_name, "DEFAULT", repr(cmd_field.default), repr(expected_default))
                seen_diffs |= True

            expected_min = explicit_values.get("minimum", model_field.get("minimum"))
            cmd_min = getattr(cmd_field.type, "minimum", None)
            if cmd_min != expected_min:
                print("\t", field_name, "MINIMUM", cmd_min, expected_min)
                seen_diffs |= True

            expected_max = explicit_values.get("maximum", model_field.get("maximum"))
            cmd_max = getattr(cmd_field.type, "maximum", None)
            if cmd_max != expected_max:
                print("\t", field_name, "MAXIMUM", cmd_max, expected_max)
                seen_diffs |= True
        else:
            print("\t", field_name, "\t", "MISSING")
            seen_diffs |= True

    if not seen_diffs:
        print("\t", "OK")


if __name__ == "__main__":
    api_spec = requests.get(openapi_url).json()

    for cmd_name, api_name in types:
        compare_type(
            cmd_name,
            api_spec["models"][api_name],
            type_expected_differences[cmd_name]
        )
