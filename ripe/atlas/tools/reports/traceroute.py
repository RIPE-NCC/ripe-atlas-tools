from .base import Report


class TracerouteReport(Report):

    @classmethod
    def format(cls, result, probes=None):

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

        return "\nProbe #{0}\n\n{1}".format(result.probe_id, r)
