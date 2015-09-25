from ripe.atlas.sagan import Result, ResultError

from ..probes import Probe
from ..exceptions import RipeAtlasToolsException

class Aggregator(object):

    # All renderers are supposed to support aggregation on the
    # basis of probes' properties (country, ASN, ...) by returning
    # Result objects containing the rendered output line and the 
    # .probe_id value.
    #
    # Custom aggregations must be explicitly declared within
    # renderers' .AGGREGATES and matched by aggregators' REQUIRES.
    REQUIRES = None

    def _prepare(self):
        # Useful to parse aggregator's options and initialize custom stuff
        return

    def __init__(self, renderer, options):
        self.options = options
        self.renderer = renderer

        if self.REQUIRES and not self.REQUIRES in renderer.AGGREGATES:
            raise RipeAtlasToolsException("Can't use this aggregation with "
                                          "the current renderer.")

        self._prepare()

    def _get_aggr_key(self, probe, sagan):
        # Must be implemented in children classes
        raise NotImplemented()

    def aggregate(self, results, probes):

        # Build "sagans" as a list of Sagan result objects: http://goo.gl/HKFkHE
        sagans = []
        for result in results:
            try:
                result = Result.get(result)
                if not probes or result.probe_id in probes:
                    sagans.append(result)
            except ResultError:
                print("Bad result found: {}\n".format(json.dumps(result)))

        # Build a lookup dictionary of id:object for below
        probes = dict([
            (p.id, p) for p in Probe.get_from_api([r.probe_id for r in sagans])
        ])

        # Build the aggregate database
        db = {}
        for result in sagans:
            line = self.renderer.on_result(result, probes=probes)

            try:
                probe_id = line.probe_id
            except:
                # It should never happen in the future, when all the renderer
                # will be implemented to return Result objects with .probe_id
                raise RipeAtlasToolsException("Can't use this aggregation "
                                              "because the renderer seems "
                                              "to not support it.")

            aggr_key = self._get_aggr_key(probes[probe_id], result)
            db.setdefault(aggr_key, []).append(line)

        #TODO: a way to sort aggregated results should be found.
        #Hint: something like a 'position' should be returned by
        #      the aggregator; if not present, the same aggr_key
        #      can be used as fallback.

        # Print everything out
        r = ""
        for aggr_key, lines in db.items():
            r += "{}\n".format(aggr_key)
            for line in lines:
                r += "  {}".format(line)
            r += "\n"

        return r

