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

from typing import NamedTuple
import sys

from common import timeit, raised


class Data(NamedTuple):
    data: dict[str, dict[int, str]]


if sys.argv[1] == '--typedload':
    from typedload import load
    f = lambda: load(data, Data)
elif sys.argv[1] == '--jsons':
    from jsons import load
    f = lambda: load(data, Data)
elif sys.argv[1] == '--pydantic':
    import pydantic
    ta = pydantic.TypeAdapter(Data)
    f = lambda: ta.validate_python(data)
elif sys.argv[1] == '--apischema':
    import apischema
    apischema.settings.serialization.check_type = True
    import copy
    # apischema will return a pointer to the same list, which is a bug
    # that can lead to data corruption, but makes it very fast
    # so level the field by copying the list
    def f():
        r = apischema.deserialize(Data, data)
        d = copy.deepcopy(r)
        return d
elif sys.argv[1] == '--dataclass_json':
    from dataclasses import dataclass
    from dataclasses_json import dataclass_json
    @dataclass_json
    @dataclass
    class Data:
        data: dict[str, dict[int, str]]
    f = lambda: Data.from_dict(data)

# Functionality test
data = {'data': { str(k): {i: str(i) for i in range(3)} for k in range(30)}}
assert f().data['0'][0] == '0'

# Test it doesn't just pass any value
data = {'data': {'ciccio', 'asd'}}
assert raised(f)

# Performance test
data = {'data': { str(k): {i: str(i) for i in range(300)} for k in range(30000)}}
print(timeit(f))
