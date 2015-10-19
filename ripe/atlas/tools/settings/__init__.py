import collections
import os
import re
import yaml


class Configuration(object):
    """
    A singleton configuration class that's smart enough to create a config
    out of defaults + yaml
    """

    USER_CONFIG_DIR = os.path.join(
        os.environ["HOME"], ".config", "ripe-atlas-tools")
    USER_RC = os.path.join(USER_CONFIG_DIR, "rc")

    DEFAULT = {
        "authorisation": {
            "fetch": "",
            "create": "",
        },
        "smart-tags": {
            "af": {
                "6": {
                    "include": ["system-ipv6-works"],
                    "exclude": []
                },
                "4": {
                    "include": ["system-ipv4-works"],
                    "exclude": []
                }
            }
        },
        "specification": {
            "af": 4,
            "description": "",
            "source": {
                "type": "area",
                "value": "WW",
                "requested": 50,
            },
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
                    "size": 48
                },
                "traceroute": {
                    "packets": 3,
                    "size": 48,
                    "protocol": "ICMP",
                    "dontfrag": False,
                    "paris": 0,
                    "firsthop": 1,
                    "maxhops": 255,
                    "port": 80,
                    "destination-option-size": None,
                    "hop-by-hop-option-size": None,
                    "timeout": 4000
                },
                "ssl": {
                    "port": 443
                },
                "ntp": {
                    "packets": 3,
                    "timeout": 4000
                },
                "dns": {
                    "cd": False,
                    "do": False,
                    "protocol": "UDP",
                    "query-class": "IN",
                    "query-type": "A",
                    "query-argument": None,
                    "use-nsid": False,
                    "use-probe-resolver": False,
                    "udp-payload-size": 512,
                    "recursion-desired": True,
                    "retry": 0
                }
            }
        },
        "ripe-ncc": {
            "endpoint": "https://atlas.ripe.net",
            "version": 0,
        }
    }

    def get(self):
        r = self.DEFAULT.copy()
        if os.path.exists(self.USER_RC):
            with open(self.USER_RC) as y:
                custom = yaml.load(y)
                if custom:
                    r = self.deep_update(r, custom)
        return r

    @classmethod
    def deep_update(cls, d, u):
        """
        Updates a dictionary with another dictionary, only it goes deep.
        Stolen from http://stackoverflow.com/questions/3232943/
        """
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = cls.deep_update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    @staticmethod
    def write(config):
        """
        PyYaml is incapable of preserving comments, or even specifying them as
        an argument to `.dump()` (http://pyyaml.org/ticket/114), so we have to
        do some regex gymnastics here to make sure that the config file remains
        easy for n00bs to read.
        """

        template = os.path.join(
            os.path.dirname(__file__), "templates", "base.yaml")

        authorisation = re.compile("^authorisation:$", re.MULTILINE)
        smart_tags = re.compile("^smart-tags:$", re.MULTILINE)
        specification = re.compile("^specification:$", re.MULTILINE)
        ripe = re.compile("^ripe-ncc:$", re.MULTILINE)

        with open(template) as t:
            payload = ripe.sub(
                "\n# Don't mess with these, or Bad Things may happen\nripe-ncc:",
                authorisation.sub(
                    "# Authorisation\nauthorisation:",
                    specification.sub(
                        "\n# Measurement Creation\nspecification:",
                        smart_tags.sub(
                            "\n# Tags added to probes selection\nsmart-tags:",
                            t.read().format(
                                payload=yaml.dump(config, default_flow_style=False)
                            )
                        )
                    )
                )
            )

        with open(Configuration.USER_RC, "w") as rc:
            rc.write(payload)


conf = Configuration().get()
