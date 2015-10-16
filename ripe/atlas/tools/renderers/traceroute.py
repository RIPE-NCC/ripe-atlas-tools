from .base import Renderer as BaseRenderer
from .base import Result


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_TRACEROUTE]

    def on_result(self, result):

        r = ""

        for hop in result.hops:

            name = ""
            rtts = []
            for packet in hop.packets:
                name = name or packet.origin
                rtts.append(packet.rtt)

            r += "{0:>3} {1:15} {2}ms\n".format(
                hop.index,
                name,
                "ms  ".join(["{0:8}".format(rtt) for rtt in rtts])
            )

        return Result(
            "\nProbe #{0}\n\n{1}".format(result.probe_id, r),
            result.probe_id
        )
