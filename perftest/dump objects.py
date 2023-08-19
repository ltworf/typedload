# typedload
# Copyright (C) 2022-2023 Salvo "LtWorf" Tomaselli
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
from typing import Literal, Union
import sys

from common import timeit, raised

@dataclass
class Car:
    type: Literal['car']
    name: str
    model: str
    extras: list[str]

@dataclass
class House:
    type: Literal['house']
    address: str
    garden: bool
    bedrooms: int

@dataclass
class Possessions:
    possessions: list[Union[House, Car]]


if sys.argv[1] == '--typedload':
    from typedload import dump
    f = lambda: dump(data)
elif sys.argv[1] == '--jsons':
    from jsons import dump
    f = lambda: dump(data)
elif sys.argv[1] == '--pydantic2':
    import pydantic
    class PPossessions(pydantic.BaseModel):
        possessions: list[Union[House, Car]]
    f = lambda: PPossessions(possessions=data.possessions).dict()
elif sys.argv[1] == '--apischema':
    import apischema
    apischema.settings.serialization.check_type = True
    # apischema will return a pointer to the same list, which is a bug
    # that can lead to data corruption, but makes it very fast
    # so level the field by copying the list
    def f():
        r = apischema.serialize(data)
        return r
elif sys.argv[1] == '--dataclass_json':
    from dataclasses_json import dataclass_json
    @dataclass_json
    @dataclass
    class Possessions:
        possessions: list[Union[House, Car]]
    f = lambda: Possessions(possessions=data.possessions).to_dict()


data = Possessions([
    Car('car',
        f'New {i}',
        str(i // 12) + 'J' if i % 6 == 0 else 'Q',
        [f'Optional {j}' for j in range(i % 40)]
    )
    if i % 2 else
    House('house',
          f'Via Mulini a vento {i}',
          i % 3 == 0,
          i // 4 + 1,
    )

    for i in range(300000)
    ])
print(timeit(f))
