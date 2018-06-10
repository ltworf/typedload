typedload
=========

Dynamic data structures are nice, but they quickly become difficult to work
with, when more static ones are easier to work with but are awkward to use to
exchange data externally.

This is a library to load untyped data (coming from example from a json string)
and convert it into Python's NamedTuple or similar, respecting all the type
hints and performing type checks or casts when needed.

Note that it is released with a GPL license and it cannot be used inside non
GPL software.

Example
=======

For example this dictionary, loaded from a json:

```
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

```
class User(NamedTuple):
    username: str
    shell: str = 'bash'
    sessions: List[str] = []

class Logins(NamedTuple):
    users: List[User]
```

And the data can be loaded into the structure with this:

```
t_data = typedload.load(data, Logins)
```

And then converted back:

```
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
 * Tuple[TypeA, TypeB, TypeC]
 * Set[SomeType]
 * Union[TypeA, TypeB]
 * dataclass (requires Python 3.7)
 * attr (Handled in a built-in plugin)
