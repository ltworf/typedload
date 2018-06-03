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


from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union
import unittest

from typedload import dataloader, load, dump


class TestDataclassLoad(unittest.TestCase):

    def test_load(self):
        @dataclass
        class A:
            a: int
            b: str
        assert load({'a': 101, 'b': 'ciao'}, A) == A(101, 'ciao')

    def test_nestedload(self):
        @dataclass
        class A:
            a: int
            b: str
        @dataclass
        class B:
            a: A
            b: List[A]

        assert load({'a': {'a': 101, 'b': 'ciao'}, 'b': []}, B) == B(A(101, 'ciao'), [])
        assert load(
            {'a': {'a': 101, 'b': 'ciao'}, 'b': [{'a': 1, 'b': 'a'},{'a': 0, 'b': 'b'}]},
            B
        ) == B(A(101, 'ciao'), [A(1, 'a'),A(0, 'b')])

class TestDataclassUnion(unittest.TestCase):

    def test_ComplicatedUnion(self):
        @dataclass
        class A:
            a: int
        @dataclass
        class B:
            a: str
        @dataclass
        class C:
            val: Union[A, B]
        loader = dataloader.Loader()
        loader.basiccast = False
        assert type(loader.load({'val': {'a': 1}}, C).val) == A
        assert type(loader.load({'val': {'a': '1'}}, C).val) == B

class TestDataclassDump(unittest.TestCase):

    def test_dump(self):
        @dataclass
        class A:
            a: int
            b: int = 0

        assert dump(A(12)) == {'a': 12}
        assert dump(A(12), hidedefault=False) == {'a': 12, 'b': 0}
