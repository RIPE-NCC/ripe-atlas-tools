from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_HTTP]

    @classmethod
    def format(cls, result, probes=None):
        print("Not ready yet\n")
