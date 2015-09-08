from .base import Report


class TracerouteReport(Report):

    @staticmethod
    def format(result):

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
                "ms  ".join(["{:6}".format(rtt) for rtt in rtts])
            )

        return r
