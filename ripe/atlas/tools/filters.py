class FilterFactory(object):

    @staticmethod
    def create(cls, key, value):
        """Create new filter class based on the key"""
        if key == "asn":
            return ASNFilter(key, value)
        else:
            return Filter(key, value)


class Filter(object):
    """
    Class that represents filter for results. For now supports only attributes
    of probes property of Result property. It could be extended for any property
    of Result easily.
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def filter(self, result):
        """
        Decide if given result should be filtered (False) or remain on the
        pile of results.
        """
        attr_value = getattr(result.probe, self.key)
        if attr_value == self.value:
            return True

        return False


class ASNFilter(Filter):
    """Class thar represents filter by probes that belong to given ASN."""

    def filter(self, result):
        asn_v4 = getattr(result.probe, "asn_v4")
        asn_v6 = getattr(result.probe, "asn_v6")
        if self.value in (asn_v4, asn_v6):
            return True

        return False


def filter_results(filters, results):
    """docstring for filter"""
    for result in results[:]:
        for rfilter in filters:
            if not rfilter.filter(result):
                results.remove(result)

    return results
