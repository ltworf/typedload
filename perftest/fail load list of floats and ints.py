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

from functools import reduce
from typing import List, NamedTuple, Union
import sys

from common import timeit, raised


class Data(NamedTuple):
    data: List[Union[int, float]]

if sys.argv[1] == '--typedload':
    from typedload import load
    f = lambda: load(data, Data)
if sys.argv[1] == '--jsons':
    from jsons import load
    f = lambda: load(data, Data)
elif sys.argv[1] == '--pydantic':
    import pydantic
    class DataPy(pydantic.BaseModel, smart_union=True):
        data: List[Union[int, float]]
    f = lambda: DataPy(**data)
elif sys.argv[1] == '--apischema':
    import apischema
    apischema.settings.serialization.check_type = True
    # apischema will return a pointer to the same list, which is a bug
    # that can lead to data corruption, but makes it very fast
    # so level the field by copying the list
    def f():
        r = apischema.deserialize(Data, data)
        r.data.copy()
        return r
elif sys.argv[1] == '--dataclass_json':
    from dataclasses import dataclass
    from dataclasses_json import dataclass_json
    @dataclass_json
    @dataclass
    class Data:
        data: List[Union[int, float]]
    f = lambda: Data.from_dict(data)

# Exception test
data = {'data': [1, 0.3, 'qwe']}
assert raised(f)

data = {'data': [1, 0.3]}
assert not raised(f)

# Actual performance test
data = {'data': [i if i % 2 else float(i) for i in range(9000000)] + ['asd']}
print(timeit(lambda: raised(f)))
