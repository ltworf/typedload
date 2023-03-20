# typedload
# Copyright (C) 2023 Salvo "LtWorf" Tomaselli
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

import datetime
import unittest

from typedload import load, dump, dataloader, datadumper


class TestTimedelta(unittest.TestCase):

    def test_findhandlers(self):
        l = dataloader.Loader()
        d = datadumper.Dumper()

        l.index(datetime.timedelta)
        d.index(datetime.timedelta(1))

    def test_dumpdelta(self):
        assert dump(datetime.timedelta(0, 1)) == 1.0
        assert dump(datetime.timedelta(1, 1)) == 86400 + 1
        assert dump(datetime.timedelta(3, 0.1)) == 86400 * 3 + 0.1

    def test_loaddelta(self):
        assert load(1.0, datetime.timedelta) == datetime.timedelta(0, 1)
        assert load(86400, datetime.timedelta) == datetime.timedelta(1, 0)
        assert load(86400.0, datetime.timedelta) == datetime.timedelta(1, 0)

    def test_loaddump(self):
        for i in [(0, 1), (2,12), (9, 50), (600, 0.4), (1000, 501)]:
            delta = datetime.timedelta(*i)
            assert load(dump(delta), datetime.timedelta) == delta
