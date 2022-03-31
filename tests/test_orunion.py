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


import unittest

from typedload import dataloader, load, dump, typechecks


class TestOrUnion(unittest.TestCase):
    '''
    From Python3.10 unions can be written as A | B.

    That is a completely different internal than Union[A, B]
    '''

    def test_typechecker(self):
        assert typechecks.is_union(int | str)
        assert not typechecks.is_union(2 | 1)

    def test_uniontypes(self):
        u = int | str | float
        assert int in typechecks.uniontypes(u)
        assert str in typechecks.uniontypes(u)
        assert float in typechecks.uniontypes(u)
        assert bytes not in typechecks.uniontypes(u)
        assert bool not in typechecks.uniontypes(u)

    def test_loadnewunion(self):
        t = list[int] | str
        assert load('ciao', t) == 'ciao'
        assert load(['1', 1.0, 0], t) == [1, 1, 0]
        assert load(('1', 1.0, 0), t) == [1, 1, 0]
