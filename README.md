typedload
=========

Load and dump json-like data into typed data structures in Python3, enforcing
a schema on the data.

This module provides an API to load dictionaries and lists (usually loaded
from json) into Python's NamedTuples, dataclass, sets, enums, and various
other typed data structures; respecting all the type-hints and performing
type checks or casts when needed.

It can also dump from typed data structures to json-like dictionaries and lists.

It is very useful for projects that use Mypy and deal with untyped data
like json, because it guarantees that the data will follow the specified schema.

It is released with a GPLv3 license but [it is possible to ask for LGPLv3](mailto:tiposchi@tiscali.it).

![GPLv3 logo](docs/gpl3logo.png)

Example
=======

For example this dictionary, loaded from a json:

```python
data = {
    'users': [
        {
            'username': 'salvo',
            'shell': 'bash',
            'sessions': ['pts/4', 'tty7', 'pts/6']
        },
        {
            'username': 'lop'
        }
    ],
}
```


Can be treated more easily if loaded into this type:

```python
@dataclasses.dataclass
class User:
    username: str
    shell: str = 'bash'
    sessions: List[str] = dataclasses.field(default_factory=list)

class Logins(NamedTuple):
    users: List[User]
```

And the data can be loaded into the structure with this:

```python
t_data = typedload.load(data, Logins)
```

And then converted back:

```python
data = typedload.dump(t_data)
```

Supported types
===============

Since this is not magic, not all types are supported.

The following things are supported:

 * Basic python types (int, str, bool, float, NoneType)
 * NamedTuple
 * Enum
 * Optional[SomeType]
 * List[SomeType]
 * Dict[TypeA, TypeB]
 * Tuple[TypeA, TypeB, TypeC] and Tuple[SomeType, ...]
 * Set[SomeType]
 * Union[TypeA, TypeB]
 * dataclass (requires Python 3.7)
 * attr.s
 * ForwardRef (Refer to the type in its own definition)
 * Literal (requires Python 3.8)
 * TypedDict (requires Python 3.8)
 * datetime.date, datetime.time, datetime.datetime
 * Path
 * IPv4Address, IPv6Address
 * typing.Any
 * typing.NewType

Using Mypy
==========

Mypy and similar tools work without requiring any plugins.

```python
# This is treated as Any, no checks done.
data = json.load(f)

# This is treated as Dict[str, int]
# but there will be runtime errors if the data does not
# match the expected format
data = json.load(f)  # type: Dict[str, int]

# This is treated as Dict[str, int] and an exception is
# raised if the actual data is not Dict[str, int]
data = typedload.load(json.load(f), Dict[str, int])
```

So when using Mypy, it makes sense to make sure that the type is correct,
rather than hoping the data will respect the format.

Extending
=========

Type handlers can easily be added, and existing ones can be replaced, so the library is fully cusomizable and can work with any type.

Inheriting a base class is not required.

Install
=======

* `pip install typedload`
* `apt install python3-typedload`
* Latest and greatest .deb file is in [releases](https://github.com/ltworf/typedload/releases)

Documentation
=============

* [Online documentation](https://ltworf.github.io/typedload/)
* In the docs/ directory

The tests are hard to read but provide more in depth examples of
the capabilities of this module.

Used by
=======

As dependency, typedload is used by those entities. Feel free to add to the list.

* Several universities around the world (via [Relational](https://ltworf.github.io/relational/))
* People who love IRC (via [localslackirc](https://github.com/ltworf/localslackirc))
* No clue but it gets thousands of downloads per day [according to pypi](https://pypistats.org/packages/typedload)
