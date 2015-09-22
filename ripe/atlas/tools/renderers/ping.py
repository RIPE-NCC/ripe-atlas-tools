from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_PING]

    def on_result(self, result, probes=None):

        packets = result.packets

        if not packets:
            return "No packets found"

        return "{0} bytes from probe #{1:<5} {2:15} to {3} ({4}): ttl={5} times:{6}\n".format(
            result.packet_size,
            result.probe_id,
            packets[0].source_address,
            result.destination_name,
            result.destination_address,
            packets[0].ttl,
            " ".join(["{:8}".format(str(_.rtt) + ",") for _ in packets])
        )
