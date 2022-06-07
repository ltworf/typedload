# typedload
# Copyright (C) 2019-2021 Salvo "LtWorf" Tomaselli
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


from typing import TypedDict
import unittest
import sys

from typedload import dataloader, load, dump, typechecks


class Person(TypedDict):
    name: str
    age: float


class A(TypedDict):
    val: str


class B(TypedDict, total=False):
    val: str


class C(A, total=False):
    vel: int


class TestTypeddictLoad(unittest.TestCase):

    def test_mixed_totality(self):

        if sys.version_info.minor == 8:
            # This only works from 3.9
            return

        with self.assertRaises(ValueError):
            load({}, C)
        assert load({'val': 'a'}, C) == {'val': 'a'}
        with self.assertRaises(ValueError):
            load({'val': 'a', 'vel': 'q'}, C)
        assert load({'val': 'a', 'vel': 1}, C) == {'val': 'a', 'vel': 1}
        assert load({'val': 'a', 'vel': '1'}, C) == {'val': 'a', 'vel': 1}
        assert load({'val': 'a','vil': 2}, C) == {'val': 'a'}
        with self.assertRaises(ValueError):
            load({'val': 'a','vil': 2}, C, failonextra=True)

    def test_totality(self):
        with self.assertRaises(ValueError):
            load({}, A)
        assert load({}, B) == {}
        assert load({'val': 'a'}, B) == {'val': 'a'}
        assert load({'vel': 'q'}, B) == {}
        with self.assertRaises(ValueError):
            load({'vel': 'q'}, B, failonextra=True)

    def test_loadperson(self):
        o = {'name': 'pino', 'age': 1.1}
        assert load(o, Person) == o
        assert load({'val': 3}, A) == {'val': '3'}
        assert load({'val': 3, 'vil': 4}, A) == {'val': '3'}

        with self.assertRaises(ValueError):
            o.pop('age')
            load(o, Person)

        with self.assertRaises(ValueError):
            load({'val': 3, 'vil': 4}, A, failonextra=True)

    def test_is_typeddict(self):
        assert typechecks.is_typeddict(A)
        assert typechecks.is_typeddict(Person)
        assert typechecks.is_typeddict(B)


if sys.version_info.minor >= 11:
    # NotRequired is present from 3.11
    from typing import NotRequired

    class TestNotRequired(unittest.TestCase):

        def test_standard(self):

            class A(TypedDict):
                i: int
                o: NotRequired[int]

            assert load({'i': 1}, A) == {'i': 1}
            assert load({'i': 1, 'o': 2}, A) == {'i': 1, 'o': 2}

        def test_nontotal(self):

            class A(TypedDict, total = False):
                i: int
                o: NotRequired[int]

            assert load({}, A) == {}
            assert load({'i': 1}, A) == {'i': 1}
            assert load({'i': 1, 'o': 2}, A) == {'i': 1, 'o': 2}

        def test_mixtotal(self):

            class A(TypedDict):
                a: int
                b: NotRequired[int]

            class B(A, total=False):
                c: int
                d: NotRequired[int]

            with self.assertRaises(ValueError):
                load({}, B)
            assert load({'a': 1}, B) == {'a': 1}
            assert load({'a': 1, 'd':12}, B) == {'a': 1, 'd': 12}
