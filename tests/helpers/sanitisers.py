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
