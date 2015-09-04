import os
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
            "create": "",
        },
        "create": {
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
        }
    }

    def get(self):
        r = self.DEFAULT.copy()
        if os.path.exists(self.USER_RC):
            with open(self.USER_RC) as y:
                custom = yaml.load(y)
                if custom:
                    r.update(custom)
        return r


conf = Configuration().get()
