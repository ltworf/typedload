# typedload
# Copyright (C) 2018-2023 Salvo "LtWorf" Tomaselli
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


import argparse
from enum import Enum
from ipaddress import IPv4Address, IPv6Address, IPv6Network, IPv4Network, IPv4Interface, IPv6Interface
from pathlib import Path
import re
import sys
import typing
from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union, Any, NewType, FrozenSet
import unittest

from typedload import dataloader, load, exceptions


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


class TestStrconstructed(unittest.TestCase):

    def test_load_strconstructed(self):
        loader = dataloader.Loader()
        class Q:
            def __init__(self, p):
                self.param = p

        loader.strconstructed.add(Q)
        data = loader.load('42', Q)
        assert data.param == '42'


class TestUnion(unittest.TestCase):
    def test_json(self):
        '''
        This test would normally be flaky, but with the scoring of
        types in union, it should always work.
        '''
        Json = Union[int, float, str, bool, None, List['Json'], Dict[str, 'Json']]
        data = [{},[]]

        loader = dataloader.Loader()
        loader.basiccast = False
        loader.frefs = {'Json' : Json}

        assert loader.load(data, Json) == data

    def test_str_obj(self):
        '''
        Possibly flaky test. Testing automatic type sorting in Union

        It depends on python internal magic of sorting the union types
        '''
        loader = dataloader.Loader()

        class Q(NamedTuple):
            a: int
        expected = Q(12)
        for _ in range(5000):
            t = eval('Union[str, Q]')
            assert loader.load({'a': 12}, t) == expected


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

    def test_debug_union(self):
        loader = dataloader.Loader()

        class A(NamedTuple):
            a: int
        class B(NamedTuple):
            a: int

        assert isinstance(loader.load({'a': 1}, Union[A, B]), (A, B))
        loader.uniondebugconflict = True
        with self.assertRaises(TypeError):
            loader.load({'a': 1}, Union[A, B])


class TestFastIterableLoad(unittest.TestCase):

    def yielder(self):
        yield from range(2)
        yield "1"

    def test_tupleload_from_generator_with_exception(self):
        loader = dataloader.Loader(basiccast=False)

        with self.assertRaises(exceptions.TypedloadValueError):
            a = loader.load(self.yielder(), Tuple[int, ...])

        with self.assertRaises(exceptions.TypedloadValueError):
            a = loader.load(self.yielder(), Tuple[Union[float, int], ...])

        loader = dataloader.Loader(basiccast=True)
        assert loader.load(self.yielder(), Tuple[int, ...]) == (0, 1, 1)
        assert loader.load(self.yielder(), Tuple[Union[float, int], ...]) == (0, 1, 1)
        assert loader.load(self.yielder(), Tuple[Union[str, int], ...]) == (0, 1, '1')

    def test_listload_from_generator_with_exception(self):
        loader = dataloader.Loader(basiccast=False)

        with self.assertRaises(exceptions.TypedloadValueError):
            a = loader.load(self.yielder(), List[int])

        with self.assertRaises(exceptions.TypedloadValueError):
            a = loader.load(self.yielder(), List[Union[int, float]])

        loader = dataloader.Loader(basiccast=True)
        assert loader.load(self.yielder(), List[int]) == [0, 1, 1]
        assert loader.load(self.yielder(), List[Union[float, int]]) == [0, 1, 1]
        assert loader.load(self.yielder(), List[Union[int, str]]) == [0, 1, "1"]

    def test_frozensetload_from_generator_with_exception(self):
        loader = dataloader.Loader(basiccast=False)

        with self.assertRaises(exceptions.TypedloadValueError):
            a = loader.load(self.yielder(), FrozenSet[int])

        loader = dataloader.Loader(basiccast=True)
        assert loader.load(self.yielder(), FrozenSet[int]) == frozenset((0, 1, 1))

    def test_setload_from_generator_with_exception(self):
        loader = dataloader.Loader(basiccast=False)

        with self.assertRaises(exceptions.TypedloadValueError):
            a = loader.load(self.yielder(), Set[int])

        with self.assertRaises(exceptions.TypedloadValueError):
            a = loader.load(self.yielder(), Set[Union[int, float]])

        loader = dataloader.Loader(basiccast=True)
        assert loader.load(self.yielder(), Set[int]) == {0, 1, 1}
        assert loader.load(self.yielder(), Set[Union[float, int]]) == {0, 1, 1}
        assert loader.load(self.yielder(), Set[Union[int, str]]) == {0, 1, "1"}

