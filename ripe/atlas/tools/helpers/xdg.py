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

import platform
import re
import os
import os.path


def get_config_home():
    """ """
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home is None:
        config_home = os.path.expanduser("~/.config")
    return os.path.join(config_home, "ripe-atlas-tools")


if hasattr(platform, "freedesktop_os_release"):
    freedesktop_os_release = platform.freedesktop_os_release
else:
    # Shim for Python versions < 3.10, taken from CPython

    # freedesktop.org os-release standard
    # https://www.freedesktop.org/software/systemd/man/os-release.html

    # NAME=value with optional quotes (' or "). The regular expression is less
    # strict than shell lexer, but that's ok.
    _os_release_line = re.compile(
        "^(?P<name>[a-zA-Z0-9_]+)=(?P<quote>[\"']?)(?P<value>.*)(?P=quote)$"
    )
    # unescape five special characters mentioned in the standard
    _os_release_unescape = re.compile(r"\\([\\\$\"\'`])")
    # /etc takes precedence over /usr/lib
    _os_release_candidates = ("/etc/os-release", "/usr/lib/os-release")
    _os_release_cache = None

    def _parse_os_release(lines):
        # These fields are mandatory fields with well-known defaults
        # in practice all Linux distributions override NAME, ID, and PRETTY_NAME.
        info = {
            "NAME": "Linux",
            "ID": "linux",
            "PRETTY_NAME": "Linux",
        }

        for line in lines:
            mo = _os_release_line.match(line)
            if mo is not None:
                info[mo.group("name")] = _os_release_unescape.sub(
                    r"\1", mo.group("value")
                )

        return info

    def freedesktop_os_release():
        """Return operation system identification from freedesktop.org os-release"""
        global _os_release_cache

        if _os_release_cache is None:
            errno = None
            for candidate in _os_release_candidates:
                try:
                    with open(candidate, encoding="utf-8") as f:
                        _os_release_cache = _parse_os_release(f)
                    break
                except OSError as e:
                    errno = e.errno
            else:
                raise OSError(
                    errno, f"Unable to read files {', '.join(_os_release_candidates)}"
                )

        return _os_release_cache.copy()


def get_os_string():
    os = platform.system()

    if os == 'Darwin':
        release = platform.mac_ver()[0]
        return f'macOS {release}'
    elif os == 'Windows':
        release = platform.win32_ver()[0]
        return f"Windows {release}"
        pass
    else:
        try:
            info = freedesktop_os_release()
        except OSError:
            pass
        else:
            name = info.get("NAME")
            if name:
                version = info.get("VERSION_ID", "")
                return f"{name} {version}"
    return platform.platform()
