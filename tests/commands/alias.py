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

import copy
import unittest

# Python 3.4+ comes with mock in unittest
try:
    from unittest import mock
except ImportError:
    import mock

from ripe.atlas.tools.commands.alias import Command
from ripe.atlas.tools.exceptions import RipeAtlasToolsException
from ripe.atlas.tools.settings import AliasesDB

from ..base import capture_sys_output


class FakeAliasesDB(AliasesDB):

    @staticmethod
    def write(aliases):
        pass

class TestAliasCommand(unittest.TestCase):

    ALIASES_PATH = "ripe.atlas.tools.commands.alias.aliases"
    ALIASES = {
        "measurement": {
            "msm1": 1
        },
        "probe": {
            "prb1": 1
        }
    }
    ALIASES_CLASS_PATH = "ripe.atlas.tools.commands.alias.AliasesDB"

    def setUp(self):
        self.cmd = Command()
        self.aliases = copy.deepcopy(TestAliasCommand.ALIASES)
        mock.patch(self.ALIASES_CLASS_PATH, FakeAliasesDB).start()

    def tearDown(self):
        mock.patch.stopall()

    def test_no_arguments(self):
        with capture_sys_output():
            with self.assertRaises(RipeAtlasToolsException) as e:
                self.cmd.init_args([])
                self.cmd.run()
            self.assertTrue(
                str(e.exception).startswith("Action not given."))

    def test_bad_action(self):
        with capture_sys_output():
            with self.assertRaises(SystemExit) as e:
                self.cmd.init_args(["test"])

    def test_bad_target_id(self):
        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit) as e:
                self.cmd.init_args("add probe a b".split())
            err = stderr.getvalue().split("\n")[-2]
        self.assertEqual(
            err,
            "Ripe-atlas alias add: error: argument target: invalid int value: 'a'"
        )

    def test_add_args(self):
        for alias_type in ("probe", "measurement"):
            with capture_sys_output() as (stdout, stderr):
                with self.assertRaises(SystemExit) as e:
                    cmd = Command()
                    cmd.init_args(["add", alias_type])

                with self.assertRaises(SystemExit) as e:
                    cmd = Command()
                    cmd.init_args(["add", alias_type, "1"])

                with self.assertRaises(SystemExit) as e:
                    cmd = Command()
                    cmd.init_args(["add", alias_type, "1", "1"])

                try:
                    cmd = Command()
                    cmd.init_args(["add", alias_type, "1", "one"])
                except Exception as e:
                    self.fail("Failed with {}".format(str(e)))

    def test_del_args(self):
        for alias_type in ("probe", "measurement"):
            with capture_sys_output() as (stdout, stderr):
                with self.assertRaises(SystemExit) as e:
                    cmd = Command()
                    cmd.init_args(["del", alias_type])

                with self.assertRaises(SystemExit) as e:
                    cmd = Command()
                    cmd.init_args(["del", alias_type, "1"])

                try:
                    cmd = Command()
                    cmd.init_args(["del", alias_type, "one"])
                except Exception as e:
                    self.fail("Failed with {}".format(str(e)))

    def test_bad_alias(self):
        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit) as e:
                self.cmd.init_args("add measurement 1 bad+alias".split())
            err = stderr.getvalue().split("\n")[-2]
        self.assertEqual(
            err,
            'Ripe-atlas alias add: error: argument alias: '
            '"bad+alias" does not appear to be a valid alias.'
        )

    def test_show_msm_ok(self):
        path = "ripe.atlas.tools.commands.alias.Command.ok"
        with mock.patch(path) as mock_ok:
            with mock.patch(self.ALIASES_PATH, self.aliases):
                self.cmd.init_args("show measurement msm1".split())
                self.cmd.run()
        mock_ok.assert_called_once()

    def test_show_msm_ko(self):
        path = "ripe.atlas.tools.commands.alias.Command.not_ok"
        with mock.patch(path) as mock_ko:
            with mock.patch(self.ALIASES_PATH, self.aliases):
                self.cmd.init_args("show measurement msm2".split())
                self.cmd.run()
        mock_ko.assert_called_once()

    def test_add_msm(self):
        with mock.patch(self.ALIASES_PATH, self.aliases):
            self.cmd.init_args("add measurement 2 msm2".split())
            self.cmd.run()
        self.assertTrue("msm2" in self.aliases["measurement"])
        self.assertEqual(
            self.aliases["measurement"]["msm2"],
            2
        )

    def test_del_msm(self):
        self.assertTrue("msm1" in self.aliases["measurement"])
        with mock.patch(self.ALIASES_PATH, self.aliases):
            self.cmd.init_args("del measurement msm1".split())
            self.cmd.run()
        self.assertFalse("msm1" in self.aliases["measurement"])

    def test_list(self):
        path = "ripe.atlas.tools.commands.alias.Command.ok"
        with mock.patch(path) as mock_ok:
            self.aliases["measurement"]["msm2"] = 2
            self.aliases["measurement"]["abc"] = 123
            with mock.patch(self.ALIASES_PATH, self.aliases):
                self.cmd.init_args("list measurement".split())
                self.cmd.run()
        mock_ok.assert_called_once_with(
            "Measurement aliases:\n\n- abc: 123\n- msm1: 1\n- msm2: 2\n"
        )
