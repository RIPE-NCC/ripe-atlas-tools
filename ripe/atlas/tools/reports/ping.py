import json

from .base import Report


class PingReport(Report):

    @staticmethod
    def format(result):

        packets = result.packets

        if not packets:
            return json.dumps(result.raw_data) + "\n"

        return "{} bytes from {:15} to {} ({}): ttl={} times:{}\n".format(
            result.packet_size,
            packets[0].source_address,
            result.destination_name,
            result.destination_address,
            packets[0].ttl,
            ", ".join(["{:7}".format(_.rtt) for _ in packets])
        )
