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

from collections.abc import Mapping
import copy
import os
import re
import yaml

from ..helpers import xdg


class UserSettingsParser(object):

    USER_CONFIG_DIR = xdg.get_config_home()

    USER_RC = None

    def get(self):
        r = copy.deepcopy(self.DEFAULT)
        if os.path.exists(self.USER_RC):
            with open(self.USER_RC) as y:
                custom = yaml.load(y, Loader=yaml.FullLoader)
                if custom:
                    r = self.deep_update(r, custom)
        return r

    @classmethod
    def deep_update(cls, d, u):
        """
        Updates a dictionary with another dictionary, only it goes deep.
        Stolen from http://stackoverflow.com/questions/3232943/
        """
        for k, v in u.items():
            if isinstance(v, Mapping):
                r = cls.deep_update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    @staticmethod
    def write(data):
        raise NotImplementedError()


class Configuration(UserSettingsParser):
    """
    A singleton configuration class that's smart enough to create a config
    out of defaults + yaml
    """

    USER_RC = os.path.join(UserSettingsParser.USER_CONFIG_DIR, "rc")

    DEFAULT = {
        "authorisation": {
            "fetch": "",
            "fetch_aliases": {},
            "create": "",
            "google_geocoding": "",
        },
        "specification": {
            "af": 4,
            "description": "",
            "source": {
                "type": "area",
                "value": "WW",
                "requested": 50,
            },
            "spread": None,
            "resolve_on_probe": None,
            "times": {
                "one-off": True,
                "interval": None,
                "start": None,
                "stop": None,
            },
            "types": {
                "ping": {
                    "packets": 3,
                    "packet-interval": 1000,
                    "size": 48,
                    "include_probe_id": None,
                },
                "traceroute": {
                    "packets": 3,
                    "size": 48,
                    "protocol": "ICMP",
                    "dont-fragment": False,
                    "paris": 0,
                    "first-hop": 1,
                    "max-hops": 255,
                    "port": 80,
                    "destination-option-size": None,
                    "hop-by-hop-option-size": None,
                    "timeout": 4000,
                    "response-timeout": None,
                    "duplicate-timeout": None,
                },
                "sslcert": {
                    "port": 443,
                    "hostname": None,
                },
                "ntp": {"packets": 3, "timeout": 4000},
                "dns": {
                    "set-cd-bit": False,
                    "set-do-bit": False,
                    "protocol": "UDP",
                    "query-class": "IN",
                    "query-type": "A",
                    "query-argument": None,
                    "set-nsid-bit": False,
                    "udp-payload-size": 512,
                    "set-rd-bit": True,
                    "retry": 0,
                    "timeout": None,
                    "tls": False,
                },
                "http": {
                    "header-bytes": 0,
                    "version": "1.1",
                    "method": "GET",
                    "port": 80,
                    "path": "/",
                    "query-string": None,
                    "user-agent": "RIPE Atlas: https://atlas.ripe.net/",
                    "body-bytes": None,
                    "timing-verbosity": 0,
                },
            },
            "tags": {
                "ipv4": {
                    "ping": {"include": [], "exclude": []},
                    "traceroute": {"include": [], "exclude": []},
                    "dns": {"include": [], "exclude": []},
                    "sslcert": {"include": [], "exclude": []},
                    "http": {"include": [], "exclude": []},
                    "ntp": {"include": [], "exclude": []},
                    "all": {"include": ["system-ipv4-works"], "exclude": []},
                },
                "ipv6": {
                    "ping": {"include": [], "exclude": []},
                    "traceroute": {"include": [], "exclude": []},
                    "dns": {"include": [], "exclude": []},
                    "sslcert": {"include": [], "exclude": []},
                    "http": {"include": [], "exclude": []},
                    "ntp": {"include": [], "exclude": []},
                    "all": {"include": ["system-ipv6-works"], "exclude": []},
                },
            },
        },
        "ripe-ncc": {
            "endpoint": "https://atlas.ripe.net",
            "stream-base-url": "https://atlas-stream.ripe.net",
            "version": 0,
        },
    }

    @staticmethod
    def write(config):
        """
        PyYaml is incapable of preserving comments, or even specifying them as
        an argument to `.dump()` (http://pyyaml.org/ticket/114), so we have to
        do some regex gymnastics here to make sure that the config file remains
        easy for n00bs to read.
        """

        template = os.path.join(os.path.dirname(__file__), "templates", "base.yaml")

        authorisation = re.compile("^authorisation:$", re.MULTILINE)
        tags = re.compile("^  tags:$", re.MULTILINE)
        specification = re.compile("^specification:$", re.MULTILINE)
        ripe = re.compile("^ripe-ncc:$", re.MULTILINE)

        with open(template) as t:
            payload = str(t.read()).format(
                payload=yaml.dump(config, default_flow_style=False)
            )
            payload = ripe.sub(
                "\n# Don't mess with these, or Bad Things may happen\n" "ripe-ncc:",
                payload,
            )
            payload = authorisation.sub("# Authorisation\n" "authorisation:", payload)
            payload = specification.sub(
                "\n# Measurement Creation\n" "specification:", payload
            )
            payload = tags.sub(
                "  # Tags added to probes selection\n" "  tags:", payload
            )

        with open(Configuration.USER_RC, "w") as rc:
            rc.write(payload)

    def get(self):
        d = super().get()
        d["website-url"] = d["ripe-ncc"]["endpoint"]
        d["api-server"] = d["ripe-ncc"]["endpoint"].replace("https://", "")
        d["stream-base-url"] = d["ripe-ncc"]["stream-base-url"]
        return d


class AliasesDB(UserSettingsParser):
    """
    A singleton class to manage user aliases
    """

    USER_RC = os.path.join(UserSettingsParser.USER_CONFIG_DIR, "aliases")

    DEFAULT = {"measurement": {}, "probe": {}}

    @staticmethod
    def write(aliases):
        if not os.path.exists(AliasesDB.USER_CONFIG_DIR):
            os.makedirs(AliasesDB.USER_CONFIG_DIR)

        payload = yaml.dump(aliases, default_flow_style=False)

        with open(AliasesDB.USER_RC, "w") as rc:
            rc.write(payload)


conf = Configuration().get()
aliases = AliasesDB().get()
