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
