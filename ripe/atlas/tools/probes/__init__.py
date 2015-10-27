from ..cache import cache

from ripe.atlas.cousteau import ProbeRequest
from ripe.atlas.cousteau import Probe as CProbe


class Probe(object):
    """
    A crude representation of the data we get from the API via Cousteau
    """

    EXPIRE_TIME = 60 * 60 * 24 * 30

    @classmethod
    def get(cls, pk):
        """
        Given a single id, attempt to fetch a probe object from the cache.  If
        that fails, do an API call to get it.  Don't use this for multiple
        probes unless you know they're all in the cache, or you'll be in for a
        long wait.
        """
        r = cache.get("probe:{}".format(pk))
        if not r:
            probe = CProbe(id=pk)
            cache.set("probe:{}".format(probe.id), probe, cls.EXPIRE_TIME)
            return probe

    @classmethod
    def get_many(cls, ids):
        """
        Given a list of ids, attempt to get probe objects out of the local
        cache.  Probes that cannot be found will be fetched from the API and
        cached for future use.
        """

        r = []

        fetch_ids = []
        for pk in ids:
            probe = cache.get("probe:{}".format(pk))
            if probe:
                r.append(probe)
            else:
                fetch_ids.append(str(pk))

        if fetch_ids:
            kwargs = {"id__in": fetch_ids}
            for probe in [p for p in ProbeRequest(return_objects=True, **kwargs)]:
                cache.set("probe:{}".format(probe.id), probe, cls.EXPIRE_TIME)
                r.append(probe)

        return r
