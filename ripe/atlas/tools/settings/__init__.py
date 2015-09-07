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
        "specification": {
            "description": "",
            "source": {
                "area": "WW",
                "probes": 50,
            },
            "is_oneoff": True,
            "types": {
                "packets": 3,
                "size": 48
            }
        },
        "version": 0,
    }

    def get(self):
        r = self.DEFAULT.copy()
        if os.path.exists(self.USER_RC):
            with open(self.USER_RC) as y:
                custom = yaml.load(y)
                if custom:
                    r.update(custom)
        return r

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
        specification = re.compile("^specification:$", re.MULTILINE)
        version = re.compile("^version:", re.MULTILINE)

        with open(template) as t:
            payload = version.sub(
                "\n# Don't mess with this, or Bad Things may happen\nversion:",
                authorisation.sub(
                    "# Authorisation\nauthorisation:",
                    specification.sub(
                        "\n# Measurement Creation\nspecification:",
                        t.read().format(
                            payload=yaml.dump(config, default_flow_style=False)
                        )
                    )
                )
            )

        with open(Configuration.USER_RC, "w") as rc:
            rc.write(payload)


conf = Configuration().get()
