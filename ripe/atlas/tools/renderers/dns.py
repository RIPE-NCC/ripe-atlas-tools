from tzlocal import get_localzone
from ..helpers.colours import colourise
from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_DNS]
    TIME_FORMAT = "%a %b %d %H:%M:%S %Z %Y"

    def on_result(self, result):

        created = result.created.astimezone(get_localzone())
        probe_id = result.probe_id

        r = "\n\nProbe #{0}\n{1}\n".format(probe_id, "=" * 79)
        if result.responses:
            for response in result.responses:
                r += self.get_formatted_response(probe_id, created, response)
        else:
            r += "\n  {}\n".format(colourise("No response found", "red"))

        return r

    @classmethod
    def get_formatted_response(cls, probe_id, created, response):

        if not response.abuf:
            return "\n- {0} -\n\n  No abuf found.\n".format(
                response.response_id)

        header_flags = []
        for flag in ("aa", "ad", "cd", "qr", "ra", "rd",):
            if getattr(response.abuf.header, flag):
                header_flags.append(flag)

        edns = ""
        if response.abuf.edns0:
            edns = "\n  ;; OPT PSEUDOSECTION:\n  ; EDNS: version: {0}, " \
                   "flags:; udp: {1}\n".format(
                       response.abuf.edns0.version,
                       response.abuf.edns0.udp_size
                   )

        question = ""
        if response.abuf.questions:
            question = response.abuf.questions[0].name

        return cls._colourise_by_response(response, cls.render(

            "reports/dns.txt",

            # Older measurements don't have a response_id
            response_id=response.response_id or 1,

            probe=probe_id,

            question_name=question,
            header_opcode=response.abuf.header.opcode,
            header_return_code=response.abuf.header.return_code,
            header_id=response.abuf.header.id,
            header_flags=" ".join(header_flags),
            edns=edns,

            question_count=len(response.abuf.questions),
            answer_count=len(response.abuf.answers),
            authority_count=len(response.abuf.authorities),
            additional_count=len(response.abuf.additionals),

            question=cls.get_section(
                "question", response.abuf.questions),
            answers=cls.get_section(
                "answer", response.abuf.answers),
            authorities=cls.get_section(
                "authority", response.abuf.authorities),
            additionals=cls.get_section(
                "additional", response.abuf.additionals),

            response_time=response.response_time,
            response_size=response.response_size,
            created=created.strftime(cls.TIME_FORMAT),
            destination_address=response.destination_address,

        ))

    @staticmethod
    def get_section(header, data):

        if not data:
            return ""

        return "\n  ;; {0} SECTION:\n{1}\n".format(
            header.upper(),
            "\n".join(["  {0}".format(_) for _ in data])
        )

    @staticmethod
    def _colourise_by_response(response, output):
        colour = "red" if response.is_error else "green"
        return colourise(output, colour)
