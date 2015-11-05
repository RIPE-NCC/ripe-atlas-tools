from .base import Renderer as BaseRenderer

THRESHOLD = 80  # %


class Renderer(BaseRenderer):
    RENDERS = [BaseRenderer.TYPE_SSLCERT]

    def __init__(self):
        self.uniqcerts = {}
        self.blob_list = []

    def additional(self, results):
        self.gather_unique_certs(results)
        most_seen_cert = self.get_nprobes_ofpopular_cert()
        for cert_id in sorted(
            self.uniqcerts,
            key=lambda id: self.uniqcerts[id]["cnt"],
            reverse=True
        ):
            self.blob_list.append(self.render_certificate(cert_id))
            if self.uniqcerts[cert_id]["cnt"] < most_seen_cert * THRESHOLD / 100:
                self.blob_list.extend(self.render_below_threshold(cert_id))

        print("\n".join(self.blob_list))

    def gather_unique_certs(self, results):
        for result in results:
            self.bucketize_result_cert(result)

    def bucketize_result_cert(self, result):
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
            self.uniqcerts[cert_id]["probes"].append(result.probe)

    def get_nprobes_ofpopular_cert(self):
        """
        Gets the number of probes that have seen the most popular
        (in terms of probes) cert.
        """
        return max(
            [self.uniqcerts[cert_id]["cnt"] for cert_id in self.uniqcerts]
        )

    def render_certificate(self, cert_id):
        """Renders the specific certificate"""
        certificate = self.uniqcerts[cert_id]["cert"]

        rstring = self.render(
            "reports/ssl_consistency.txt",
            issuer_c=certificate.issuer_c,
            issuer_o=certificate.issuer_o,
            issuer_cn=certificate.issuer_cn,
            subject_c=certificate.subject_c,
            subject_o=certificate.subject_o,
            subject_cn=certificate.subject_cn,
            sha256fp=certificate.checksum_sha256,
            seenby=self.uniqcerts[cert_id]["cnt"],
            s="s" if self.uniqcerts[cert_id]["cnt"] > 1 else ""
        )
        return rstring

    def render_below_threshold(self, cert_id):
        """
        Print information about the given cert that is below our threshold
        of visibility.
        """
        blob_list = []
        blob_list.append("  Below the threshold ({0}%)".format(THRESHOLD))
        blob_list.append("  Probes that saw it: ")

        for probe in self.uniqcerts[cert_id]["probes"]:
            log = (
                "    ID: {id}, country code: {cc}, ASN (v4/v6): {asn4}/{asn6}"
            ).format(
                id=probe.id, cc=probe.country_code,
                asn4=probe.asn_v4, asn6=probe.asn_v6
            )
            blob_list.append(log)

        return blob_list

    def on_result(self, result):
        return ""
