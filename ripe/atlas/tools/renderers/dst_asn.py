from .base import Renderer as BaseRenderer
from collections import Counter

from ..ipdetails import IP


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_PING]

    SHOW_DEFAULT_HEADER = False
    SHOW_DEFAULT_FOOTER = False

    def __init__(self):
        self.asns = Counter()  # keys are timestamps, data struct captures ASN membership
        self.asn2name = {}

    def on_result(self, result):
        dst = result.destination_address
        if dst is not None:
            ip = IP(dst)
            if ip.asn:
                self.asns[ip.asn] += 1
                self.asn2name[ip.asn] = ip.holder
            else:
                self.asns['<unknown>'] += 1
                self.asn2name['<unknown>'] = 'unknown'
            return ""
        return ""

    def additional(self, results):
        total = sum(self.asns.values())
        for asn, count in self.asns.most_common():
            print "AS%s %.2f%% (%s)" % (
                asn,
                100.0 * count / total,
                self.asn2name[asn]
            )
