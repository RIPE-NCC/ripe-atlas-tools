from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):
    """
    This is meant to be a stub example for what an aggregate renderer might look
    like.  If you have ideas as to how to make this better, feel free to send
    along a pull request.
    """

    RENDERS = [BaseRenderer.TYPE_PING]

    def __init__(self):
        self.totals = {
            "sent": 0,
            "received": 0
        }

    def on_start(self):
        return "Collecting results...\n"

    def on_result(self, result, probes=None):

        self.totals["sent"] += result.packets_sent
        self.totals["received"] += result.packets_received

        return ""

    def on_finish(self):
        return "\nTotals:\n  Sent: {sent}\n  Received: {received}\n".format(
            **self.totals
        )
