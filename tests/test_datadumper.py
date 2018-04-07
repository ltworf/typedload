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

from typedload import datadumper, dataloader, dump, load


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


class TestBasicDump(unittest.TestCase):

    def test_dump_namedtuple(self):
        dumper = datadumper.Dumper()
        assert dumper.dump(NamedA(1, 'a')) == {'a': 1, 'b': 'a'}
        assert dumper.dump(NamedA(1, 'a', 'yes')) == {'a': 1, 'b': 'a', 'c': 'yes'}

    def test_dump_dict(self):
        dumper = datadumper.Dumper()
        assert dumper.dump({EnumA.B: 'ciao'}) == {'2': 'ciao'}

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
