from .base import Report


class SslcertReport(Report):
    """
    Somehow, we need to figure out how to make an SSL result look like the the
    output from `openssl x509 -in w00t -noout -text`.
    """

    @classmethod
    def format(cls, result, probes=None):
        res = "\n"
        for cert in result.certificates:
            res += "Certificate:\n"
            res += "    Issuer: C={c}, O={o}, CN={cn}\n".format(
                c=cert.issuer_c,
                o=cert.issuer_o,
                cn=cert.issuer_cn)
            res += "    Validity\n"
            res += "        Not Before: {nb}\n".format(
              nb=cert.valid_from)
            res += "        Not After : {na}\n".format(
              na=cert.valid_until)
            res += "    Subject: C={c}, O={o}, CN={cn}\n".format(
                c=cert.subject_c,
                o=cert.subject_o,
                cn=cert.subject_cn)

        return res
 
