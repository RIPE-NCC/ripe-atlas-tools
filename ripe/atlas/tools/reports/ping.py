import json

from .base import Report


class PingReport(Report):

    @classmethod
    def format(cls, result, probes=None):

        packets = result.packets

        if not packets:
            return json.dumps(result.raw_data) + "\n"

        return "{0} bytes from probe #{1:<5} {2:15} to {3} ({4}): ttl={5} times:{6}\n".format(
            result.packet_size,
            result.probe_id,
            packets[0].source_address,
            result.destination_name,
            result.destination_address,
            packets[0].ttl,
            " ".join(["{:8}".format(str(_.rtt) + ",") for _ in packets])
        )
