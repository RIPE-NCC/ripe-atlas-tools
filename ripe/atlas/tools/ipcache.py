import time
import json
import socket
import urllib2
import IPy

from cache import cache

class IPCache(object):

    def get_details(self, ip):
        """
        Return {"ASN": "<str>", "Holder": "<str>", "Prefix": "<str>"}

        ASN may be None if the IP/prefix is not announced or private/reserved.
        """
        ip_object = IPy.IP(ip)

        ip = ip_object.strFullsize()

        details = cache.get("IPDetails:{}".format(ip))
        if details:
            return details

        details = {"ASN": None, "Holder": None, "Prefix": None}

        if ip_object.iptype() in ['RESERVED', 'UNSPECIFIED', 'LOOPBACK',
                                  'UNASSIGNED', 'DOCUMENTATION', 'ULA',
                                  'LINKLOCAL']:
            return details

        found = False
        for cache_entry in cache.keys():
            if cache_entry.startswith("IPDetailsPrefix:"):
                prefix_details = cache.get(cache_entry)
                prefix = IPy.IP(prefix_details["Prefix"])

                if ip_object in prefix:
                    details = prefix_details
                    found = True
                    break

        if not found:
            URL = "https://stat.ripe.net/data/prefix-overview/data.json?resource={}".format(ip)

            res = json.loads( urllib2.urlopen(URL).read() )

            if res["status"] == "ok":
                if res["data"]["asns"] != []:
                    details["ASN"] = str(res["data"]["asns"][0]["asn"])
                    details["Holder"] = res["data"]["asns"][0]["holder"]
                    details["Prefix"] = res["data"]["resource"]

                    cache.set("IPDetailsPrefix:{}".format(details["Prefix"]),
                              details, 60*60*24*7)

        cache.set("IPDetails:{}".format(ip), details, 60*60*24*7)

        return details

ip_cache = IPCache()
