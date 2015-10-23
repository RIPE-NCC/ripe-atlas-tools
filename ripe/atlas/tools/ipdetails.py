import requests
import IPy

from .cache import cache


class IP(object):

    RIPESTAT_URL = "https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}"

    def __init__(self, address):
        self.ip_object = IPy.IP(address)

        self.address = self.ip_object.strFullsize()
        self.asn = None
        self.holder = None
        self.prefix = None

        details = self._get_details()
        if details:
            self.asn = details["ASN"]
            self.holder = details["Holder"]
            self.prefix = details["Prefix"]

    def __str__(self):
        return "IP {}, ASN {}, Holder {}".format(
            self.address, self.asn, self.holder)

    def _get_details(self):
        details = cache.get("IPDetails:{}".format(self.address))
        if details:
            return details

        details = {"ASN": None, "Holder": None, "Prefix": None}

        not_querable_types = [
            'RESERVED', 'UNSPECIFIED', 'LOOPBACK',
            'UNASSIGNED', 'DOCUMENTATION', 'ULA',
            'LINKLOCAL', 'PRIVATE'
        ]
        if self.ip_object.iptype() in not_querable_types:
            return details

        found = False
        for cache_entry in cache.keys():
            if cache_entry.startswith("IPDetailsPrefix:"):
                prefix_details = cache.get(cache_entry)
                prefix = IPy.IP(prefix_details["Prefix"])

                if self.ip_object in prefix:
                    details = prefix_details
                    found = True
                    break

        if not found:
            URL = IP.RIPESTAT_URL.format(ip=self.address)

            try:
                response = requests.get(URL)
                if not response.ok:
                    return details
                res = response.json()
            except requests.exceptions.RequestException:
                return details

            if (
                res["status"] == "ok" and
                res["data"]["asns"]
            ):
                details["ASN"] = str(res["data"]["asns"][0]["asn"])
                details["Holder"] = res["data"]["asns"][0]["holder"]
                details["Prefix"] = res["data"]["resource"]

                cache.set(
                    "IPDetailsPrefix:{}".format(details["Prefix"]),
                    details,
                    60 * 60 * 24 * 7
                )

        cache.set("IPDetails:{}".format(self.address), details, 60 * 60 * 24 * 7)

        return details
