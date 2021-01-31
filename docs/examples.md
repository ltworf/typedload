Examples
========

Objects
-------

TODO

Optional values
---------------

TODO

Unions
------

### Disable cast

TODO

### List or single object

Some terribly evil programmers use json in this way:

* A list in case they have multiple values
* A single object in case they have one value
* Nothing at all in case they have zero values

Let's see how typedload can help us survive the situation without having to handle all the cases every time.

```python
import typedload
from typing import NamedTuple, Union, List
import dataclasses

# Multiple data points, a list is used
data0 = {
    "data_points": [{"x": 1.4, "y": 4.1}, {"x": 5.2, "y": 6.13}]
}

# A single data point. Instead of a list of 1 element, the element is passed directly
data1 = {
    "data_points": {"x": 1.4, "y": 4.1}
}

# No data points. Instead of an empty list, the object is empty
data2 = {}

# Now we make our objects
class Point(NamedTuple):
    x: float
    y: float

@dataclasses.dataclass
class Data:
    # We make an hidden field to load the data_points field from the json
    # If the value is absent it will default to an empty list
    # The hidden field can either be a List[Point] or directly a Point object
    _data_points: Union[Point, List[Point]] = dataclasses.field(default_factory=list, metadata={'name': 'data_points'})

    @property
    def data_points(self) -> List[Point]:
        # We make a property called data_points, that always returns a list
        if not isinstance(self._data_points, list):
            return [self._data_points]
        return self._data_point

# Now we can load our data, and they will all be lists of Point
typedload.load(data0, Data).data_points
typedload.load(data1, Data).data_points
typedload.load(data2, Data).data_points
```

### Objects

TODO

### Object type in value

Let's assume that our json objects contain a *type* field that names the object itself. Slack sends events in this way for example.

```python
import typedload
from typing import List, Literal, Union, NamedTuple

events = [
    {
    "type": "message",
    "text": "hello"
    },
    {
    "type": "user-joined",
    "username": "giufà"
    }
]

# We have events that can be of many types

class Message(NamedTuple):
    type: Literal['message']
    text: str

class UserJoined(NamedTuple):
    type: Literal['user-joined']
    username: str

# Now to load our event list
typedload.load(events, List[Union[Message, UserJoined]])
```


Name mangling
-------------

Name mangling is primarily used to deal with camel-case in codebases that use snake_case.

It is supported using `dataclass` and `attrs`, which provide metadata for the fields.

Let's assume that our original data uses camel case.

Since we are not maniacs, we want the fields in python to use snake_case, we do the following:

```python
from dataclasses import dataclass, field
import typedload

@dataclass
class Character:
    first_name: str = field(metadata={'name': 'firstName'})
    last_name: str = field(metadata={'name': 'lastName'})

data = {"firstName": "Paolino", "lastName": "Paperino"}

character = typedload.load(data, Character)
```

When dumping back the data

```python
typedload.dump(character)
```

the names will be converted back to camel case.


### Multiple name mangling schemes

If we want to load from a source and dump to another source that uses a different convention, we can use `mangle_key`

```python
from dataclasses import dataclass, field
import typedload

@dataclass
class Character:
    first_name: str = field(metadata={'name': 'firstName', 'alt_name': 'first-name'})
    last_name: str = field(metadata={'name': 'lastName', 'alt_name': 'last-name'})

data = {"firstName": "Paolino", "lastName": "Paperino"}

character = typedload.load(data, Character)
typedload.dump(character, mangle_key='alt_name')
```

Custom handlers
---------------

TODO

Exceptions
----------

TODO
