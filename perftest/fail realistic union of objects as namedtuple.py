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

from typing import Tuple, Union, Literal, NamedTuple
import sys
from dataclasses import dataclass

from common import timeit, raised

@dataclass(frozen=True)
class EventMessage:
    timestamp: float
    type: Literal['message']
    text: str
    sender: str
    receiver: str

@dataclass(frozen=True)
class EventFile:
    timestamp: float
    type: Literal['file']
    filename: str
    sender: str
    receiver: str
    url: str

@dataclass(frozen=True)
class EventPing:
    timestamp: float
    type: Literal['ping']

@dataclass
class EventEnter:
    type: Literal['enter']
    timestamp: float
    sender: str
    room: int

@dataclass
class EventExit:
    type: Literal['exit']
    timestamp: float
    sender: str
    room: int

Event = Union[EventMessage, EventPing, EventFile, EventEnter, EventExit]


class EventList(NamedTuple):
    data: Tuple[Event, ...]


events = [
    {
        'timestamp': 13,
        'type': 'exit',
        'sender': 'asdsd',
        'room': 42,
    },
    {
        'timestamp': 11,
        'type': 'enter',
        'sender': 'asdasd',
        'room': 42,
    },
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
]

if sys.argv[1] == '--typedload':
    from typedload import load
    f = lambda: load(data, EventList)
elif sys.argv[1] == '--jsons':
    from jsons import load
    f = lambda: load(data, EventList)
elif sys.argv[1] == '--pydantic2':
    import pydantic
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
    class EventEnterPy(pydantic.BaseModel):
        type: Literal['enter']
        timestamp: float
        sender: str
        room: int
    class EventExitPy(pydantic.BaseModel):
        type: Literal['exit']
        timestamp: float
        sender: str
        room: int
    EventPy = Union[EventExitPy, EventEnterPy,EventMessagePy, EventPingPy, EventFilePy]
    class EventListPy(pydantic.BaseModel):
        data: Tuple[EventPy, ...]
    f = lambda: EventListPy(**data)
elif sys.argv[1] == '--apischema':
    import apischema
    apischema.settings.serialization.check_type = True
    f = lambda: apischema.deserialize(EventList, data)
elif sys.argv[1] == '--dataclass_json':
    from dataclasses_json import dataclass_json
    @dataclass_json
    @dataclass
    class EventList:
        data: Tuple[Event, ...]
    f = lambda: EventList.from_dict(data)
elif sys.argv[1] == '--apischema-discriminator':
    import apischema
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
        f = lambda: apischema.deserialize(DiscriminatedEventList, data)

data = {'data': events + [{}]}
assert raised(f)

data = {'data': events}
assert not raised(f)

data = {'data': events * 50000 + [{}]}
print(timeit(lambda: raised(f)))

