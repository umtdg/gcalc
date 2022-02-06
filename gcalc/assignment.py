from typing import Dict, List, Union

import gcalc.utils as utils


class Assignment:
    DICT_TYPE = Dict[str, Union[str, float, int, List[float]]]

    def __init__(self,
                 name: str,
                 weight: float,
                 count: int):
        self.name: str = name
        self.weight: float = weight
        self.count: int = count
        self.grades: List[float] = []

    def __str__(self) -> str:
        return f"{self.count} {self.name.title()} ({self.weight}%)"

    def __repr__(self) -> str:
        result: str = ""
        for i in range(len(self.grades)):
            result += f"{self.name} {i + 1}: {self.grades[i]}\n"
        return result

    @property
    def dict(self) -> "Assignment.DICT_TYPE":
        return self.__dict__

    @staticmethod
    def from_dict(d: "Assignment.DICT_TYPE") -> "Assignment":
        utils.check_dict_keys(
            d,
            ["name", "weight", "count"],
            throw=True
        )

        assignment = Assignment(
            d["name"],
            d["weight"],
            d["count"]
        )

        if "grades" in d and \
                isinstance(d["grades"], list) and \
                all(isinstance(grade, (int, float)) for grade in d["grades"]):
            assignment.grades = d["grades"]

        return assignment

    def print(self) -> None:
        print(repr(self))

    def calculate_total(self) -> float:
        if self.count == 0:
            return 0

        return sum(self.grades) * (self.weight / self.count) / 100
