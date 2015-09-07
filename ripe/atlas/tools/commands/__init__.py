import os
import pkgutil


def get_available_commands():
    """
    Get a list of commands that we can execute.  By default, we have a fixed
    that we make available in this directory, but the user can create her own
    plugins and store them at ~/.config/ripe-atlas-tools/commands/.  If we find
    any files there, we add them to the list here.
    """

    paths = [os.path.dirname(__file__)]
    if "HOME" in os.environ:
        paths += [os.path.join(
            os.environ["HOME"], ".config", "ripe-atlas-tools", "commands")]

    return [package_name for _, package_name, _ in pkgutil.iter_modules(paths)]
