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


class TestDatetimedump(unittest.TestCase):
    def test_isodatetime(self):
        dumper = datadumper.Dumper(isodates=True)
        assert dumper.dump(datetime.date(2011, 12, 12)) == '2011-12-12'
        assert dumper.dump(datetime.time(15, 41)) == '15:41:00'
        assert dumper.dump(datetime.datetime(2019, 5, 31, 12, 44, 22)) == '2019-05-31T12:44:22'
        assert dumper.dump(datetime.datetime(2023, 3, 20, 7, 43, 19, 906439, tzinfo=datetime.timezone.utc)) == '2023-03-20T07:43:19.906439+00:00'

    def test_datetime(self):
        dumper = datadumper.Dumper()
        assert dumper.dump(datetime.date(2011, 12, 12)) == [2011, 12, 12]
        assert dumper.dump(datetime.time(15, 41)) == [15, 41, 0, 0]
        assert dumper.dump(datetime.datetime(2019, 5, 31, 12, 44, 22)) == [2019, 5, 31, 12, 44, 22, 0]

class TestDatetimeLoad(unittest.TestCase):
    def test_isoload(self):
        now = datetime.datetime.now()
        assert load(now.isoformat(), datetime.datetime) == now

        withtz = datetime.datetime(2023, 3, 20, 7, 43, 19, 906439, tzinfo=datetime.timezone.utc)
        assert load(withtz.isoformat(), datetime.datetime) == withtz

        date = datetime.date(2023, 4, 1)
        assert load(date.isoformat(), datetime.date) == date

        time = datetime.time(23, 44, 12)
        assert load(time.isoformat(), datetime.time) == time

    def test_date(self):
        loader = dataloader.Loader()
        assert loader.load((2011, 1, 1), datetime.date) == datetime.date(2011, 1, 1)
        assert loader.load((15, 33), datetime.time) == datetime.time(15, 33)
        assert loader.load((15, 33, 0), datetime.time) == datetime.time(15, 33)
        assert loader.load((2011, 1, 1), datetime.datetime) == datetime.datetime(2011, 1, 1)
        assert loader.load((2011, 1, 1, 22), datetime.datetime) == datetime.datetime(2011, 1, 1, 22)

        # Same but with lists
        assert loader.load([2011, 1, 1], datetime.date) == datetime.date(2011, 1, 1)
        assert loader.load([15, 33], datetime.time) == datetime.time(15, 33)
        assert loader.load([15, 33, 0], datetime.time) == datetime.time(15, 33)
        assert loader.load([2011, 1, 1], datetime.datetime) == datetime.datetime(2011, 1, 1)
        assert loader.load([2011, 1, 1, 22], datetime.datetime) == datetime.datetime(2011, 1, 1, 22)

    def test_exception(self):
        loader = dataloader.Loader()
        with self.assertRaises(TypeError):
            loader.load((2011, ), datetime.datetime)
            loader.load(33, datetime.datetime)


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
