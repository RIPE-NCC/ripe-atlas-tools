import os
import re


def get_available_commands():
    """
    Get a list of commands that we can execute.  By default, we have a fixed
    that we make available in this directory, but the user can create her own
    plugins and store them at ~/.config/ripe-atlas-tools/commands/.  If we find
    any files there, we add them to the list here.
    """

    exclude = re.compile("^(__init__|base).pyc?$")
    files = os.listdir(os.path.dirname(__file__))

    # Standard modules
    r = [re.sub("\.pyc?$", "", _) for _ in files if not exclude.match(_)]

    if not "HOME" in os.environ:
        return r

    plugins = os.path.join(
        os.environ["HOME"], ".config", "ripe-atlas-tools", "commands")
    if os.path.exists(plugins):
        r += [re.sub("\.pyc?$", "", _) for _ in plugins if not exclude.match(_)]

    return r
