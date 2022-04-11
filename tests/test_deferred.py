# typedload
# Copyright (C) 2022 Salvo "LtWorf" Tomaselli
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
from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, Optional
import unittest

from typedload import load

class A(NamedTuple):
    a: Optional[int]

@dataclass
class B:
    a: Optional[int]

class TestDeferred(unittest.TestCase):
    '''
    This test should entirely be deleted when the PEP is superseeded.
    '''

    def test_deferred_named_tuple(self):
        assert load({'a': None}, A, pep563=True) == A(None)
        assert load({'a': 3}, A, pep563=True) == A(3)

        with self.assertRaises(ValueError):
            load({'a': None}, A)
        with self.assertRaises(ValueError):
            load({'a': 3}, A)

    def test_deferred_dataclass(self):
        assert load({'a': None}, B, pep563=True) == B(None)
        assert load({'a': 3}, B, pep563=True) == B(3)

        with self.assertRaises(TypeError):
            load({'a': None}, B)
        with self.assertRaises(TypeError):
            load({'a': 3}, B)
