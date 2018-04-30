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

import attr

from typedload import attrload, attrdump
from typedload import datadumper
from typedload.plugins import attrdump as attrplugin


class Hair(Enum):
    BROWN = 'brown'
    BLACK = 'black'
    BLONDE = 'blonde'
    WHITE = 'white'


@attr.s
class Person:
    name = attr.ib(default='Turiddu', type=str)
    address = attr.ib(type=Optional[str], default=None)


@attr.s
class DetailedPerson(Person):
    hair = attr.ib(type=Hair, default=Hair.BLACK)


@attr.s
class Students:
    course = attr.ib(type=str)
    students = attr.ib(type=List[Person])


class TestAttrDump(unittest.TestCase):

    def test_basicdump(self):
        assert attrdump(Person()) == {}
        assert attrdump(Person('Alfio')) == {'name': 'Alfio'}
        assert attrdump(Person('Alfio', '33')) == {'name': 'Alfio', 'address': '33'}

    def test_dumpdefault(self):
        dumper = datadumper.Dumper()
        attrplugin.add2dumper(dumper)
        dumper.hidedefault = False
        assert dumper.dump(Person()) == {'name': 'Turiddu', 'address': None}

    def test_nesteddump(self):
        assert attrdump(
            Students('advanced coursing', [
            Person('Alfio'),
            Person('Carmelo', 'via mulino'),
        ])) == {
            'course': 'advanced coursing',
            'students': [
                {'name': 'Alfio'},
                {'name': 'Carmelo', 'address': 'via mulino'},
            ]
        }


class TestAttrload(unittest.TestCase):

    def test_basicload(self):
        assert attrload({'name': 'gino'}, Person) == Person('gino')
        assert attrload({}, Person) == Person('Turiddu')

    def test_nestenum(self):
        assert attrload({'hair': 'white'}, DetailedPerson) == DetailedPerson(hair=Hair.WHITE)

    def test_nested(self):
        assert attrload(
            {
                'course': 'advanced coursing',
                'students': [
                    {'name': 'Alfio'},
                    {'name': 'Carmelo', 'address': 'via mulino'},
                ]
            },
            Students,
        ) == Students('advanced coursing', [
            Person('Alfio'),
            Person('Carmelo', 'via mulino'),
        ])
