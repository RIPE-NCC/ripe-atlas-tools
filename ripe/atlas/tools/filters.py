# Copyright (c) 2016 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from ripe.atlas.sagan import Result
from ripe.atlas.sagan import ResultParseError
from ripe.atlas.cousteau import ProbeRequest
from ripe.atlas.cousteau import Probe as CProbe

from .exceptions import RipeAtlasToolsException
from .cache import cache
from .settings import conf


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
                "Cousteau's Probe class does not have an attribute " "called: <{}>"
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


class SaganSet(object):
    """
    An iterable of sagan results with attached probe information that allows
    for filtering by the filters module.
    """

    def __init__(self, iterable=None, probes=()):
        self._probes = probes
        self._iterable = iterable

    def __iter__(self):

        sagans = []

        for line in self._iterable:

            # line may be a dictionary (parsed JSON)
            if hasattr(line, "strip"):
                line = line.strip()

            # Break out when there's nothing left
            if not line:
                break

            try:
                sagan = Result.get(
                    line,
                    on_error=Result.ACTION_IGNORE,
                    on_warning=Result.ACTION_IGNORE,
                )
                if not self._probes or sagan.probe_id in self._probes:
                    sagans.append(sagan)
                if len(sagans) > 100:
                    for sagan in self._attach_probes(sagans):
                        yield sagan
                    sagans = []
            except ResultParseError:
                pass  # Probably garbage in the file

        for sagan in self._attach_probes(sagans):
            yield sagan

    def __next__(self):
        return iter(self).next()

    def next(self):
        return self.__next__()

    def _attach_probes(self, sagans):
        probes = dict(
            [
                (p.id, p)
                for p in Probe.get_many(
                    (s.probe_id for s in sagans)
                )
            ]
        )
        for sagan in sagans:
            sagan.probe = probes[sagan.probe_id]
            yield sagan


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
            kwargs = {"id": pk, "server": conf["api-server"]}
            probe = CProbe(**kwargs)
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
            kwargs = {"id__in": fetch_ids, "server": conf["api-server"]}
            for probe in [p for p in ProbeRequest(return_objects=True, **kwargs)]:
                cache.set("probe:{}".format(probe.id), probe, cls.EXPIRE_TIME)
                r.append(probe)

        return r
