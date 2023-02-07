# Copyright (c) 2023 RIPE NCC
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

import argparse
import csv
import re
from io import StringIO
from typing import (Any, Dict, Iterable, Iterator, List, Mapping, Optional,
                    Tuple)

from typing_extensions import Literal, NotRequired, TypedDict

from .colours import colourise

Alignment = Literal["<", "^", ">"]
LEFT: Alignment = "<"
CENTRE: Alignment = "^"
RIGHT: Alignment = ">"


class ColumnDef(TypedDict):
    align: Alignment
    width: int


class RowDef(TypedDict):
    obj: NotRequired[Any]
    values: Dict[str, Any]
    colour: NotRequired[str]


# ((1, "Value1"), (3, True), (4, 5342),)
AggregationKey = Tuple[Any, ...]


class SortableNull:
    def __str__(self):
        return "null"

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return isinstance(other, type(self))

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return False
        return True

    def __gt__(self, other):
        return False


class Renderer:
    """
    Abstract base class for tabular renderers.
    """

    def __init__(
        self,
        rows: List[RowDef],
        total_count: int,
        columns: Dict[str, ColumnDef],
        filters: Mapping[str, str],
        arguments: argparse.Namespace,
    ):
        self.rows = rows
        self.total_count = total_count
        self.columns = columns
        self.filters = filters

        self.aggregate_by: List[str] = arguments.aggregate_by
        self.max_per_aggregation: Optional[int] = arguments.max_per_aggregation
        self.no_header: bool = arguments.no_header

    def __iter__(self) -> Iterator[str]:
        if not self.no_header:
            for line in self.get_header():
                yield line
        if self.aggregate_by:
            for composite, rows in self._aggregate():
                aggr_header = self.get_aggregation_header(composite)
                if aggr_header is not None:
                    yield aggr_header
                for row in rows:
                    yield self.get_line(row)
        else:
            for row in self.rows:
                yield self.get_line(row)
        if not self.no_header:
            for line in self.get_footer():
                yield line

    def get_header(self) -> Iterable[str]:
        """
        Return an iterable of lines to output before the table.
        """
        return []

    def get_aggregation_header(self, composite: AggregationKey) -> Optional[str]:
        """
        Return a line to output before each aggregation bucket.
        """
        return None

    def get_line(self, row: RowDef) -> str:
        """
        Return a single line rendering the given row.
        """
        raise NotImplementedError

    def get_footer(self) -> Iterable[str]:
        """
        Return an iterable of lines to output after the table.
        """
        return []

    def _aggregate(self) -> Iterable[Tuple[AggregationKey, List[RowDef]]]:
        buckets: Dict[AggregationKey, List[RowDef]] = {}
        for row in self.rows:
            values = [row["values"][k] for k in self.aggregate_by]
            composite = tuple(SortableNull() if v is None else v for v in values)
            bucket = buckets.setdefault(composite, [])
            if (
                self.max_per_aggregation is None
                or len(bucket) < self.max_per_aggregation
            ):
                bucket.append(row)
        return sorted(buckets.items())


