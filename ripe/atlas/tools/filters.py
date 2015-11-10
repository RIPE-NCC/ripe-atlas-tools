from .exceptions import RipeAtlasToolsException


class FilterFactory(object):

    @staticmethod
    def create(key, value):
        """Create new filter class based on the key"""
        if key == "asn":
            return ASNFilter(value)
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
        try:
            attr_value = getattr(result.probe, self.key)
        except AttributeError:
            log = (
                "Cousteau's Probe class does not have an attribute "
                "called: <{}>"
            ).format(self.key)
            raise RipeAtlasToolsException(log)
        if attr_value == self.value:
            return True

        return False


class ASNFilter(Filter):
    """Class thar represents filter by probes that belong to given ASN."""

    def __init__(self, value):
        key = "asn"
        super(ASNFilter, self).__init__(key, value)

    def filter(self, result):
        asn_v4 = getattr(result.probe, "asn_v4")
        asn_v6 = getattr(result.probe, "asn_v6")
        if self.value in (asn_v4, asn_v6):
            return True

        return False


def filter_results(filters, results):
    """docstring for filter"""
    new_results = []
    for result in results:
        for rfilter in filters:
            if rfilter.filter(result):
                new_results.append(result)
                break

    return new_results
