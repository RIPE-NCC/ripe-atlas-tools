# Copyright (c) 2016 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ..helpers.sanitisers import sanitise
from .base import Renderer as BaseRenderer

THRESHOLD = 80  # %


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_SSLCERT]

    def __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)
        self.uniqcerts = {}
        self.blob_list = []

    def additional(self, results):
        self.gather_unique_certs(results)
        most_seen_cert = self.get_nprobes_ofpopular_cert()
        for cert_id in sorted(
            self.uniqcerts,
            key=lambda pk: self.uniqcerts[pk]["cnt"],
            reverse=True
        ):
            self.blob_list.append(self.render_certificate(cert_id))
            if self.uniqcerts[cert_id]["cnt"] < most_seen_cert * THRESHOLD / 100:
                self.blob_list.extend(self.render_below_threshold(cert_id))

        return "\n".join(self.blob_list)

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

        return self.render(
            "reports/ssl_consistency.txt",
            issuer_c=sanitise(certificate.issuer_c),
            issuer_o=sanitise(certificate.issuer_o),
            issuer_cn=sanitise(certificate.issuer_cn),
            subject_c=sanitise(certificate.subject_c),
            subject_o=sanitise(certificate.subject_o),
            subject_cn=sanitise(certificate.subject_cn),
            sha256fp=certificate.checksum_sha256,
            seenby=self.uniqcerts[cert_id]["cnt"],
            s="s" if self.uniqcerts[cert_id]["cnt"] > 1 else ""
        )

    def render_below_threshold(self, cert_id):
        """
        Print information about the given cert that is below our threshold
        of visibility.
        """
        blob_list = [
            "  Below the threshold ({0}%)".format(THRESHOLD),
            "  Probes that saw it: ",
        ]

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