class TestTupleLoad(unittest.TestCase):

    def test_ellipsis(self):
        loader = dataloader.Loader()

        l = list(range(33))
        t = tuple(l)
        assert loader.load(l, Tuple[int, ...]) == t
        assert loader.load('abc', Tuple[str, ...]) == ('a', 'b', 'c')
        assert loader.load('a', Tuple[str, ...]) == ('a', )

    def test_tuple(self):
        loader = dataloader.Loader()

        with self.assertRaises(ValueError):
            assert loader.load([1], Tuple[int, int]) == (1, 2)

        assert loader.load([1, 2, 3], Tuple[int, int]) == (1, 2)
        loader.failonextra = True
        # Now the same will fail
        with self.assertRaises(ValueError):
            loader.load([1, 2, 3], Tuple[int, int]) == (1, 2)



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

    def test_disable(self):
        class A(NamedTuple):
            i: 'int'
        loader = dataloader.Loader(frefs=None)
        with self.assertRaises(Exception):
            loader.load(3, A)

    def test_add_fref(self):
        class A(NamedTuple):
            i: 'alfio'
        loader = dataloader.Loader()
        with self.assertRaises(ValueError):
            loader.load({'i': 3}, A)
        loader.frefs['alfio'] = int
        assert loader.load({'i': 3}, A) == A(3)



class TestLoaderIndex(unittest.TestCase):

    def test_removal(self):

        loader = dataloader.Loader()
        assert loader.load(3, int) == 3
        loader = dataloader.Loader()
        loader.handlers.pop(loader.index(int))
        with self.assertRaises(TypeError):
            loader.load(3, int)


class TestExceptions(unittest.TestCase):
    def test_dict_is_not_list(self):
        loader = dataloader.Loader()
        with self.assertRaises(exceptions.TypedloadTypeError):
            loader.load({1: 1}, List[int])
        with self.assertRaises(exceptions.TypedloadTypeError):
            loader.load({1: 1}, Tuple[int, ...])
        with self.assertRaises(exceptions.TypedloadTypeError):
            loader.load({1: 1}, Set[int])

    def test_dict_exception(self):
        loader = dataloader.Loader()
        with self.assertRaises(exceptions.TypedloadAttributeError):
            loader.load(None, Dict[int, int])

    def test_index(self):
        loader = dataloader.Loader()
        try:
            loader.load([1, 2, 3, 'q'], List[int])
        except Exception as e:
            assert e.trace[-1].annotation[1] == 3

        try:
            loader.load(['q', 2], Tuple[int,int])
        except Exception as e:
            assert e.trace[-1].annotation[1] == 0

        try:
            loader.load({'q': 1}, Dict[int,int])
        except Exception as e:
            assert e.trace[-1].annotation[1] == 'q'

    def test_attrname(self):
        class A(NamedTuple):
            a: int
        class B(NamedTuple):
            a: A
            b: int
        loader = dataloader.Loader()

        try:
            loader.load({'a': 'q'}, A)
        except Exception as e:
            assert e.trace[-1].annotation[1] == 'a'

        try:
            loader.load({'a':'q','b': {'a': 1}}, B)
        except Exception as e:
            assert e.trace[-1].annotation[1] == 'a'

        try:
            loader.load({'a':3,'b': {'a': 'q'}}, B)
        except Exception as e:
            assert e.trace[-1].annotation[1] == 'a'

    def test_typevalue(self):
        loader = dataloader.Loader()
        try:
            loader.load([1, 2, 3, 'q'], List[int])
        except Exception as e:
            assert e.value == 'q'
            assert e.type_ == int


class TestDictEquivalence(unittest.TestCase):

    def test_namespace(self):
        loader = dataloader.Loader()
        data = argparse.Namespace(a=12, b='33')
        class A(NamedTuple):
            a: int
            b: int
            c: int = 1
        assert loader.load(data, A) == A(12, 33, 1)
        assert loader.load(data, Dict[str, int]) == {'a': 12, 'b': 33}

    def test_nonamespace(self):
        loader = dataloader.Loader(dictequivalence=False)
        data = argparse.Namespace(a=1)
        with self.assertRaises(AttributeError):
            loader.load(data, Dict[str, int])


