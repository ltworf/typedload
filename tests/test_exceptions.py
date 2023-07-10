# typedload
# Copyright (C) 2021-2023 Salvo "LtWorf" Tomaselli
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


import enum
from typing import List, NamedTuple, Optional, Tuple, Set, FrozenSet
import unittest

from typedload import dataloader, load, dump, typechecks, exceptions

class Firewall(NamedTuple):
    open_ports: List[int]


class Networking(NamedTuple):
    nic: Optional[str]
    firewall: Firewall


class Remote(NamedTuple):
    networking: Networking


class Config(NamedTuple):
    remote: Optional[Remote]

class Enumeration(enum.Enum):
    A = 1
    B =  '2'
    C = 3.0

class TestExceptionsStr(unittest.TestCase):

    def test_tuple_exceptions(self):
        try:
            load(('1',), Tuple[int, ...], basiccast=False)
        except exceptions.TypedloadException as e:
            assert e._path(e.trace) == '.[0]'
        try:
            load((1, '1',), Tuple[int, ...], basiccast=False)
        except exceptions.TypedloadException as e:
            assert e._path(e.trace) == '.[1]'

        try:
            load(('1'), Tuple[int], basiccast=False)
        except exceptions.TypedloadException as e:
            assert e._path(e.trace) == '.[0]'

        try:
            load(('1', 1), Tuple[int, int], basiccast=False)
        except exceptions.TypedloadException as e:
            assert e._path(e.trace) == '.[0]'
        try:
            load((1, '1'), Tuple[int, int], basiccast=False)
        except exceptions.TypedloadException as e:
            assert e._path(e.trace) == '.[1]'
        try:
            load((1,), Tuple[int, int], basiccast=False)
        except exceptions.TypedloadException as e:
            assert e._path(e.trace) == '.'

    def test_exceptions_str(self):
        incorrect = [
            {'remote': {'networking': {'nic': "eth0", "firewall": {"open_ports":[1,2,3, 'a']}}}},
            {'remote': {'networking': {'nic': "eth0", "firewall": {"closed_ports": [], "open_ports":[1,2,3]}}}},
            {'remote': {'networking': {'noc': "eth0", "firewall": {"open_ports":[2,3]}}}},
            {'romote': {'networking': {'nic': "eth0", "firewall": {"open_ports":[2,3]}}}},
            {'remote': {'nitworking': {'nic': "eth0", "firewall": {"open_ports":[2,3]}}}},
        ]

        paths = []
        for i in incorrect:
            try:
                load(i, Config, basiccast=False, failonextra=True)
                assert False
            except exceptions.TypedloadException as e:
                for i in e.exceptions:
                    paths.append(e._path(e.trace) + '.' + i._path(i.trace[1:]))
        #1st object
        assert paths[0] == '.remote.networking.firewall.open_ports.[3]'
        assert paths[1] == '.remote.'
        #2nd object
        assert paths[2] == '.remote.networking.firewall'
        assert paths[3] == '.remote.'
        #3rd object
        assert paths[4] == '.remote.networking'
        assert paths[5] == '.remote.'
        #4th object
        # Nothing because of no sub-exceptions, fails before the union
        #5th object
        assert paths[6] == '.remote.'
        assert paths[7] == '.remote.'
        assert len(paths) == 8


    def test_tuple_exceptions_str(self):
        incorrect = [
            [1, 1],
            [1, 1, 1],
            [1],
            [1, 1.2],
            [1, None],
            [1, None, 1],
        ]
        for i in incorrect:
            try:
                load(i, Tuple[int, int], basiccast=False, failonextra=True)
            except Exception as e:
                str(e)

    def test_enum_exceptions_str(self):
        incorrect = [
            [1, 1],
            '3',
            12,
        ]
        for i in incorrect:
            try:
                load(i, Enumeration, basiccast=False, failonextra=True)
            except Exception as e:
                str(e)

    def test_nested_wrong_type(self):
        with self.assertRaises(exceptions.TypedloadException):
            load([[1]], List[List[bytes]])
        with self.assertRaises(exceptions.TypedloadException):
            load([[1]], List[Tuple[bytes, ...]])
        with self.assertRaises(exceptions.TypedloadException):
            load([[1]], List[Set[bytes]])
        with self.assertRaises(exceptions.TypedloadException):
            load([[1]], List[FrozenSet[bytes]])

    def test_notiterable_exception(self):
        loader = dataloader.Loader()
        with self.assertRaises(exceptions.TypedloadTypeError):
            loader.load(None, List[int])
        with self.assertRaises(exceptions.TypedloadTypeError):
            loader.load(None, Tuple[int, ...])
        with self.assertRaises(exceptions.TypedloadTypeError):
            loader.load(None, Set[int])
        with self.assertRaises(exceptions.TypedloadTypeError):
            loader.load(None, FrozenSet[int])
