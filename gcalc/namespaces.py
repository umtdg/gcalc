from argparse import Namespace

from typing import List


class NsBase(Namespace):
    course: str
    dry_run: bool
    verbose: bool


class NsNew(NsBase):
    replace: bool


class NsShow(NsBase):
    show_grades: bool
    show_all: bool


class NsAddBase(NsBase):
    name: str
    out_of: int
    grades: List[float]


class NsAdd(NsAddBase):
    weight: float
    count: int


class NsEdit(NsAdd):
    update: bool
    append: bool
    rm: bool
