from ..cache import cache

from ripe.atlas.cousteau import ProbeRequest


class Status(object):

    NAMES = {
        1: "Connected",
        2: "Disconnected",
        3: "Never Connected"
    }

    def __init__(self, pk):
        self.id = pk
        self.name = self.NAMES[pk]


class Probe(object):
    """
    A crude representation of the data we get from the API via Cousteau
    """

    EXPIRE_TIME = 60 * 60 * 24 * 30

    def __init__(self, **kwargs):

        self.id = kwargs.get("id")
        self.is_anchor = kwargs.get("is_anchor")
        self.country_code = kwargs.get("country_code")
        self.description = kwargs.get("description")
        self.is_public = kwargs.get("is_public")
        self.asn_v4 = kwargs.get("asn_v4")
        self.asn_v6 = kwargs.get("asn_v6")
        self.address_v4 = kwargs.get("address_v4")
        self.address_v6 = kwargs.get("address_v6")
        self.prefix_v4 = kwargs.get("prefix_v4")
        self.prefix_v6 = kwargs.get("prefix_v6")
        self.geometry = (kwargs["latitude"], kwargs["longitude"])
        self.status = Status(kwargs["status"])

    def __str__(self):
        return "Probe #{}".format(self.id)

    def __repr__(self):
        return str(self)

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
            return cls.get_from_api([pk])[0]

    @classmethod
    def get_from_api(cls, ids):
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
            kwargs = {"id__in": ",".join(fetch_ids)}
            for probe in [cls(**p) for p in ProbeRequest(**kwargs)]:
                cache.set("probe:{}".format(probe.id), probe, cls.EXPIRE_TIME)
                r.append(probe)

        return r
