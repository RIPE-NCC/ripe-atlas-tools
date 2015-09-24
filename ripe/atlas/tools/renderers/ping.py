from .base import Renderer as BaseRenderer
from .base import Result


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_PING]

    def on_result(self, result, probes=None):

        packets = result.packets

        if not packets:
            return "No packets found"

        line = "{} bytes from probe #{:<5} {:15} to {} ({}): ttl={} times:{}\n"
        return Result(line.format(
            result.packet_size,
            result.probe_id,
            packets[0].source_address,
            result.destination_name,
            result.destination_address,
            packets[0].ttl,
            " ".join(["{:8}".format(str(_.rtt) + ",") for _ in packets])
        ), result.probe_id)
