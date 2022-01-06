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

import random
import requests

from ..cache import cache
from ..helpers.colours import colourise
from ..helpers.sanitisers import sanitise
from .base import Command as BaseCommand


class Command(BaseCommand):

    DESCRIPTION = "https://xkcd.com/806/"
    HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RIPE Atlas Tools (Magellan)",
    }
    URLS = {
        "root": "https://api.github.com",
        "statistics": [
            "/repos/RIPE-NCC/ripe.atlas.sagan/stats/contributors",
            "/repos/RIPE-NCC/ripe-atlas-cousteau/stats/contributors",
            "/repos/RIPE-NCC/ripe-atlas-tools/stats/contributors",
        ],
        "users": "/users",
    }

    SPACING = (
        61,
        61,
        61,
        53,
        7,
        53,
        6,
        52,
        5,
        52,
        49,
        48,
        47,
        46,
        47,
        47,
        43,
        41,
        38,
        39,
        42,
        46,
    )
    BOAT = (
        "\n{}|\n{}|\n{}|\n{}|{}|\n{}|{}---\n{}---{}'-'\n{}'-'  ____|_____\n{}__"
        "__|__/    |    /\n{}/    | /     |   /\n{}/     |(      |  (\n{}(     "
        " | \\     |   \\\n{}\\     |  \\____|____\\   /|\n{}/\\____|___`---.----` ."
        "' |\n{}.-'/      |  \\    |__.--'    \\\n{}.'/ (       |   \\   |.      "
        "    \\\n{}_ /_/   \\      |    \\  | `.         \\\n{}`-.'    \\.--._|.--"
        "-`  |   `-._______\\\n{}``-.-------'-------'------------/\n{}`'.______"
        "_________________.'\n"
    ).format(*[" " * _ for _ in SPACING])

    WATER = "~" * 80

    def __init__(self, *args, **kwargs):
        BaseCommand.__init__(self, *args, **kwargs)
        self.statistics = {}

    def run(self):

        r = (
            "\nThanks for using RIPE Atlas!\n\nThis toolkit "
            "(Magellan) is a group effort, spearheaded by the team at the "
            "RIPE\nNCC, but supported by members of the community from all "
            "over.  If you're\ncurious about who we are and what sorts of "
            "stuff we work on, here's a break\ndown of our contributions to "
            "date.\n\nName                     Changes  URL\n{}\n"
        ).format("-" * 79)

        for contributor in self.get_contributors():
            r += "{name:20}  {changes:10}  {url}\n".format(**contributor)

        print(
            "{}{}{}\n".format(
                r,
                colourise(self.BOAT, "bold"),
                colourise(self.WATER, "blue"),
            )
        )

    def get_contributors(self):

        cache_key = "github:statistics"

        self.statistics = cache.get(cache_key, {})
        if not self.statistics:
            for url in self.URLS["statistics"]:
                self._update_statistics_from_url(url)
            cache.set(cache_key, self.statistics, 60 * 10)

        r = []
        for k, v in self.statistics.items():
            r.append(
                {"name": sanitise(k), "changes": v["changes"], "url": v["url"]}
            )

        random.shuffle(r)

        return r

    def _update_statistics_from_url(self, url):

        response = requests.get(
            "{}{}".format(self.URLS["root"], url), headers=self.HEADERS
        )

        contributors = response.json()

        # Sometimes, GitHub just returns nothing
        if not contributors:
            return self._update_statistics_from_url(url)

        for contributor in response.json():

            user = self.get_user(contributor["author"]["login"])
            name = user["name"] or contributor["author"]["login"]

            if name not in self.statistics:
                self.statistics[name] = {
                    "changes": 0,
                    "url": contributor["author"]["html_url"],
                }

            for week in contributor["weeks"]:
                self.statistics[name]["changes"] += week["a"] + week["d"]

    def get_user(self, username):

        cache_key = "github-user:{}".format(username)

        user = cache.get(cache_key)
        if user:
            return user

        cache.set(
            cache_key,
            requests.get(
                "{}{}/{}".format(
                    self.URLS["root"], self.URLS["users"], username
                ),
                headers=self.HEADERS,
            ).json(),
            60 * 60 * 24 * 365,
        )

        return self.get_user(username)
