# typedload
# Copyright (C) 2021 Salvo "LtWorf" Tomaselli
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

from typing import Tuple, Union, Literal, NamedTuple
import sys
from dataclasses import dataclass

from typedload import load
import apischema
import pydantic

from common import timeit

class EventMessagePy(pydantic.BaseModel):
    timestamp: float
    type: Literal['message']
    text: str
    sender: str
    receiver: str

class EventFilePy(pydantic.BaseModel):
    timestamp: float
    type: Literal['file']
    filename: str
    sender: str
    receiver: str
    url: str

class EventPingPy(pydantic.BaseModel):
    timestamp: float
    type: Literal['ping']


EventPy = Union[EventMessagePy, EventPingPy, EventFilePy]

class EventListPy(pydantic.BaseModel):
    data: Tuple[EventPy, ...]


class EventMessage(NamedTuple):
    timestamp: float
    type: Literal['message']
    text: str
    sender: str
    receiver: str

class EventFile(NamedTuple):
    timestamp: float
    type: Literal['file']
    filename: str
    sender: str
    receiver: str
    url: str

class EventPing(NamedTuple):
    timestamp: float
    type: Literal['ping']

Event = Union[EventMessage, EventPing, EventFile]


class EventList(NamedTuple):
    data: Tuple[Event, ...]


events = [
    {
        'timestamp': 44.3,
        'type': 'message',
        'text': 'qweqweqweqwe',
        'sender': '3141',
        'receiver': '3145',
    },
    {
        'timestamp': 44.3,
        'type': 'ping',
    },
    {
        'timestamp': 44.3,
        'type': 'file',
        'filename': 'qweqweqweqwe.txt',
        'sender': '3141',
        'receiver': '3145',
        'url': 'http://url',
    },
] * 50000

data = {'data': events}


if sys.argv[1] == '--typedload':
    print(timeit(lambda: load(data, EventList)))
elif sys.argv[1] == '--pydantic':
    print(timeit(lambda: EventListPy(**data)))
elif sys.argv[1] == '--apischema':
    print(timeit(lambda: apischema.deserialize(EventList, data)))
if sys.argv[1] == '--apischema-discriminator':
    try:
        from typing import Annotated
    except ImportError:
        pass
    else:
        discriminator = apischema.discriminator(
            "type", {"message": EventMessage, "ping": EventPing, "file": EventFile}
        )
        class DiscriminatedEventList(NamedTuple):
            data: Tuple[Annotated[Event, discriminator], ...]
        print(timeit(lambda: apischema.deserialize(DiscriminatedEventList, data)))

