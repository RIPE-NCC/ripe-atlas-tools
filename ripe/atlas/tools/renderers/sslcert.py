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

from tzlocal import get_localzone
import OpenSSL

from ..helpers.colours import colourise
from ..helpers.sanitisers import sanitise
from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_SSLCERT]
    TIME_FORMAT = "%a %b %d %H:%M:%S %Z %Y"

    def on_result(self, result):
        r = ""
        for certificate in result.certificates:
            r += self.get_formatted_response(certificate)
        created = result.created.astimezone(get_localzone())
        return "\n{}\n{}\n{}\n".format(
            colourise("Probe #{}".format(result.probe_id), "bold"),
            colourise(created.strftime(self.TIME_FORMAT), "bold"),
            r,
        )

    @classmethod
    def get_formatted_response(cls, certificate):
        x509 = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM,
            certificate.raw_data.replace("\\/", "/").replace("\n\n", "\n"),
        )

        pkey_type = x509.get_pubkey().type()

        # TODO: to be improved
        if pkey_type == 6:
            pkey_type_descr = "rsaEncryption"
        else:
            pkey_type_descr = pkey_type

        return cls.render_template(
            "reports/sslcert.txt",
            issuer_c=sanitise(certificate.issuer_c),
            issuer_o=sanitise(certificate.issuer_o),
            issuer_cn=sanitise(certificate.issuer_cn),
            not_before=certificate.valid_from,
            not_after=certificate.valid_until,
            subject_c=sanitise(certificate.subject_c),
            subject_o=sanitise(certificate.subject_o),
            subject_cn=sanitise(certificate.subject_cn),
            version=x509.get_version(),
            serial_number=x509.get_serial_number(),
            signature_algorithm=x509.get_signature_algorithm(),
            pkey_type=pkey_type_descr,
            pkey_bits=x509.get_pubkey().bits(),
            sha1fp=certificate.checksum_sha1,
            sha256fp=certificate.checksum_sha256,
        )
