import json

from ripe.atlas.cousteau import ProbeRequest
from ripe.atlas.sagan import Result, ResultError

from ..cache import memoised
from .base import Aggregator as BaseAggregator


class CountryAggregator(BaseAggregator):

    def aggregate(self, results, probes):

        db = {}
        for result in results:
            result = Result.get(result)
            try:
                line = self.renderer.on_result(result, probes=probes)
                country = self.get_country(line.probe_id)
                db.setdefault(country, []).append(line)
            except ResultError:
                db[None] = json.dumps(result) + "\n"

        r = ""
        for country, lines in db.items():
            r += "{}\n".format(country)
            for line in lines:
                r += "  {}".format(line)

        return r

    @memoised(60 * 60 * 24 * 30)
    def get_country(self, probe_id):
        """
        This code really should live somewhere separate, like a Probe class, but
        for now, this will do.
        """

        return ProbeRequest(id=probe_id).next()["country_code"]
