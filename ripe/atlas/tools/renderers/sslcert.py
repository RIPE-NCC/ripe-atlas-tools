import OpenSSL

from ..helpers.sanitisers import sanitise
from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_SSLCERT]

    def on_result(self, result):
        r = ""
        for certificate in result.certificates:
            r += self.get_formatted_response(certificate)
        return "\nProbe #{0}\n{1}\n".format(result.probe_id, r)

    @classmethod
    def get_formatted_response(cls, certificate):
        x509 = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM,
            certificate.raw_data.replace("\\/", "/").replace("\n\n", "\n")
        )

        pkey_type = x509.get_pubkey().type()

        # TODO: to be improved
        if pkey_type == 6:
            pkey_type_descr = "rsaEncryption"
        else:
            pkey_type_descr = pkey_type

        return cls.render(
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
            sha256fp=certificate.checksum_sha256
        )
