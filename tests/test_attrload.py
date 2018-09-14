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

@attr.s
class Mangle:
    value = attr.ib(type=int, metadata={'name': 'va.lue'})

class TestAttrDump(unittest.TestCase):

    def test_basicdump(self):
        assert attrdump(Person()) == {}
        assert attrdump(Person('Alfio')) == {'name': 'Alfio'}
        assert attrdump(Person('Alfio', '33')) == {'name': 'Alfio', 'address': '33'}

    def test_norepr(self):
        @attr.s
        class A:
            i = attr.ib(type=int)
            j = attr.ib(type=int, repr=False)
        assert attrdump(A(1,1)) == {'i': 1}

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

    def test_uuid(self):
        import uuid

        @attr.s
        class A:
            a = attr.ib(type=int)
            uuid_value = attr.ib(type=str, init=False)

            def __attrs_post_init__(self):
                self.uuid_value = str(uuid.uuid4())

        assert type(attrload({'a': 1}, A).uuid_value) == str
        assert attrload({'a': 1}, A) != attrload({'a': 1}, A)


class TestMangling(unittest.TestCase):

    def test_load_metanames(self):
        a = {'va.lue': 12}
        b = a.copy()
        assert attrload(a, Mangle) == Mangle(12)
        assert a == b

    def test_dump_metanames(self):
        assert attrdump(Mangle(12)) == {'va.lue': 12}


class TestAttrExceptions(unittest.TestCase):

    def test_index(self):
        try:
            attrload(
                {
                    'course': 'advanced coursing',
                    'students': [
                        {'name': 'Alfio'},
                        {'name': 'Carmelo', 'address': 'via mulino'},
                        [],
                    ]
                },
                Students,
            )
        except Exception as e:
            assert e.trace[-2].annotation[1] == 'students'
            assert e.trace[-1].annotation[1] == 2
