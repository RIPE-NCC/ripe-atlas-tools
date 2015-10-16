from .base import Renderer as BaseRenderer
from .base import Result


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_PING]

    def on_result(self, result):

        packets = result.packets

        if not packets:
            return "No packets found\n"

        # Because the origin value is more reliable as "from" in v4 and as
        # "packet.source_address" in v6.
        origin = result.origin
        if ":" in origin:
            origin = packets[0].source_address

        line = "{} bytes from probe #{:<5} {:15} to {} ({}): ttl={} times:{}\n"
        return Result(line.format(
            result.packet_size,
            result.probe_id,
            origin,
            result.destination_name,
            result.destination_address,
            packets[0].ttl,
            " ".join(["{:8}".format(str(_.rtt) + ",") for _ in packets])
        ), result.probe_id)
