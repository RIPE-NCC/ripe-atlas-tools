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

import sys

from contextlib import contextmanager
try:
    from cStringIO import StringIO
except ImportError:  # Python 3
    from io import StringIO


class FakeTTY(object):
    """
    Basic simulation of a user terminal.
    """
    def __init__(self, file_obj):
        self.file_obj = file_obj

    def __getattr__(self, name):
        return getattr(self.file_obj, name)

    def isatty(self):
        return True


@contextmanager
def capture_sys_output(use_fake_tty=False):
    """
    Wrap a block with this, and it'll capture standard out and standard error
    into handy variables:

      with capture_sys_output() as (stdout, stderr):
          self.cmd.run()

    More info: https://stackoverflow.com/questions/18651705/
    """

    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    current_in = sys.stdin
    try:
        if use_fake_tty:
            sys.stdin = FakeTTY(current_in)
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err
        sys.stdin = current_in
