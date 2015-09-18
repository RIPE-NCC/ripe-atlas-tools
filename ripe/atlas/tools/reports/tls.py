from .base import Report


class TlsReport(Report):
    """
    Somehow, we need to figure out how to make an SSL result look like the the
    output from `openssl x509 -in w00t -noout -text`.
    """

    @classmethod
    def format(cls, result, probes=None):
        print("Not ready yet\n")
