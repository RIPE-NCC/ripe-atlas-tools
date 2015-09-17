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

            r += "{:>3} {:15} {}ms\n".format(
                hop.index,
                name,
                "ms  ".join(["{:8}".format(rtt) for rtt in rtts])
            )

        return "\nProbe #{}\n\n{}".format(result.probe_id, r)
