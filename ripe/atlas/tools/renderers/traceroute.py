from .base import Renderer as BaseRenderer
from .base import Result

from ..helpers.colours import colourise


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_TRACEROUTE]

    def on_result(self, result):

        r = ""

        for hop in result.hops:

            if hop.is_error:
                r += "{}\n".format(colourise(hop.error_message, "red"))
                continue

            name = ""
            rtts = []
            for packet in hop.packets:
                name = name or packet.origin or "*"
                if packet.rtt:
                    rtts.append("{:8} ms".format(packet.rtt))
                else:
                    rtts.append("          *")

            r += "{:>3} {:39} {}\n".format(
                hop.index,
                name,
                "  ".join(rtts)
            )

        return Result(
            "\n{}\n\n{}".format(
                colourise("Probe #{}".format(result.probe_id), "bold"),
                r
            ),
            result.probe_id
        )
