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

from typedload import dataloader, load


class TestRealCase(unittest.TestCase):

    def test_stopboard(self):

        class VehicleType(Enum):
            ST = 'ST'
            TRAM = 'TRAM'
            BUS = 'BUS'
            WALK = 'WALK'
            BOAT = 'BOAT'

        class BoardItem(NamedTuple):
            name: str
            type: VehicleType
            date: str
            time: str
            stop: str
            stopid: str
            journeyid: str
            sname: Optional[str] = None
            track: str = ''
            rtDate: Optional[str] = None
            rtTime: Optional[str] = None
            direction: Optional[str] = None
            accessibility: str = ''
            bgColor: str = '#0000ff'
            fgColor: str = '#ffffff'
            stroke: Optional[str] = None
            night: bool = False

        c = {
            'JourneyDetailRef': {'ref': 'https://api.vasttrafik.se/bin/rest.exe/v2/journeyDetail?ref=859464%2F301885%2F523070%2F24954%2F80%3Fdate%3D2018-04-08%26station_evaId%3D5862002%26station_type%3Ddep%26format%3Djson%26'},
            'accessibility': 'wheelChair',
            'bgColor': '#00394d',
            'date': '2018-04-08',
            'direction': 'Kortedala',
            'fgColor': '#fa8719',
            'journeyid': '9015014500604285',
            'name': 'Spårvagn 6',
            'rtDate': '2018-04-08',
            'rtTime': '12:27',
            'sname': '6',
            'stop': 'SKF, Göteborg',
            'stopid': '9022014005862002',
            'stroke': 'Solid',
            'time': '12:17',
            'track': 'B',
            'type': 'TRAM'
        }
        loader = dataloader.Loader()
        loader.load(c, BoardItem)


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
        assert loader.load(None, Optional[str]) is None


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


class TestForwardRef(unittest.TestCase):

    def test_known_refs(self):
        class Node(NamedTuple):
            value: int = 1
            next: Optional['Node'] = None
        l = {'next': {}, 'value': 12}
        loader = dataloader.Loader()
        assert loader.load(l, Node) == Node(value=12,next=Node())


class TestLoaderIndex(unittest.TestCase):

    def test_removal(self):

        loader = dataloader.Loader()
        assert loader.load(3, int) == 3
        loader.handlers.pop(loader.index(int))
        with self.assertRaises(TypeError):
            loader.load(3, int)
