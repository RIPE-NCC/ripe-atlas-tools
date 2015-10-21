from __future__ import absolute_import, print_function

import random
import requests

from ..cache import cache
from .base import Command as BaseCommand


class Command(BaseCommand):

    DESCRIPTION = "https://xkcd.com/806/"
    HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RIPE Atlas Tools (Magellan)",
    }
    URLS = {
        "root": "https://api.github.com",
        "statistics": "/repos/RIPE-NCC/ripe-atlas-tools/stats/contributors",
        "users": "/users"
    }

    def run(self):

        r = "\nThanks for using RIPE Atlas!\n\nThis toolkit " \
            "(Magellan) is a group effort, spearheaded by the team at the " \
            "RIPE\nNCC, but supported by members of the community from all " \
            "over.  If you're\ncurious about who we are and what sorts of " \
            "stuff we work on, here's a break\ndown of our contributions to " \
            "date.\n\nName                     Changes  URL\n{}\n".format(
                "-" * 79)

        for contributor in self.get_contributors():
            r += "{name:20}  {changes:10}  {url}\n".format(**contributor)

        print(r + """
                                                             |
                                                             |
                                                             |
                                                     |       |
                                                     |      ---
                                                    ---     '-'
                                                    '-'  ____|_____
                                                 ____|__/    |    /
                                                /    | /     |   /
                                               /     |(      |  (
                                              (      | \     |   \\
                                               \     |  \____|____\   /|
                                               /\____|___`---.----` .' |
                                           .-'/      |  \    |__.--'    \\
                                         .'/ (       |   \   |.          \\
                                      _ /_/   \      |    \  | `.         \\
                                       `-.'    \.--._|.---`  |   `-._______\\
                                          ``-.-------'-------'------------/
                                              `'._______________________.'\n""")

    def get_contributors(self):

        cache_key = "github:statistics"

        r = cache.get(cache_key)
        if r:
            random.shuffle(r)
            return r

        response = requests.get(
            "{}{}".format(self.URLS["root"], self.URLS["statistics"]),
            headers=self.HEADERS
        )

        r = []
        for contributor in response.json():
            user = self.get_user(contributor["author"]["login"])
            d = {
                "changes": 0,
                "name": user["name"] or contributor["author"]["login"],
                "url": contributor["author"]["html_url"]
            }
            for week in contributor["weeks"]:
                d["changes"] += week["a"] + week["d"]
            r.append(d)

        random.shuffle(r)

        # Sometimes GitHub just returns nothing
        if not r:
            return self.get_contributors()

        cache.set(cache_key, r, 60 * 10)

        return r

    def get_user(self, username):

        cache_key = "github-user:{}".format(username)

        user = cache.get(cache_key)
        if user:
            return user

        cache.set(
            cache_key,
            requests.get(
                "{}{}/{}".format(
                    self.URLS["root"],
                    self.URLS["users"],
                    username
                ),
                headers=self.HEADERS
            ).json(),
            60 * 60 * 24 * 365
        )

        return self.get_user(username)
