import argparse
import cmd
import json
import os
import platform

import rich.style
from rich.console import Console
from rich.table import Table
from rich.style import Style
from rich.color import Color

from typing import Any, Dict, List, Optional

from gcalc.course import Course
from gcalc.assignment import Assignment
from gcalc.namespaces import (
    NsAdd,
    NsBase,
    NsNew,
    NsEdit,
    NsShow,
    NsAddBase
)
from gcalc.parsers import (
    get_base_parser,
    get_new_parser,
    get_show_parser,
    get_add_parser,
    get_edit_parser,
    parse_args,
    ArgumentParser
)

# import readline if available
try:
    import readline
except ImportError:
    readline = None

# rich config
console = Console()
error_str = "[bold red][!][/bold red]"
warn_str = "[bold yellow][!][/bold yellow]"
info_str = "[bold blue][*][/bold blue]"
dry_str = "[bold green][DRY RUN][/bold green]"

# check home directory
current_os = platform.system()
home_dir = ""
if current_os == "Linux":
    home_dir = os.environ["HOME"]
elif current_os == "Windows":
    home_dir = os.environ["HOMEPATH"]
else:
    console.print(f"{error_str} Operating system not supported")
    exit(0)

grades_dir = os.path.join(home_dir, ".grades")


class GCalc(cmd.Cmd):
    def __init__(self):
        super().__init__()

        self.courses: Dict[str, Course] = {}
        self.courses_old: Dict[str, Course] = {}
        self.courses_file: str = os.getenv(
            "GCALC_COURSES_FILE",
            os.path.join(home_dir, ".courses.json")
        )
        self.dry_run: bool = False
        self.message: Optional[str] = None
        self.verbose: bool = False

        self._load_courses()

    def postcmd(self, stop: bool, line: str) -> bool:
        if not self.dry_run:
            self._save_courses()
        elif self.message is not None:
            console.print(f"{dry_str} {self.message}")

        return super(GCalc, self).postcmd(stop, line)

    def _try_parse_args(self, parser: ArgumentParser,
                        namespace: NsBase,
                        arg: str) -> bool:
        try:
            parse_args(parser, namespace, arg.split(" "))
            namespace.course = namespace.course.casefold()
            if isinstance(namespace, NsAddBase):
                namespace.name = namespace.name.casefold()

            self.dry_run = namespace.dry_run
            self.verbose = namespace.verbose

            if self.verbose and self.dry_run:
                console.print(f"{info_str} Dry run enabled")

            return True
        except argparse.ArgumentError as e:
            console.print(f"{error_str} {e.message}")
            return False

    def _check_courses_file(self) -> Optional[Any]:
        try:
            with open(self.courses_file, "r") as f:
                courses = json.loads(f.read())
            return courses
        except FileNotFoundError as e:
            # console.print(f"{error_str} {str(e)}")
            return None
        except json.JSONDecodeError as e:
            console.print(f"{error_str} Json error: {str(e)}")
            return None

    def _load_courses(self) -> None:
        courses = self._check_courses_file()
        if not courses:
            return

        if not isinstance(courses, list):
            console.print(
                f"{error_str} The file {self.courses_file} does not contain a list of courses"
            )
            return

        try:
            courses = [Course.from_dict(course) for course in courses]
        except KeyError as e:
            console.print(f"{error_str} {str(e)}")
            return

        self.courses = {course._name: course for course in courses}

    def _save_courses(self) -> None:
        with open(self.courses_file, "w+") as f:
            f.write(json.dumps([course.dict for course in self.courses.values()], indent=4))

    def _check_course(self, name: str) -> bool:
        if name not in self.courses:
            console.print(f"{error_str} Could not found course with name '{name}'")
            return False

        if self.verbose:
            console.print(f"{info_str} Given course '{name}' is valid")

        return True

    def _new_course(self, name: str, replace: bool):
        exists: bool = name in self.courses

        self.message = f"New course '{name}'"
        if exists and replace:
            self.message = f"Replacing already existing course '{name}'"
            if not self.dry_run:
                console.print(f"{warn_str} {self.message}")
        elif exists:
            self.message = f"Course '{name}' already exists"
            if not self.dry_run:
                console.print(f"{info_str} {self.message}")
            return

        if self.verbose:
            console.print(f"{info_str} Added new course")
        self.courses[name] = Course(name)

    def do_new(self, arg: str):
        """Create a new course"""
        parsed: NsNew = NsNew()
        if not self._try_parse_args(get_new_parser(), parsed, arg):
            return

        self._new_course(parsed.course, parsed.replace)

    def do_rm(self, arg: str):
        parsed: NsBase = NsBase()
        if not self._try_parse_args(get_base_parser(prog="rm"), parsed, arg):
            return

        if not self._check_course(parsed.course):
            return

        self.message = f"Remove course '{parsed.course}'"
        self.courses.pop(parsed.course)

    def do_ls(self, _: str):
        """Print name of the every course"""
        for course in self.courses.values():
            console.print(str(course))

    @classmethod
    def _print_course_table(cls, course: Course, show_grades: bool) -> None:
        table = Table(title=f"{str(course)} Assignments")
        table.add_column("Name")
        table.add_column("Weight")
        table.add_column("Count")

        grades: Dict[str, float] = {}
        if show_grades:
            table.add_column("Grade")
            grades = course.calculate_grades()

        total_weight = 0.0
        total_count = 0
        for assignment in course.assignments.values():
            weight = f"{assignment.weight:.2f}%"
            count = str(assignment.count)
            if show_grades:
                table.add_row(assignment.name, weight, count,
                              f"{grades[assignment.name]:.2f}")
            else:
                table.add_row(assignment.name, weight, count)

            total_weight += assignment.weight
            total_count += assignment.count

        total_weight = f"{total_weight:.2f}%"
        total_count = str(total_count)
        if show_grades:
            table.add_row("Total", total_weight, total_count,
                          f"{grades['total']:.2f}")
        else:
            table.add_row("Total", total_weight, total_count)

        console.print(table, justify="center")

    def _show_course(self, name: str, show_grades: bool):
        if self._check_course(name):
            self._print_course_table(self.courses[name], show_grades=show_grades)

    def do_show(self, arg: str):
        """Show a table of assignments of a course"""
        parsed: NsShow = NsShow()
        if not self._try_parse_args(get_show_parser(), parsed, arg):
            return

        if parsed.show_all:
            for course in self.courses.values():
                self._print_course_table(course, parsed.show_grades)
        else:
            self._show_course(parsed.course, parsed.show_grades)

    def _check_assignment(
            self,
            name: str,
            course_name: str,
            should_exists: bool = False
    ) -> bool:
        if not self._check_course(course_name):
            return False

        if name in self.courses[course_name].assignments:
            if not should_exists:
                console.print(f"{error_str} Assignment with the same name already exists")
            return should_exists

        return True

    def _check_assignment_args(self, args: NsAdd) -> bool:
        result: bool = True

        if args.weight is not None and args.weight <= 0:
            console.print(f"{error_str} Assignment weight "
                          f"should be a positive floating point number")
            result = False

        if args.count is not None and args.count <= 0:
            console.print(f"{error_str} Number of assignments should be"
                          f"a positive integer")
            result = False

        if args.out_of <= 0:
            console.print(f"{error_str} '--outof' option should take positive integers")
            result = False

        if len(args.grades) > args.count:
            console.print(f"{error_str} Total number of grades cannot exceed"
                          f" number of assignments (--count option)")
            result = False

        if self.verbose and result:
            console.print(f"{info_str} Given assignment '{args.name}' is valid")

        return result

    def do_add(self, arg: str):
        """Add an assignment to a course"""
        parsed: NsAdd = NsAdd()
        if not self._try_parse_args(get_add_parser(), parsed, arg):
            return

        if not self._check_assignment_args(parsed):
            return

        course = self.courses[parsed.course]

        assignment = Assignment(
            parsed.name, parsed.weight, parsed.count
        )
        assignment.grades = [100 * grade / parsed.out_of for grade in parsed.grades]

        if not course.add_assignment(assignment):
            self.message = "Assignment with the same name already exists"
            console.print(f"{error_str} {self.message}")
        else:
            self.message = f"{repr(course)}"

    @classmethod
    def _update_grades(cls,
                       assignment: Assignment,
                       grades: List[float],
                       out_of: int):
        if len(grades) > assignment.count:
            console.print(f"{error_str} Total number of grades cannot exceed"
                          f" number of assignments (--count option)")
            return

        assignment.grades.clear()
        assignment.grades = [100 * grade / out_of for grade in grades]

    @classmethod
    def _append_grades(cls,
                       assignment: Assignment,
                       grades: List[float],
                       out_of: int):
        if len(grades) + len(assignment.grades) > assignment.count:
            console.print(f"{error_str} Total number of grades cannot exceed"
                          f" number of assignments (--count option)")
            return

        assignment.grades += [100 * grade / out_of for grade in grades]

    def do_edit(self, arg: str):
        """Edit an existing assignment in a course"""
        parsed: NsEdit = NsEdit()
        if not self._try_parse_args(get_edit_parser(), parsed, arg):
            return

        if not self._check_assignment(parsed.name, parsed.course, True):
            return

        if self.verbose:
            console.print(f"{info_str} Editing assignment '{parsed.name}' "
                          f"in course '{parsed.course}'")

        course = self.courses[parsed.course]

        if parsed.rm:
            self.message = f"Removing assignment '{parsed.name}'"
            course.remove_assignment(parsed.name)
            return

        assignment = course.assignments[parsed.name]

        if parsed.weight is not None:
            assignment.weight = parsed.weight

        if parsed.count is not None:
            assignment.count = parsed.count
        else:
            parsed.count = assignment.count

        if not self._check_assignment_args(parsed):
            return

        if parsed.update:
            self._update_grades(assignment, parsed.grades, parsed.out_of)
        elif parsed.append:
            self._append_grades(assignment, parsed.grades, parsed.out_of)

        self.message = f"Assignment after update/append:\n{repr(assignment)}"
