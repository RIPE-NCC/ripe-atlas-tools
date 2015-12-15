# Copyright (c) 2015 RIPE NCC
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

import sys


class RipeAtlasToolsException(Exception):

    RED = "\033[1;31m"
    RESET = "\033[0m"

    def write(self):
        r = str(self)
        if sys.stderr.isatty():
            r = self.RED + r + self.RESET
        sys.stderr.write("\n{0}\n\n".format(r))
