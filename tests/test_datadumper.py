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


from enum import Enum
from ipaddress import IPv4Address, IPv4Network, IPv4Interface, IPv6Address, IPv6Network, IPv6Interface
from pathlib import Path
import re
from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union
import unittest

from typedload import datadumper, dump, load


class EnumA(Enum):
    A: int = 1
    B: str = '2'
    C: Tuple[int, int] = (1, 2)


class NamedA(NamedTuple):
    a: int
    b: str
    c: str = 'no'


class TestDumpLoad(unittest.TestCase):

    def test_enum(self):
        assert load(dump(EnumA.C), EnumA) == EnumA.C


class TestLegacyDump(unittest.TestCase):

    def test_dump(self):
        A = NamedTuple('A',[('a', int), ('b', str)])
        assert dump(A(1, '12')) == {'a': 1, 'b': '12'}


class TestStrconstructed(unittest.TestCase):

    def test_dump_strconstructed(self):
        dumper = datadumper.Dumper()
        class Q:
            def __str__(self):
                return '42'

        dumper.strconstructed.add(Q)
        assert dumper.dump(Q()) == '42'


class TestBasicDump(unittest.TestCase):

    def test_dump_namedtuple(self):
        dumper = datadumper.Dumper()
        assert dumper.dump(NamedA(1, 'a')) == {'a': 1, 'b': 'a'}
        assert dumper.dump(NamedA(1, 'a', 'yes')) == {'a': 1, 'b': 'a', 'c': 'yes'}

        dumper.hidedefault = False
        assert dumper.dump(NamedA(1, 'a')) == {'a': 1, 'b': 'a', 'c': 'no'}

    def test_dump_dict(self):
        dumper = datadumper.Dumper()
        assert dumper.dump({EnumA.B: 'ciao'}) == {'2': 'ciao'}

    def test_dump_set(self):
        dumper = datadumper.Dumper()
        assert dumper.dump(set(range(3))) == [0, 1, 2]
        assert dumper.dump(frozenset(range(3))) == [0, 1, 2]

    def test_dump_enums(self):
        dumper = datadumper.Dumper()
        assert dumper.dump(EnumA.A) == 1
        assert dumper.dump(EnumA.B) == '2'
        assert dumper.dump(EnumA.C) == [1, 2]

    def test_dump_iterables(self):
        dumper = datadumper.Dumper()
        assert dumper.dump([1]) == [1]
        assert dumper.dump((1, 2)) == [1, 2]
        assert dumper.dump([(1, 1), (0, 0)]) == [[1, 1], [0, 0]]
        assert dumper.dump({1, 2}) == [1, 2]

    def test_basic_types(self):
        # Casting enabled, by default
        dumper = datadumper.Dumper()
        assert dumper.dump(1) == 1
        assert dumper.dump('1') == '1'
        assert dumper.dump(None) == None
        dumper.basictypes = {int, str}
        assert dumper.dump('1') == '1'
        assert dumper.dump(1) == 1
        with self.assertRaises(ValueError):
            assert dumper.dump(None) == None
            assert dumper.dump(True) == True


class TestHandlersDumper(unittest.TestCase):

    def test_custom_handler(self):
        class Q:
            def __eq__(self, other):
                return isinstance(other, Q)

        dumper = datadumper.Dumper()
        dumper.handlers.append((
            lambda v: isinstance(v, Q),
            lambda l, v: 12
        ))
        assert dumper.dump(Q()) == 12

    def test_broken_handler(self):
        dumper = datadumper.Dumper()
        dumper.handlers.insert(0, (lambda v: 'a' + v is None, lambda l, v: None))
        with self.assertRaises(TypeError):
            dumper.dump(1)
        dumper.raiseconditionerrors = False
        assert dumper.dump(1) == 1

    def test_replace_handler(self):
        dumper = datadumper.Dumper()
        index = dumper.index([])
        dumper.handlers[index] = (dumper.handlers[index][0], lambda *args: 3)
        assert dumper.dump([11]) == 3


class TestDumper(unittest.TestCase):

    def test_kwargs(self):
        with self.assertRaises(ValueError):
            dump(1, handlers=[])


class TestDumpCommonTypes(unittest.TestCase):

    def test_path(self):
        assert dump(Path('/')) == '/'

    def test_ipaddress(self):
        assert dump(IPv4Address('10.10.10.1')) == '10.10.10.1'
        assert dump(IPv4Network('10.10.10.0/24')) == '10.10.10.0/24'
        assert dump(IPv4Interface('10.10.10.1/24')) == '10.10.10.1/24'
        assert dump(IPv6Address('fe80::123')) == 'fe80::123'
        assert dump(IPv6Network('fe80::/64')) == 'fe80::/64'
        assert dump(IPv6Interface('fe80::123/64')) == 'fe80::123/64'

    def test_pattern(self):
        assert dump(re.compile(r'[bc](at|ot)\d+')) == r'[bc](at|ot)\d+'
        assert dump(re.compile(br'[bc](at|ot)\d+')) == br'[bc](at|ot)\d+'
