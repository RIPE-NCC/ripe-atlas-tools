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

import os

from ..exceptions import RipeAtlasToolsException
from ..helpers.validators import ArgumentType
from ..settings import AliasesDB, aliases
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "alias"

    EDITOR = os.environ.get("EDITOR", "/usr/bin/vim")
    DESCRIPTION = "Manage measurements' and probes' aliases"
    EXTRA_DESCRIPTION = (
        "As an alternative to this command, you can just create/edit {}".format(
            AliasesDB.USER_RC
        )
    )

    def add_arguments(self):
        subparsers = self.parser.add_subparsers(
            title="action",
            dest="action",
            help="Action to be performed on aliases. "
            "Run 'ripe-atlas alias <action> --help' for more details.",
        )

        add_parser = subparsers.add_parser("add", help="Add/modify an alias.")
        add_parser.add_argument(
            "type",
            action="store",
            choices=["measurement", "probe"],
            help="Type of target object.",
        )
        add_parser.add_argument(
            "target",
            action="store",
            type=int,
            help="Target's ID.",
        )
        add_parser.add_argument(
            "alias",
            action="store",
            type=ArgumentType.alias_is_valid,
            help="Alias name.",
        )

        del_parser = subparsers.add_parser("del", help="Remove an alias.")
        del_parser.add_argument(
            "type",
            action="store",
            choices=["measurement", "probe"],
            help="Type of target object.",
        )
        del_parser.add_argument(
            "alias",
            action="store",
            type=ArgumentType.alias_is_valid,
            help="Alias name.",
        )

        show_parser = subparsers.add_parser("show", help="Show target's ID.")
        show_parser.add_argument(
            "type",
            action="store",
            choices=["measurement", "probe"],
            help="Type of target object.",
        )
        show_parser.add_argument(
            "alias",
            action="store",
            type=ArgumentType.alias_is_valid,
            help="Alias name.",
        )

        list_parser = subparsers.add_parser("list", help="List configured aliases.")
        list_parser.add_argument(
            "type",
            action="store",
            choices=["measurement", "probe"],
            help="Type of target object.",
        )

        subparsers.add_parser(
            "editor",
            help="Invoke {0} to edit the configuration directly".format(self.EDITOR),
        )

    def run(self):

        if not self.arguments.action:
            raise RipeAtlasToolsException(
                "Action not given. Use --help for more information."
            )

        if self.arguments.action == "editor":
            os.system("{0} {1}".format(self.EDITOR, AliasesDB.USER_RC))
            return self.ok("Aliases file writen to {}".format(AliasesDB.USER_RC))

        else:
            alias_type = self.arguments.type

            if self.arguments.action == "add":
                alias_name = self.arguments.alias
                target_id = self.arguments.target

                try:
                    ArgumentType.alias_is_valid(alias_name)
                except Exception as e:
                    raise RipeAtlasToolsException(str(e))

                aliases[alias_type][alias_name] = target_id
                AliasesDB.write(aliases)

            elif self.arguments.action == "del":
                alias_name = self.arguments.alias
                del aliases[alias_type][alias_name]
                AliasesDB.write(aliases)

            elif self.arguments.action == "show":
                alias_name = self.arguments.alias
                if alias_name in aliases[alias_type]:
                    self.ok(
                        "'{}' is an alias for {}".format(
                            alias_name, aliases[alias_type][alias_name]
                        )
                    )
                else:
                    self.not_ok("'{}' alias does not exist".format(alias_name))

            elif self.arguments.action == "list":
                res = "{} aliases:\n\n".format(alias_type.capitalize())
                for alias_name in sorted(aliases[alias_type]):
                    res += "- {}: {}\n".format(
                        alias_name, aliases[alias_type][alias_name]
                    )
                self.ok(res)
