from .base import Renderer as BaseRenderer
from ripe.atlas.cousteau import ProbeRequest

THRESHOLD = 80 #%


class Renderer(BaseRenderer):
    RENDERS = [BaseRenderer.TYPE_TLS]

    def __init__(self):
        self.uniqcerts = {}

    def on_start(self):
        return "Collecting results...\n"

    def on_result(self, result, probes=None):
        probe_id = result.probe_id

        for certificate in result.certificates:
            cert_id = certificate.checksum_sha256
            if cert_id not in self.uniqcerts:
              self.uniqcerts[cert_id] = {
                "cert": None,
                "cnt": 0,
                "probes": []
              }
            self.uniqcerts[cert_id]["cert"] = certificate
            self.uniqcerts[cert_id]["cnt"] += 1
            self.uniqcerts[cert_id]["probes"].append(probe_id)
        return ""

    def on_finish(self):
        s = ""
        most_seen_cnt = max([self.uniqcerts[cert_id]["cnt"] for cert_id in self.uniqcerts])

        for cert_id in sorted(self.uniqcerts,
                              key=lambda id: self.uniqcerts[id]["cnt"],
                              reverse=True):
            certificate = self.uniqcerts[cert_id]["cert"]

            s += self.render(
                "reports/ssl_consistency.txt",
                issuer_c=certificate.issuer_c,
                issuer_o=certificate.issuer_o,
                issuer_cn=certificate.issuer_cn,
                subject_c=certificate.subject_c,
                subject_o=certificate.subject_o,
                subject_cn=certificate.subject_cn,
                sha256fp=certificate.checksum_sha256,
                seenby=self.uniqcerts[cert_id]["cnt"],
                s="s" if self.uniqcerts[cert_id]["cnt"] > 1 else "")

            #TODO: a better way to determine consistency?
            if self.uniqcerts[cert_id]["cnt"] < most_seen_cnt*THRESHOLD/100:
                s += "\n"
                s += "  Below the threshold ({0}%)\n".format(THRESHOLD)
                s += "  Probes that saw it: \n"

                probes_ids = ",".join(map(str, self.uniqcerts[cert_id]["probes"]))
                probes = ProbeRequest(id__in=probes_ids)

                for probe in probes:
                    s += "    ID: {id}, country code: {cc}, " \
                        "ASN (v4/v6): {asn4}/{asn6}\n".format(
                        id=probe["id"], cc=probe["country_code"],
                        asn4=probe["asn_v4"], asn6=probe["asn_v6"])

            s += "\n"

        return s
