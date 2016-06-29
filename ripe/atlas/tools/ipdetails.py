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

import requests
import IPy

from .cache import cache


class IP(object):

    RIPESTAT_URL = "https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}"
    CACHE_EXPIRATION_TIME = 60 * 60 * 24 * 7

    def __init__(self, address):
        self.cached_prefix_found = False
        self.ip_object = IPy.IP(address)

        self.address = self.ip_object.strFullsize()
        self.asn = None
        self.holder = None
        self.prefix = None
        self.not_querable_types = [
            'RESERVED', 'UNSPECIFIED', 'LOOPBACK',
            'UNASSIGNED', 'DOCUMENTATION', 'ULA',
            'LINKLOCAL', 'PRIVATE'
        ]

        details = self._get_details()
        if details:
            self.asn = details["ASN"]
            self.holder = details["Holder"]
            self.prefix = details["Prefix"]

    def _get_details(self):
        details = None

        if not self.is_querable():
            return details

        details = cache.get("IPDetails:{}".format(self.address))
        if details:
            return details

        details = self.get_from_cached_prefix()

        if not details:
            details = self.query_stat()

        if details:
            self.update_cache(details)

        return details

    def is_querable(self):
        """Determines if address is worth querable."""
        return (self.ip_object.iptype() not in self.not_querable_types)

    def get_from_cached_prefix(self):
        """Search cache for existing cached Prefix"""
        details = None

        for cache_entry in cache.keys():
            if not cache_entry.decode().startswith("IPDetailsPrefix:"):
                continue

            prefix_details = cache.get(cache_entry)

            # data could exist but expired
            if not prefix_details:
                continue

            prefix = IPy.IP(prefix_details["Prefix"])

            if self.ip_object in prefix:
                details = prefix_details
                self.cached_prefix_found = True
                break

        return details

    def query_stat(self):
        """Query RIPE Stat to get address details."""
        URL = self.RIPESTAT_URL.format(ip=self.address)
        details = {}

        try:
            response = requests.get(URL)
            if not response.ok:
                return details
            res = response.json()
        except (requests.exceptions.RequestException, ValueError):
            # Catch all requests exception + not valid json ones.
            return details

        if res.get("status") == "ok":
            try:
                details = {
                    "ASN": str(res["data"]["asns"][0]["asn"]),
                    "Holder": res["data"]["asns"][0]["holder"],
                    "Prefix": res["data"]["resource"]
                }
            except (
                # Protect from any kind of malformed json response
                AttributeError, ValueError, KeyError, IndexError, TypeError
            ):
                pass

        return details

    def update_cache(self, details):
        """Update cache for the address and prefix if needed."""
        if not self.cached_prefix_found:
            key = "IPDetailsPrefix:{}".format(details["Prefix"])
            cache.set(key, details, self.CACHE_EXPIRATION_TIME)

        key = "IPDetails:{}".format(self.address)
        cache.set(key, details, self.CACHE_EXPIRATION_TIME)

    def __str__(self):
        return "IP {}, ASN {}, Holder {}".format(
            self.address, self.asn, self.holder
        )
