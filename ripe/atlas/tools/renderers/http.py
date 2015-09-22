from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_HTTP]

    def on_result(self, result, probes=None):
        print("Not ready yet\n")
