# typedload
# Copyright (C) 2018 Salvo "LtWorf" Tomaselli
#
# typedload is free software: you can redistribute it and/or modify
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
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>


from enum import Enum
from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union
import unittest

from typedload import dump, load


class Result(Enum):
    PASS = True
    FAIL = False


class Student(NamedTuple):
    name: str
    id: int
    email: Optional[str] = None


class ExamResults(NamedTuple):
    results: List[Tuple[Student, Result]]


class TestDumpLoad(unittest.TestCase):

    def test_dump_load_results(self):
        results = ExamResults(
            [
                (Student('Anna', 1), Result.PASS),
                (Student('Alfio', 2), Result.PASS),
                (Student('Iano', 3, 'iano@iano.it'), Result.PASS),
            ]
        )
        assert load(dump(results), ExamResults) == results