class PrettyRenderer(Renderer):
    """
    Renderer which outputs colourised, human-readable tables
    """

    _fmt = None

    @property
    def fmt(self) -> str:
        if not self._fmt:
            self._fmt = " ".join(
                f"{{!s:{c['align']}{c['width']}}}" for c in self.columns.values()
            )
        return self._fmt

    def get_header(self) -> Iterable[str]:
        if self.filters:
            yield ""
            yield colourise("Filters:", "white")
            for k, v in self.filters.items():
                if k not in ("search",):
                    v = str(v)
                yield colourise(f"  {k}: {v}", "cyan")
        yield ""
        yield colourise(self.fmt.format(*self.columns.keys()), "white")
        yield colourise(self._get_horizontal_rule(), "white")

    def get_aggregation_header(self, composite: AggregationKey) -> str:
        header = dict(zip(self.aggregate_by, composite))
        values = []
        for name in self.columns:
            if name in self.aggregate_by:
                values.append(header[name])
            else:
                values.append(" ")
        line = self.fmt.format(*values)
        result = re.sub(
            r" ( *)( [^ ]|$)",
            lambda s: " " + len(s.group(1)) * "-" + s.group(2),
            line,
        )
        for name in self.aggregate_by:
            if name not in self.columns:
                result += f" ({name}:{header[name]})"
        return result

    def get_line(self, row: RowDef) -> str:
        values = [
            "-" if val is None else str(val)[: col["width"]]
            for (col, val) in zip(self.columns.values(), row["values"].values())
        ]
        line = self.fmt.format(*values)
        if row.get("colour"):
            line = colourise(line, row["colour"])
        return line

    def get_footer(self) -> Iterable[str]:
        hr = self._get_horizontal_rule()
        yield colourise(hr, "white")
        yield colourise(
            ("{:>" + str(len(hr)) + "}").format(
                "Showing {} of {}".format(
                    min(len(self.rows), self.total_count) or "all",
                    self.total_count,
                )
            ),
            "white",
        )

    def _get_horizontal_rule(self, char="=") -> str:
        """
        A bit of a hack: We get a formatted line for no other reason than to
        determine the width of that line.  Then we use a regex to overwrite that
        line with "=".
        """
        return re.sub(r".", char, self.fmt.format(*["" for c in self.columns]))


class CSVRenderer(Renderer):
    """
    Renderer which outputs comma-separated values, where strings are always
    enclosed in double quotes, and literal double quotes are written as "".
    """

    dialect = "excel"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = StringIO()
        self.writer = csv.writer(self.data, dialect=self.dialect)

    def get_header(self) -> Iterable[str]:
        yield self.get_line({"values": dict((k, k) for k in self.columns.keys())})

    def get_line(self, row: RowDef) -> str:
        self.data.seek(self.data.truncate(0))
        self.writer.writerow(
            [
                "" if v is None else str(v)
                for (k, v) in row["values"].items()
                if k in self.columns
            ]
        )
        return self.data.getvalue()[:-1]


class TabRenderer(Renderer):
    """
    Renderer which outputs tab-separated values, where literal tabs are replaced
    with spaces.
    """

    def get_header(self) -> Iterable[str]:
        yield self.get_line({"values": dict((k, k) for k in self.columns.keys())})

    def get_line(self, row: RowDef) -> str:
        return "\t".join(
            "" if v is None else str(v).replace("\t", "    ")
            for (k, v) in row["values"].items()
            if k in self.columns
        )


class IDAction(argparse.Action):
    def __call__(self, parser, namespace, *args, **kwargs):
        namespace.format = "tab"
        namespace.field = ["id"]
        namespace.no_header = True


def add_argument_group(parser: argparse.ArgumentParser, fields: Iterable[str]):
    """
    Add an argument group to the given parser with all of the parameters
    for controlling the tabular renderers.
    """
    fields = list(fields)
    group = parser.add_argument_group("Output")
    group.add_argument(
        "--field",
        type=str,
        action="append",
        choices=fields,
        default=[],
        help="The field(s) to display. Invoke multiple times for multiple fields.",
    )
    group.add_argument(
        "--format",
        default="pretty",
        choices=renderers.keys(),
        help="Output format. Default: pretty",
    )
    group.add_argument(
        "--no-header",
        action="store_true",
        default=False,
        help="Omit header line(s)",
    )
    group.add_argument(
        "--ids-only",
        nargs=0,
        action=IDAction,
        help="Print only IDs, equivalent to --format=tab --field=id --no-header. "
        "Useful for piping to another command.",
    )
    group.add_argument(
        "--aggregate-by",
        action="append",
        default=[],
        choices=fields,
        help="Aggregate results based on all specified aggregations."
        " Use this option multiple times for more specific aggregations.",
    )
    group.add_argument(
        "--max-per-aggregation",
        type=int,
        help="Maximum number of rows per aggregated bucket.",
    )


renderers = {
    "pretty": PrettyRenderer,
    "csv": CSVRenderer,
    "tab": TabRenderer,
}
