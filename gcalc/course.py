from typing import Dict, List, Optional, Union

import gcalc.utils as utils
from gcalc.assignment import Assignment


class Course:
    DICT_TYPE = Dict[str, Union[str, int, List[Assignment.DICT_TYPE]]]

    def __init__(self, name: str):
        self._name: str = name
        self.assignments: Dict[str, Assignment] = {}

    def __str__(self) -> str:
        return self._name.upper()

    def __repr__(self) -> str:
        result = f"{str(self)}\n"
        for assignment in self.assignments.values():
            result += f"\t{str(assignment)}\n"
        return result

    def __eq__(self, other: "Course") -> bool:
        return self._name.casefold() == other._name.casefold()

    @property
    def name(self) -> str:
        return self.name

    @property
    def dict(self) -> "Course.DICT_TYPE":
        return {
            "name": self._name,
            "assignments": [a.__dict__ for a in self.assignments.values()]
        }

    @staticmethod
    def from_dict(d: "Course.DICT_TYPE") -> "Course":
        utils.check_dict_keys(
            d,
            ["name"],
            throw=True
        )

        course = Course(d["name"])
        if "assignments" in d and \
                isinstance(d["assignments"], list) and \
                all(isinstance(a, dict) for a in d["assignments"]):
            for assignment in d["assignments"]:
                course.add_assignment(Assignment.from_dict(assignment))

        return course

    def print(self) -> None:
        print(repr(self))

    def add_assignment(self, assignment: Assignment) -> Optional[Assignment]:
        if assignment.name in self.assignments:
            return None

        self.assignments[assignment.name] = assignment
        return assignment

    def remove_assignment(self, name: str) -> Optional[Assignment]:
        return self.assignments.pop(name)

    def calculate_grades(self) -> Dict[str, float]:
        result: Dict[str, float] = {}
        total: float = 0.0
        for assignment in self.assignments.values():
            assignment_total = assignment.calculate_total()
            result[assignment.name] = assignment_total

            total += assignment_total

        result["total"] = total
        return result
