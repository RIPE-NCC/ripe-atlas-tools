# coding=utf-8

# Copyright (c) 2015 RIPE NCC
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

import unittest
from unittest import mock
from io import StringIO


from ripe.atlas.tools.commands import base
from ripe.atlas.tools.version import __version__


class TestBaseCommand(unittest.TestCase):
    SAMPLE_PLATFORM = "Linux-5.4.0-91-generic-x86_64-with-glibc2.29"

    @mock.patch("ripe.atlas.tools.commands.base.open")
    def test_user_agent_configured(self, mock_open):
        tests = {
            "Some Cool User Agent String": "Some Cool User Agent String",
            "Some custom agent\nwith a second line": "Some custom agent",
            "x" * 3000: "x" * 128,
            "Πράκτορας χρήστη": "Πράκτορας χρήστη",
            "이것은 테스트 요원": "이것은 테스트 요원",
        }

        for contents, expected in tests.items():
            s = StringIO(contents)
            mock_open.return_value = s
            cmd = base.Command()
            self.assertEqual(cmd.user_agent, expected)

    @mock.patch("platform.system", return_value="Darwin")
    @mock.patch("platform.mac_ver", return_value=("11.6", ("", "", ""), "x86_64"))
    def test_user_agent_mac(self, *mocks):
        cmd = base.Command()
        self.assertEqual(cmd.user_agent, f"RIPE Atlas Tools [macOS 11.6] {__version__}")

    @mock.patch("platform.system", return_value="Windows")
    @mock.patch(
        "platform.win32_ver",
        return_value=("10", "10.0.10240", "", "Multiprocessor Free"),
    )
    def test_user_agent_windows(self, *mocks):
        cmd = base.Command()
        self.assertEqual(cmd.user_agent, f"RIPE Atlas Tools [Windows 10] {__version__}")

    @mock.patch("platform.system", return_value="Linux")
    @mock.patch(
        "ripe.atlas.tools.helpers.xdg.freedesktop_os_release",
        return_value={
            "NAME": "Debian GNU/Linux",
            "VERSION_ID": "10",
        },
    )
    def test_user_agent_xdg_present(self, *mocks):
        cmd = base.Command()
        self.assertEqual(
            cmd.user_agent, f"RIPE Atlas Tools [Debian GNU/Linux 10] {__version__}"
        )

    @mock.patch("platform.system", return_value="Linux")
    @mock.patch("platform.platform", return_value=SAMPLE_PLATFORM)
    @mock.patch(
        "ripe.atlas.tools.helpers.xdg.freedesktop_os_release", side_effect=OSError
    )
    def test_user_agent_xdg_absent(self, *mocks):
        cmd = base.Command()
        self.assertEqual(
            cmd.user_agent,
            f"RIPE Atlas Tools [{self.SAMPLE_PLATFORM}] {__version__}",
        )
