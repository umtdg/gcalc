import argparse

from typing import Sequence, Text

from gcalc.namespaces import NsBase


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, prog="gcalc"):
        super(ArgumentParser, self).__init__(prog=prog)
        self.add_argument("-c", "--course", dest="course", required=True,
                          type=str, help="Course name")
        self.add_argument("-d", "--dry-run", dest="dry_run", action="store_true",
                          help="Print the new course/assignment after making changes"
                               " without actually saving it to the file")
        self.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                          help="Enable verbose output")


def get_base_parser(prog: str = "gcalc") -> ArgumentParser:
    return ArgumentParser(prog=prog)


def get_new_parser() -> ArgumentParser:
    parser = get_base_parser(prog="new")
    parser.add_argument("-r", "--replace", dest="replace", action="store_true",
                        help="Replace existing course with the same name")
    return parser


def get_show_parser() -> ArgumentParser:
    parser = get_base_parser(prog="show")
    parser.add_argument("-g", "--grades", dest="show_grades", action="store_true",
                        help="Also show total grade of each assignment")
    parser.add_argument("-a", "--all", dest="show_all", action="store_true",
                        help="Show every course instead of just one")
    return parser


def get_add_base_parser(prog: str = "add") -> ArgumentParser:
    parser = get_base_parser(prog=prog)
    parser.add_argument("-n", "--name", dest="name", required=True,
                        type=str, help="Assignment name")
    parser.add_argument("-o", "--outof", dest="out_of", default=100,
                        type=int, help="Grades are calculated out of this (i.e. Maximum grade for the assignment)")
    parser.add_argument("grades", nargs=argparse.REMAINDER, type=float, default=[],
                        help="Grades of the assignment out of --outof option")

    return parser


def get_add_parser(prog: str = "add", required: bool = True) -> ArgumentParser:
    parser = get_add_base_parser(prog=prog)
    parser.add_argument("-w", "--weight", dest="weight", required=required,
                        type=float, help="Total weight of the assignment in percentage")
    parser.add_argument("--count", dest="count", required=required,
                        type=int, help="Number of assignments")

    return parser


def get_edit_parser() -> ArgumentParser:
    parser = get_add_parser("edit", False)
    parser.add_argument("--rm", dest="rm", action="store_true", required=False,
                        help="Remove the assignment. When specified, other options "
                             "except -n and -c are ignored")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--update", dest="update", action="store_true",
                       required=False, help="Update current grades with the new ones")
    group.add_argument("-a", "--append", dest="append", action="store_true",
                       required=False,
                       help="Append new grades to current grades, total number of grades"
                            " cannot exceed number of assignments")
    return parser


def parse_args(parser: ArgumentParser,
               namespace: NsBase,
               args: Sequence[Text] = ...) -> None:
    parser.parse_args(args, namespace=namespace)
