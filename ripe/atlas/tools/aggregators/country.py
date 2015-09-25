import json

from ripe.atlas.sagan import Result, ResultError

from ..probes import Probe
from .base import Aggregator as BaseAggregator


class CountryAggregator(BaseAggregator):

    def aggregate(self, results, probes):

        # Rebuild results as a list of Sagan result objects
        results = [Result.get(r) for r in results]

        # Build a lookup dictionary of id:object for below
        probes = dict([
            (p.id, p) for p in Probe.get_from_api([r.probe_id for r in results])
        ])

        # Build the aggregate database
        db = {}
        for result in results:
            try:
                line = self.renderer.on_result(result, probes=probes)
                db.setdefault(probes[line.probe_id].country_code, []).append(
                    line)
            except ResultError:
                db[None] = json.dumps(result) + "\n"

        # Print everything out
        r = ""
        for country, lines in db.items():
            r += "{}\n".format(country)
            for line in lines:
                r += "  {}".format(line)

        return r
