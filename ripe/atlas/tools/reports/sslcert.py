from .base import Report


class SslcertReport(Report):
    """
    Somehow, we need to figure out how to make an SSL result look like the the
    output from `openssl x509 -in w00t -noout -text`.
    """

    @classmethod
    def format(cls, result, probes=None):
        r = ""
        for certificate in result.certificates:
            r += cls.get_formatted_response(certificate)
        return "\nProbe #{0}\n{1}\n".format(result.probe_id, r)

    @classmethod
    def get_formatted_response(cls, certificate):
        return cls.render(
            "reports/sslcert.txt",
            issuer_c=certificate.issuer_c,
            issuer_o=certificate.issuer_o,
            issuer_cn=certificate.issuer_cn,
            not_before=certificate.valid_from,
            not_after=certificate.valid_until,
            subject_c=certificate.subject_c,
            subject_o=certificate.subject_o,
            subject_cn=certificate.subject_cn
        )
