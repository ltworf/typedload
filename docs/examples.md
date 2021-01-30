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

TODO

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

If we want to load from a source and dump from another source that uses a different convention, we can use `mangle_key`

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