class TestCommonTypes(unittest.TestCase):

    def test_path(self):
        loader = dataloader.Loader()
        assert loader.load('/', Path) == Path('/')

    def test_pattern_str(self):
        loader = dataloader.Loader()
        if sys.version_info[:2] <= (3, 8):
            with self.assertRaises(TypeError):
                assert loader.load(r'[bc](at|ot)\d+', re.Pattern[str])
        else:
            assert loader.load(r'[bc](at|ot)\d+', re.Pattern[str]) == re.compile(r'[bc](at|ot)\d+')
        assert loader.load(r'[bc](at|ot)\d+', typing.Pattern[str]) == re.compile(r'[bc](at|ot)\d+')

    def test_pattern_bytes(self):
        loader = dataloader.Loader()
        if sys.version_info[:2] <= (3, 8):
            with self.assertRaises(TypeError):
                assert loader.load(br'[bc](at|ot)\d+', re.Pattern[bytes])
        else:
            assert loader.load(br'[bc](at|ot)\d+', re.Pattern[bytes]) == re.compile(br'[bc](at|ot)\d+')
        assert loader.load(br'[bc](at|ot)\d+', typing.Pattern[bytes]) == re.compile(br'[bc](at|ot)\d+')

    def test_pattern(self):
        loader = dataloader.Loader()
        assert loader.load(r'[bc](at|ot)\d+', re.Pattern) == re.compile(r'[bc](at|ot)\d+')
        assert loader.load(br'[bc](at|ot)\d+', re.Pattern) == re.compile(br'[bc](at|ot)\d+')
        assert loader.load(r'[bc](at|ot)\d+', typing.Pattern) == re.compile(r'[bc](at|ot)\d+')
        assert loader.load(br'[bc](at|ot)\d+', typing.Pattern) == re.compile(br'[bc](at|ot)\d+')

        # Right type, invalid value
        with self.assertRaises(exceptions.TypedloadException) as e:
            assert loader.load(r'((((((', re.Pattern)
        with self.assertRaises(exceptions.TypedloadException) as e:
            assert loader.load(br'((((((', re.Pattern)
        with self.assertRaises(exceptions.TypedloadException) as e:
            assert loader.load(r'((((((', typing.Pattern)
        with self.assertRaises(exceptions.TypedloadException) as e:
            assert loader.load(br'((((((', typing.Pattern)
        with self.assertRaises(exceptions.TypedloadException) as e:
            assert loader.load(r'(?P<my_group>[bc])(?P<my_group>(at|ot))\d+', re.Pattern)
        with self.assertRaises(exceptions.TypedloadException) as e:
            assert loader.load(br'(?P<my_group>[bc])(?P<my_group>(at|ot))\d+', re.Pattern)
        with self.assertRaises(exceptions.TypedloadException) as e:
            assert loader.load(r'(?P<my_group>[bc])(?P<my_group>(at|ot))\d+', typing.Pattern)
        with self.assertRaises(exceptions.TypedloadException) as e:
            assert loader.load(br'(?P<my_group>[bc])(?P<my_group>(at|ot))\d+', typing.Pattern)

        # Wrong type
        with self.assertRaises(exceptions.TypedloadTypeError) as e:
            assert loader.load(33, re.Pattern)
        with self.assertRaises(exceptions.TypedloadTypeError) as e:
            assert loader.load(33, typing.Pattern)
        with self.assertRaises(exceptions.TypedloadTypeError) as e:
            assert loader.load(False, re.Pattern)
        with self.assertRaises(exceptions.TypedloadTypeError) as e:
            assert loader.load(False, typing.Pattern)
        with self.assertRaises(exceptions.TypedloadTypeError) as e:
            assert loader.load(None, re.Pattern)
        with self.assertRaises(exceptions.TypedloadTypeError) as e:
            assert loader.load(None, typing.Pattern)

    def test_ipaddress(self):
        loader = dataloader.Loader()
        assert loader.load('10.10.10.1', IPv4Address) == IPv4Address('10.10.10.1')
        assert loader.load('10.10.10.1', IPv4Network) == IPv4Network('10.10.10.1/32')
        assert loader.load('10.10.10.1', IPv4Interface) == IPv4Interface('10.10.10.1/32')
        assert loader.load('fe80::123', IPv6Address) == IPv6Address('fe80::123')
        assert loader.load('10.10.10.0/24', IPv4Network) == IPv4Network('10.10.10.0/24')
        assert loader.load('fe80::/64', IPv6Network) == IPv6Network('fe80::/64')
        assert loader.load('10.10.10.1/24', IPv4Interface) == IPv4Interface('10.10.10.1/24')
        assert loader.load('fe80::123/64', IPv6Interface) == IPv6Interface('fe80::123/64')

        # Wrong IP version
        with self.assertRaises(ValueError):
            loader.load('10.10.10.1', IPv6Address)
        with self.assertRaises(ValueError):
            loader.load('fe80::123', IPv4Address)
        with self.assertRaises(ValueError):
            loader.load('10.10.10.0/24', IPv6Network)
        with self.assertRaises(ValueError):
            loader.load('fe80::123', IPv4Network)
        with self.assertRaises(ValueError):
            loader.load('10.10.10.1/24', IPv6Interface)
        with self.assertRaises(ValueError):
            loader.load('fe80::123/64', IPv4Interface)

        # Wrong ipaddress type
        with self.assertRaises(ValueError):
            loader.load('10.10.10.1/24', IPv4Address)
        with self.assertRaises(ValueError):
            loader.load('10.10.10.1/24', IPv4Network)


class TestAny(unittest.TestCase):

    def test_any(self):
        loader = dataloader.Loader()
        o = object()
        assert loader.load(o, Any) is o


class TestNewType(unittest.TestCase):

    def test_newtype(self):
        loader = dataloader.Loader()
        Foo = NewType("Foo", str)
        bar = loader.load("bar", Foo)
        assert bar == "bar"
        assert type(bar) is str
