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

from typedload import dataloader, load, dump, typechecks


class Person(TypedDict):
    name: str
    age: float


class A(TypedDict):
    val: str


class B(TypedDict, total=False):
    val: str

class TestTypeddictLoad(unittest.TestCase):

    def test_totality(self):
        with self.assertRaises(ValueError):
            load({}, A)
        assert load({}, B) == {}

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
