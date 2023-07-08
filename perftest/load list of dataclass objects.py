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

from dataclasses import dataclass
import sys

from common import timeit, raised


@dataclass
class Child:
    value: int

@dataclass
class Data:
    data: list[Child]


if sys.argv[1] == '--typedload':
    from typedload import load
    f = lambda: load(data, Data)
elif sys.argv[1] == '--pydantic':
    # Yes pydantic supports dataclasses by having a decorator with the same name as the python one -_-'
    from pydantic.dataclasses import dataclass as dc

    @dc
    class ChildPy:
        value: int

    @dc
    class DataPy:
        data: list[ChildPy]
    f = lambda: DataPy(**data)
elif sys.argv[1] == '--apischema':
    import apischema
    apischema.settings.serialization.check_type = True
    f = lambda: apischema.deserialize(Data, data)

data = {'data': [{'value': i} for i in range(30)]}
assert f().data[1].value == 1

data = {'data': [{'value': 'qwe'} for i in range(30)]}
assert raised(f)

data = {'data': [{'value': i} for i in range(900000)]}
print(timeit(f))

