import unittest

from ripe.atlas.tools.helpers.sanitisers import sanitise


class TestSanitisersHelper(unittest.TestCase):

    def test_sanitise(self):

        self.assertEqual("clean", sanitise("clean"))
        for i in list(range(0, 32)) + [127]:
            self.assertEqual("unclean", sanitise("unclean" + chr(i)))

        self.assertEqual(None, sanitise(None))
        self.assertEqual(7, sanitise(7))

    def test_sanitise_with_newline_exception(self):
        self.assertEqual(
            "unc\nlean", sanitise("unc\nlean", strip_newlines=False))
        for i in set(list(range(0, 32)) + [127]).difference({10}):
            self.assertEqual(
                "unc\nlean",
                sanitise("unc\nlean" + chr(i), strip_newlines=False)
            )
