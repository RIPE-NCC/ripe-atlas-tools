from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_NTP]

    def on_result(self, result, probes=None):
        print("Not ready yet\n")
