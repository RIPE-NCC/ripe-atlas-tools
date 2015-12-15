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

from sphinx.application import Sphinx


class DocTest(unittest.TestCase):

    SOURCE_DIR = "docs"
    CONFIG_DIR = "docs"
    OUTPUT_DIR = "docs/build"
    DOCTREE_DIR = "docs/build/doctrees"

    def test_html_documentation(self):
        Sphinx(
            self.SOURCE_DIR,
            self.CONFIG_DIR,
            self.OUTPUT_DIR,
            self.DOCTREE_DIR,
            buildername="html",
            warningiserror=True,
        ).build(force_all=True)

    def test_text_documentation(self):
        Sphinx(
            self.SOURCE_DIR,
            self.CONFIG_DIR,
            self.OUTPUT_DIR,
            self.DOCTREE_DIR,
            buildername="text",
            warningiserror=True,
        ).build(force_all=True)
