from tzlocal import get_localzone
from .base import Report


class DnsReport(Report):

    TIME_FORMAT = "%a %b %d %H:%M:%S %Z %Y"

    def format(self, result):

        # We're not currently handling multiple responses because it's hard
        response = result.responses[0]
        created = result.created.astimezone(get_localzone())

        flags = []
        for flag in ("aa", "ad", "cd", "qr", "ra", "rd",):
            if getattr(response.abuf.header, flag):
                flags.append(flag)

        return self.render(

            "reports/dns.txt",

            probe=result.probe_id,

            flags=" ".join(flags),

            question_count=len(response.abuf.questions),
            answer_count=len(response.abuf.answers),
            authority_count=len(response.abuf.authorities),
            additional_count=len(response.abuf.additionals),

            question=self.get_section(
                "question", response.abuf.questions),
            answers=self.get_section(
                "answer", response.abuf.answers),
            authorities=self.get_section(
                "authority", response.abuf.authorities),
            additionals=self.get_section(
                "additional", response.abuf.additionals),

            response_time=response.response_time,
            response_size=response.response_size,
            created=created.strftime(self.TIME_FORMAT)

        )

    @staticmethod
    def get_section(header, data):

        if not data:
            return ""

        return "\n\n;; {} SECTION:\n".format(
            header.upper()) + "\n".join([str(_) for _ in data]) + "\n"
