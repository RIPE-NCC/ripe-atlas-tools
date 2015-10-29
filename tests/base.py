import sys

from contextlib import contextmanager
try:
    from cStringIO import StringIO
except ImportError:  # Python 3
    from io import StringIO

@contextmanager
def capture_sys_output():
    """
    Wrap a block with this, and it'll capture standard out and standard error
    into handy variables:

      with capture_sys_output() as (stdout, stderr):
          self.cmd.run()

    More info: https://stackoverflow.com/questions/18651705/
    """

    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err
