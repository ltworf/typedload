# loadtyped
# Copyright (C) 2018 Salvo "LtWorf" Tomaselli
#
# loadtyped is free software: you can redistribute it and/or modify
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
import unittest

from loadtyped import dataloader


class TestEnum(unittest.TestCase):

    def test_load_enum(self):
        loader = dataloader.Loader()

        class TestEnum(Enum):
            LABEL1 = 1
            LABEL2 = '2'

        assert loader.load(1, TestEnum) == TestEnum.LABEL1
        assert loader.load('2', TestEnum) == TestEnum.LABEL2
        with self.assertRaises(ValueError):
            loader.load(2, TestEnum)


class TestBasicTypes(unittest.TestCase):

    def test_basic_casting(self):
        # Casting enabled, by default
        loader = dataloader.Loader()
        assert loader.load(1, int) == 1
        assert loader.load(1.1, int) == 1
        assert loader.load(False, int) == 0
        assert loader.load('ciao', str) == 'ciao'
        assert loader.load('1', float) == 1.0
        with self.assertRaises(ValueError):
            loader.load('ciao', float)


    def test_extra_basic(self):
        # Add more basic types
        loader = dataloader.Loader()
        with self.assertRaises(TypeError):
            assert loader.load(b'ciao', bytes) == b'ciao'
        loader.basictypes.add(bytes)
        assert loader.load(b'ciao', bytes) == b'ciao'

    def test_basic_nocasting(self):
        # Casting enabled, by default
        loader = dataloader.Loader()
        loader.basiccast = False
        assert loader.load(1, int) == 1
        assert loader.load(True, bool) == True
        assert loader.load(1.5, float) == 1.5
        with self.assertRaises(TypeError):
            assert loader.load(1.1, int) == 1
            assert loader.load(False, int) == 0
            assert loader.load('ciao', str) == 'ciao'
            assert loader.load('1', float) == 1.0
