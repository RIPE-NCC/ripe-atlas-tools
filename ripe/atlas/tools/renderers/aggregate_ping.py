from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):
    """
    This is meant to be a stub example for what an aggregate renderer might look
    like.  If you have ideas as to how to make this better, feel free to send
    along a pull request.
    """

    RENDERS = [BaseRenderer.TYPE_PING]

    def __init__(self):
        self.target = ""
        self.packet_loss = 0
        self.totals = {
            "sent": 0,
            "received": 0,
            "min": [],
            "rtts": [],
            "max": []
        }

    @staticmethod
    def mean(rtts):
        return round(float(sum(rtt for rtt in rtts if rtt is not None))/max(len(rtts),1), 3)

    @staticmethod
    def median(rtts):
        sorted_rtts = sorted(rtts)
        index = (len(rtts) - 1) // 2
        if (len(rtts) % 2):
            return sorted_rtts[index]
        else:
            return (sorted_rtts[index] + sorted_rtts[index +1])/2.0

    def on_start(self):
        return "Collecting results...\n"

    def on_result(self, result):
        # destination_name is included in every ping result
        # but not exposed to on_start, on_finish via msm metadata
        # set it only if it was empty
        if self.target == "":
            self.target = result.destination_name
        self.totals["sent"] += result.packets_sent
        self.totals["received"] += result.packets_received
        self.totals["min"].append(result.rtt_min)
        self.totals["max"].append(result.rtt_max)

        for packet in result.packets:
            self.totals["rtts"].append(packet.rtt)

        return ""

    def on_finish(self):
        self.packet_loss = (1 - float(self.totals["received"]) / self.totals["sent"]) * 100
        return self.render(
            "reports/aggregate_ping.txt",
            target=self.target,
            sent=self.totals["sent"],
            received=self.totals["received"],
            packet_loss=self.packet_loss,
            min=min(min for min in self.totals["min"] if min is not None),
            median=self.median(self.totals["rtts"]),
            mean=self.mean(self.totals["rtts"]),
            max=max(self.totals["max"])
        )
