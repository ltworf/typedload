# typedload
# Copyright (C) 2018-2019 Salvo "LtWorf" Tomaselli
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

from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union
import unittest

from typedload import typechecks


class TestChecks(unittest.TestCase):

    def test_is_list(self):
        assert typechecks.is_list(List)
        assert typechecks.is_list(List[int])
        assert typechecks.is_list(List[str])
        assert not typechecks.is_list(list)
        assert not typechecks.is_list(Tuple[int, str])
        assert not typechecks.is_list(Dict[int, str])

    def test_is_dict(self):
        assert typechecks.is_dict(Dict[int, int])
        assert typechecks.is_dict(Dict)
        assert typechecks.is_dict(Dict[str, str])
        assert not typechecks.is_dict(Tuple[str, str])
        assert not typechecks.is_dict(Set[str])

    def test_is_set(self):
        assert typechecks.is_set(Set[int])
        assert typechecks.is_set(Set)

    def test_is_tuple(self):
        assert typechecks.is_tuple(Tuple[str, int, int])
        assert typechecks.is_tuple(Tuple)

    def test_is_union(self):
        assert typechecks.is_union(Optional[int])
        assert typechecks.is_union(Optional[str])
        assert typechecks.is_union(Union[bytes, str])
        assert typechecks.is_union(Union[str, int, float])
