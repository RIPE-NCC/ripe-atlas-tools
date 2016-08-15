import os.path
import unittest
import tempfile
import shutil
import sys

try:
    from unittest import mock  # Python 3.4+
except ImportError:
    import mock

# Python 2.7 does have io.StringIO but StringIO. is more liberal regarding str
# versus unicode inputs to write()
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from ripe.atlas.tools.commands.base import Command


USER_COMMAND = """
from ripe.atlas.tools.commands.base import Command as BaseCommand

class Command(BaseCommand):
    NAME = 'user-command-1'
"""


class TestCommandLoading(unittest.TestCase):
    expected_builtins = [
        "configure",
        "alias",
        "go",
        "measure",
        "measurement-info",
        "measurement-search",
        "probe-info",
        "probe-search",
        "report",
        "shibboleet",
        "stream",
    ]

    def setUp(self):
        # Create a directory for storing user commands and insert the dummy
        # command
        self.user_command_path = tempfile.mkdtemp()
        with open(
            os.path.join(self.user_command_path, "user_command_1.py"),
            "w"
        ) as f:
            f.write(USER_COMMAND)

    def tearDown(self):
        shutil.rmtree(self.user_command_path)

    @mock.patch(
        "ripe.atlas.tools.commands.base.Command._get_user_command_path",
        return_value=None,
    )
    def test_command_loading(self, _get_user_command_path):
        _get_user_command_path.return_value = self.user_command_path

        available_commands = Command.get_available_commands()

        # Check that we have the command list that we expect
        self.assertEquals(
            sorted(available_commands),
            sorted(
                [b.replace('-', '_') for b in self.expected_builtins] +
                ["user_command_1"]
            ),
        )

        # Check that we can load (i.e. import) every builtin command
        for expected_builtin in self.expected_builtins:
            self.assertIn(expected_builtin.replace("-", "_"), available_commands)
            cmd_cls = Command.load_command_class(expected_builtin)
            self.assertIsNotNone(cmd_cls)
            self.assertEquals(cmd_cls.get_name(), expected_builtin)

        # Check that we can load the user command
        user_cmd_cls = Command.load_command_class("user-command-1")
        self.assertIsNotNone(user_cmd_cls)
        self.assertEquals(user_cmd_cls.get_name(), "user-command-1")

        # Check that load_command_class() returns None for junk commands
        unexpected_cmd = Command.load_command_class("no-such-command")
        self.assertIsNone(unexpected_cmd)

    def test_deprecated_aliases(self):
        aliases = [
            ("measurement", "measurement-info"),
            ("measurements", "measurement-search"),
            ("probe", "probe-info"),
            ("probes", "probe-search"),
        ]

        # Check that each alias is loaded correctly and outputs a warning
        stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            for alias, cmd_name in aliases:
                sys.stderr.truncate()
                cmd_cls = Command.load_command_class(alias)
                self.assertIn(
                    "{} is a deprecated alias for {}".format(alias, cmd_name),
                    sys.stderr.getvalue(),
                )
                self.assertIsNotNone(cmd_cls)
                self.assertEquals(cmd_cls.get_name(), cmd_name)
        finally:
            sys.stderr = stderr
