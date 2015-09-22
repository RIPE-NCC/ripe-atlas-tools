from __future__ import print_function

import json

from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [
        BaseRenderer.TYPE_PING,
        BaseRenderer.TYPE_TRACEROUTE,
        BaseRenderer.TYPE_DNS,
        BaseRenderer.TYPE_TLS,
        BaseRenderer.TYPE_HTTP,
        BaseRenderer.TYPE_NTP
    ]

    @classmethod
    def format(cls, result, probes=None):
        if not probes or result.probe_id in probes:
            return json.dumps(result.raw_data, separators=(",", ":")) + "\n"
