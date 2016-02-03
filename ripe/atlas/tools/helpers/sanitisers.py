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

import six

FORBIDDEN = dict((i, None) for i in list(range(0, 32)) + [127])


def sanitise(s, strip_newlines=True):
    """
    Strip out control characters to prevent people from screwing with the output
    """

    if not isinstance(s, six.string_types):
        return s

    if six.PY2:
        s = unicode(s)

    if not strip_newlines:
        return s.translate(
            dict((k, v) for k, v in FORBIDDEN.items() if not k == 10))

    return s.translate(FORBIDDEN)
