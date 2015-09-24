import json

from ripe.atlas.sagan import Result, ResultError

from .base import Aggregator as BaseAggregator


class SimpleAggregator(BaseAggregator):

    def aggregate(self, results, probes):

        r = self.renderer.on_start()

        for result in results:
            result = Result.get(result)
            try:
                r += self.renderer.on_result(result, probes=probes)
            except ResultError:
                r += json.dumps(result) + "\n"

        r += self.renderer.on_finish()

        return r
