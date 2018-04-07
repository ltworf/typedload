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

from typedload import dataloader


class TestUnion(unittest.TestCase):

    def test_ComplicatedUnion(self):
        class A(NamedTuple):
            a: int

        class B(NamedTuple):
            a: str

        class C(NamedTuple):
            val: Union[A, B]

        loader = dataloader.Loader()
        loader.basiccast = False
        assert type(loader.load({'val': {'a': 1}}, C).val) == A
        assert type(loader.load({'val': {'a': '1'}}, C).val) == B


    def test_optional(self):
        loader = dataloader.Loader()
        assert loader.load(1, Optional[int]) == 1
        assert loader.load(None, Optional[int]) == None
        assert loader.load('1', Optional[int]) == 1
        with self.assertRaises(ValueError):
            loader.load('ciao', Optional[int])
            loader.basiccast = False
            loader.load('1', Optional[int])

    def test_union(self):
        loader = dataloader.Loader()
        loader.basiccast = False
        assert loader.load(1, Optional[Union[int, str]]) == 1
        assert loader.load('a', Optional[Union[int, str]]) == 'a'
        assert loader.load(None, Optional[Union[int, str]]) == None
        assert type(loader.load(1, Optional[Union[int, float]])) == int
        assert type(loader.load(1.0, Optional[Union[int, float]])) == float
        with self.assertRaises(ValueError):
            loader.load('', Optional[Union[int, float]])

        loader.basiccast = True
        assert type(loader.load(1, Optional[Union[int, float]])) == int
        assert type(loader.load(1.0, Optional[Union[int, float]])) == float


class TestNamedTuple(unittest.TestCase):

    def test_simple(self):
        class A(NamedTuple):
            a: int
            b: str
        loader = dataloader.Loader()
        r = A(1,'1')
        assert loader.load({'a': 1, 'b': 1}, A) == r
        assert loader.load({'a': 1, 'b': 1, 'c': 3}, A) == r
        loader.failonextra = True
        with self.assertRaises(ValueError):
            loader.load({'a': 1, 'b': 1, 'c': 3}, A)

    def test_simple_defaults(self):
        class A(NamedTuple):
            a: int = 1
            b: str = '1'
        loader = dataloader.Loader()
        r = A(1,'1')
        assert loader.load({}, A) == r

    def test_nested(self):
        class A(NamedTuple):
            a: int

        class B(NamedTuple):
            a: A
        loader = dataloader.Loader()
        r = B(A(1))
        assert loader.load({'a': {'a': 1}}, B) == r
        with self.assertRaises(TypeError):
            loader.load({'a': {'a': 1}}, A)

    def test_fail(self):
        class A(NamedTuple):
            a: int
            q: str
        loader = dataloader.Loader()
        with self.assertRaises(ValueError):
            loader.load({'a': 3}, A)


class TestSet(unittest.TestCase):

    def test_load_set(self):
        loader = dataloader.Loader()
        r = {(1, 1), (2, 2), (0, 0)}
        assert loader.load(zip(range(3), range(3)), Set[Tuple[int,int]]) == r
        assert loader.load([1, '2', 2], Set[int]) == {1, 2}


class TestDict(unittest.TestCase):

    def test_load_dict(self):
        loader = dataloader.Loader()
        class State(Enum):
            OK = 'ok'
            FAILED = 'failed'

        v = {'1': 'ok', '15': 'failed'}
        r = {1: State.OK, 15: State.FAILED}
        assert loader.load(v, Dict[int, State]) == r

    def test_load_nondict(self):

        class SimDict():

            def items(self):
                return zip(range(12), range(12))

        loader = dataloader.Loader()
        assert loader.load(SimDict(), Dict[str, int]) == {str(k): v for k,v in zip(range(12), range(12))}
        with self.assertRaises(AttributeError):
            loader.load(33, Dict[int, str])


class TestTuple(unittest.TestCase):

    def test_load_list_of_tuples(self):
        t = List[Tuple[str, int, Tuple[int, int]]]
        v = [
            ['a', 12, [1, 1]],
            ['b', 15, [3, 2]],
        ]
        r = [
            ('a', 12, (1, 1)),
            ('b', 15, (3, 2)),
        ]
        loader = dataloader.Loader()
        assert loader.load(v, t) == r


    def test_load_nested_tuple(self):
        loader = dataloader.Loader()
        assert loader.load([1, 2, 3, [1, 2]], Tuple[int,int,int,Tuple[str,str]]) == (1, 2, 3, ('1', '2'))

    def test_load_tuple(self):
        loader = dataloader.Loader()

        assert loader.load([1, 2, 3], Tuple[int,int,int]) == (1, 2, 3)
        assert loader.load(['2', False, False], Tuple[int, bool]) == (2, False)

        with self.assertRaises(ValueError):
            loader.load(['2', False], Tuple[int, bool, bool])
            loader.failonextra = True
            assert loader.load(['2', False, False], Tuple[int, bool]) == (2, False)


class TestEnum(unittest.TestCase):

    def test_load_difficult_enum(self):
        class TestEnum(Enum):
            A: int = 1
            B: Tuple[int,int,int] = (1, 2, 3)
        loader = dataloader.Loader()
        assert loader.load(1, TestEnum) == TestEnum.A
        assert loader.load((1, 2, 3), TestEnum) == TestEnum.B
        assert loader.load([1, 2, 3], TestEnum) == TestEnum.B
        assert loader.load([1, 2, 3, 4], TestEnum) == TestEnum.B
        loader.failonextra = True
        with self.assertRaises(ValueError):
            loader.load([1, 2, 3, 4], TestEnum)

    def test_load_enum(self):
        loader = dataloader.Loader()

        class TestEnum(Enum):
            LABEL1 = 1
            LABEL2 = '2'

        assert loader.load(1, TestEnum) == TestEnum.LABEL1
        assert loader.load('2', TestEnum) == TestEnum.LABEL2
        with self.assertRaises(ValueError):
            loader.load(2, TestEnum)
        assert loader.load(['2', 1], Tuple[TestEnum, TestEnum]) == (TestEnum.LABEL2, TestEnum.LABEL1)


class TestBasicTypes(unittest.TestCase):

    def test_basic_casting(self):
        # Casting enabled, by default
        loader = dataloader.Loader()
        assert loader.load(1, int) == 1
        assert loader.load(1.1, int) == 1
        assert loader.load(False, int) == 0
        assert loader.load('ciao', str) == 'ciao'
        assert loader.load('1', float) == 1.0
        with self.assertRaises(ValueError):
            loader.load('ciao', float)

    def test_list_basic(self):
        loader = dataloader.Loader()
        assert loader.load(range(12), List[int]) == list(range(12))
        assert loader.load(range(12), List[str]) == [str(i) for i in range(12)]

    def test_extra_basic(self):
        # Add more basic types
        loader = dataloader.Loader()
        with self.assertRaises(TypeError):
            assert loader.load(b'ciao', bytes) == b'ciao'
        loader.basictypes.add(bytes)
        assert loader.load(b'ciao', bytes) == b'ciao'

    def test_none_basic(self):
        loader = dataloader.Loader()
        loader.load(None, type(None))
        with self.assertRaises(ValueError):
            loader.load(12, type(None))

    def test_basic_nocasting(self):
        # Casting enabled, by default
        loader = dataloader.Loader()
        loader.basiccast = False
        assert loader.load(1, int) == 1
        assert loader.load(True, bool) == True
        assert loader.load(1.5, float) == 1.5
        with self.assertRaises(TypeError):
            loader.load(1.1, int)
            loader.load(False, int)
            loader.load('ciao', str)
            loader.load('1', float)
