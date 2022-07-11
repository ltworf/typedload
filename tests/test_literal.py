# typedload
# Copyright (C) 2019 Salvo "LtWorf" Tomaselli
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


from typing import Literal, NamedTuple, TypedDict
import unittest

from typedload import dataloader, load, dump, typechecks


class TestLiteralLoad(unittest.TestCase):

    def test_literalvalues(self):
        assert isinstance(typechecks.literalvalues(Literal[1]), set)
        assert typechecks.literalvalues(Literal[1]) == {1}
        assert typechecks.literalvalues(Literal[1, 1]) == {1}
        assert typechecks.literalvalues(Literal[1, 2]) == {1, 2}

    def test_load(self):
        l = Literal[1, 2, 'a']
        assert load(1, l) == 1
        assert load(2, l) == 2
        assert load('a', l) == 'a'

    def test_fail(self):
        l = Literal[1, 2, 'a']
        with self.assertRaises(ValueError):
            load(3, l)

    def test_discriminatorliterals_wrong(self):
        assert typechecks.discriminatorliterals(int) == {}

    def test_discriminatorliterals_namedtuple(self):
        class A(NamedTuple):
            t: Literal['a', 'b']
            i: int
            q: str

        class B(NamedTuple):
            t: Literal[33]
            q: Literal[12]
            i: int

        class C(NamedTuple):
            t: Literal['a']
            i: int

        assert typechecks.discriminatorliterals(A) == {'t': {'a', 'b'}}
        assert typechecks.discriminatorliterals(B) == {'t': {33,}, 'q': {12,}}
        assert typechecks.discriminatorliterals(C) == {'t': {'a', }}


    def test_discriminatorliterals_typeddict(self):
        class A(TypedDict):
            t: Literal['a', 'b']
            i: int
            q: str

        class B(TypedDict):
            t: Literal[33]
            q: Literal[12]
            i: int

        class C(TypedDict):
            t: Literal['a']
            i: int

        assert typechecks.discriminatorliterals(A) == {'t': {'a', 'b'}}
        assert typechecks.discriminatorliterals(B) == {'t': {33,}, 'q': {12,}}
        assert typechecks.discriminatorliterals(C) == {'t': {'a', }}
