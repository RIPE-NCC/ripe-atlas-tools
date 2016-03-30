import os
import unittest
import subprocess


class BashCompletionTests(unittest.TestCase):
    """
    Testing the Python level bash completion code.
    This requires setting up the environment as if we got passed data
    from bash.
    """

    def setUp(self):
        os.environ['RIPE_ATLAS_AUTO_COMPLETE'] = '1'

    def _setup_env(self, substring):
        input_str = "ripe-atlas" + substring
        os.environ['COMP_WORDS'] = input_str
        comp_cword = len(input_str.split(' ')) - 1  # Index of the last word
        os.environ['COMP_CWORD'] = str(comp_cword)

    def _autocomplete(self, substring):

        self._setup_env(substring)
        cmd_parts = "ripe-atlas" + substring
        envs = os.environ.copy()
        process = subprocess.Popen(
            cmd_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=envs, shell=True
        )
        output, error = process.communicate()
        return output.decode("utf-8"), error.decode("utf-8")

    def test_commands_completion(self):
        """Tests autocompletion of commands."""
        input_str = " "
        output, error = self._autocomplete(input_str)
        print(output, error)
        self.assertTrue("report" in output)

    def test_completion_disable(self):
        """
        Tests if autocompletion is disabled if environmental variable
        is not set.
        """
        input_str = " mea"
        del os.environ['RIPE_ATLAS_AUTO_COMPLETE']
        output, error = self._autocomplete(input_str)
        print(output, error)
        self.assertTrue("No such command" in error)

    def test_command_completion(self):
        """Tests autocompletion of specific command."""
        input_str = " meas"
        output, error = self._autocomplete(input_str)
        print(output, error)
        self.assertTrue("measure" in output)

    def test_options_completion(self):
        """Tests autocompletion of existing options for a command."""
        input_str = " measure "
        output, error = self._autocomplete(input_str)
        print(output, error)
        self.assertEqual(output, "dns http ntp ping sslcert traceroute")

    def test_option_completion(self):
        """Tests autocompletion of specific option of a command."""
        input_str = " measure ping --h"
        output, error = self._autocomplete(input_str)
        print(output, error)
        self.assertEqual(output, "--help")
