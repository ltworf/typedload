# typedload
# Copyright (C) 2021-2022 Salvo "LtWorf" Tomaselli
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

from typing import List, NamedTuple
import sys

from common import timeit


class Data(NamedTuple):
    data: List[int]


data = {'data': list(range(3000000))}


if sys.argv[1] == '--typedload':
    from typedload import load
    f = lambda: load(data, Data)
    assert f().data[1] == 1
    print(timeit(f))
elif sys.argv[1] == '--pydantic':
    import pydantic
    class DataPy(pydantic.BaseModel):
        data: List[int]
    f = lambda: DataPy(**data)
    assert f().data[1] == 1
    print(timeit(f))
elif sys.argv[1] == '--apischema':
    import apischema
    # apischema will return a pointer to the same list, which is a bug
    # that can lead to data corruption, but makes it very fast
    # so level the field by copying the list
    f = lambda: list(apischema.deserialize(Data, data))
    assert f().data[1] == 1
    print(timeit(f))
elif sys.argv[1] == '--dataclass_json':
    from dataclasses import dataclass
    from dataclasses_json import dataclass_json
    @dataclass_json
    @dataclass
    class Data:
        data: List[int]
    f = lambda: Data.from_dict(data)
    assert f().data[1] == 1
    print(timeit(f))
