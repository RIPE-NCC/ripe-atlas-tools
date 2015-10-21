import sys

try:
    from unittest import mock
except ImportError:
    import mock

import unittest
from collections import namedtuple

from ripe.atlas.tools.commands.measurements import Command


class FakeGen(object):
    """
    A rip-off of the code used for testing probes, but a little prettier.
    """

    Measurement = namedtuple(
        "Measurement",
        ("id", "type", "status", "status_id", "meta_data", "destination_name")
    )

    def __init__(self):
        self.data = [
            self.Measurement(id=1, type="ping", status="Ongoing", status_id=2, meta_data={"status": {"name": "Ongoing", "id": 2}}, destination_name="Name 1",),
            self.Measurement(id=2, type="ping", status="Ongoing", status_id=2, meta_data={"status": {"name": "Ongoing", "id": 2}}, destination_name="Name 2",),
            self.Measurement(id=3, type="ping", status="Ongoing", status_id=2, meta_data={"status": {"name": "Ongoing", "id": 2}}, destination_name="Name 3",),
            self.Measurement(id=4, type="ping", status="Ongoing", status_id=2, meta_data={"status": {"name": "Ongoing", "id": 2}}, destination_name="Name 4",),
            self.Measurement(id=5, type="ping", status="Ongoing", status_id=2, meta_data={"status": {"name": "Ongoing", "id": 2}}, destination_name="Name 5",),
        ]
        self.total_count = 5

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if not self.data:
            raise StopIteration()
        else:
            return self.data.pop(0)


class TestMeasurementsCommand(unittest.TestCase):

    def setUp(self):
        self.cmd = Command()

    @mock.patch("ripe.atlas.tools.commands.measurements.MeasurementRequest")
    def test_with_empty_args(self, mock_request):
        mock_request.return_value = FakeGen()
        self.cmd.init_args([])
        self.cmd.run()
