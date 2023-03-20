Supported types
===============

None
----

```python
typedload.load(obj, None)
```

It will either return a None or fail.

This is normally used to handle unions such as `Optional[int]` rather than by itself.

Basic types
-----------

By default: `{int, bool, float, str, NONETYPE}`

Those types are the basic building blocks and no operations are performed on them.

*NOTE*: If `basiccast=True` (the default) casting between them can still happen.

```python
In : typedload.load(1, float)
Out: 1.0

In : typedload.load(1, str)
Out: '1'

In : typedload.load(1, int)
Out: 1

In : typedload.load(1, float, basiccast=False)
Exception: TypedloadValueError

In : typedload.load(1, bool, basiccast=False)
Exception: TypedloadValueError
```

The `basictypes` set can be tweaked.

```python
In : typedload.load(1, bytes, basictypes={bytes, int})
Out: b'\x00'

In : typedload.load(1, int, basictypes={bytes, int})
Out: 1
```

typing.Literal
--------------

```python
typedload.load(obj, Literal[1])
typedload.load(obj, Literal[1,2,3])
```

Succeeds only if obj equals one of the allowed values.

This is normally used in objects, to decide the correct type in a `Union`.

It is very common to use Literal to disambiguate objects in a Union. [See example](examples.md#object-type-in-value)

*This is very fast, because typedload will internally use the `Literal` values to try the best type in the union first.*

enum.Enum
---------

```python
class Flags(Enum):
    NOVAL = 0
    YESVAL = 1

In : typedload.load(1, Flags)
Out: <Flags.YESVAL: 1>


```

Load values from an Enum, when dumping the value is used.

typing.List
-----------

```python
In : typedload.load([1, 2, 3], List[int])
Out: [1, 2, 3]

In : typedload.load([1.1, 2, '3'], List[int])
Out: [1, 2, 3]

In : typedload.load([1.1, 2, '3'], List[int], basiccast=False)
Exception: TypedloadValueError
```

Load an iterable into a list object.

Always dumped as a list.

typing.Tuple
------------

Always dumped as a list.

### Finite size tuple

```python
In : typedload.load([1, 2, 3], Tuple[int, float])
Out: (1, 2.0)

# Be more strict and fail if there is more data than expected on the iterator
In : typedload.load([1, 2, 3], Tuple[int, float], failonextra=True)
Exception: TypedloadValueError
```

### Infinite size tuple

```python
In : typedload.load([1, 2, 3], Tuple[int, ...])
Out: (1, 2, 3)
```

Uses Ellipsis (`...`) to indicate that the tuple contains an indefinite amount of items of the same size.

typing.Dict
-----------

```python
In : typedload.load({1: '1'}, Dict[int, Path])
Out: {1: PosixPath('1')}

In : typedload.load({1: '1'}, Dict[int, str])
Out: {1: '1'}

In : typedload.load({'1': '1'}, Dict[int, str])
Out: {1: '1'}

In : typedload.load({'1': '1'}, Dict[int, str], basiccast=False)
Exception: TypedloadValueError

class A(NamedTuple):
    y: str='a'

In : typedload.load({1: {}}, Dict[int, A], basiccast=False)
Out: {1: A(y='2')}

```

Loads a dictionary, making sure that the types are correct.

Objects
-------

* typing.NamedTuple
* dataclasses.dataclass
* attr.s

```python
class Point2d(NamedTuple):
    x: float
    y: float

class Point3d(NamedTuple):
    x: float
    y: float
    z: float

@attr.s
class Polygon:
    vertex: List[Point2d] = attr.ib(factory=list, metadata={'name': 'Vertex'})

@dataclass
class Solid:
    vertex: List[Point3d] = field(default_factory=list)
    total: int = field(init=False)

    def __post_init__(self):
        self.total = 123 # calculation here

In : typedload.load({'Vertex':[{'x': 1,'y': 1}, {'x': 2,'y': 2},{'x': 3,'y': 3}]}, Polygon)
Out: Polygon(vertex=[Point2d(x=1.0, y=1.0), Point2d(x=2.0, y=2.0), Point2d(x=3.0, y=3.0)])

In : typedload.load({'vertex':[{'x': 1,'y': 1,'z': 1}, {'x': 2,'y': 2, 'z': 2},{'x': 3,'y': 3,'z': 3}]}, Solid)
Out: Solid(vertex=[Point3d(x=1.0, y=1.0, z=1.0), Point3d(x=2.0, y=2.0, z=2.0), Point3d(x=3.0, y=3.0, z=3.0)], total=123)
```

They are loaded from dictionaries into those objects. `failonextra` when set can generate exceptions if more fields than expected are present.

When dumping they go back to dictionaries. `hide_default` defaults to True, so all fields that were equal to the default will not be dumped.

### attrs converters

Attrs fields can have a converter function associated.

If this is the case, typedload will ignore the assigned type, inspect the type hints of the converter function, and assign the type of the parameter of the converter as type. If the function is not typed, `Any` will be used.

This can be useful when the data format has been changed in a more complex way than just adding a few extra fields. Then the converter function can be used to do the necessary conversions for the old data format.

#### Examples

```python
@attr.s
class A:
    x: int = attr.ib(converter=str) # x has a converter that just calls str()

In : load({'x': [1]}, A)
Out: A(x='[1]')

# In this case the int type for x was completely ignored, because a converter is defined
# The str() function does not define type hints, so Any is used
# So the list [1] is passed as is to the constructor of A() which calls str() on it to convert it
```


```python
@attr.s
class Old:
    oldfield: int = attr.ib()

@attr.s
class New:
    newfield: int = attr.ib()

def conv(p: Old | New) -> New:
    # The type hinting necessary to tell typedload what to do
    # Without hinting it would just pass the dictionary directly
    if isinstance(p, New):
        return p
    return New(p.oldfield)

@attr.s
class Outer:
    '''
    Our old data format was using the Old class, but
    we now use the New class.

    The converter returns a New instance from an Old instance.
    '''
    inner: New = attr.ib(converter=conv)

# Calling load with the new data format, returns a New class
In : load({'inner': {'newfield':3}}, Outer)
Out: Outer(inner=New(newfield=3))
# Loading with the old data format, still returns a New class
In : load({'inner': {'oldfield':3}}, Outer)
Out: Outer(inner=New(newfield=3))
```

Forward references
------------------

A forward reference is when a type is specified as a string instead of as an object:

```python
a: ObjA = ObjA()
a: 'ObjA' = ObjA()
```

The 2nd generates a forward reference, that is, a fake type that is really hard to resolve.

The current strategy for typedload is to cache all the names of the types it encounters and use this cache to resolve the names.

In alternative, it is possible to use the `frefs` dictionary to manually force resolution for a particular type.

Python `typing` module offers some ways to resolve those types which are not used at the moment because they are slow and have strong limitations.

Python developers want to turn every type annotation into a forward reference, for speed reasons. This was supposed to come in 3.10 but has been postponed. So for the moment there is little point into working on this very volatile API.


typing.Union
------------

A union means that a value can be of more than one type.

If the passed value is of a `basictype` that is also present in the Union, the value will be returned.

Otherwise, basictype values are evaluated last. This is to avoid that a Union containing a `str` will catch more than it should.

After this sorting of types, a Union is loaded by trying to load the value with each of the types. The first load that succeeds is returned. In general you cannot make assumptions on the order in which types are evaluated, because it is decided by the runtime.

### Optional

A typical case is when using Optional values

```python
In : typedload.load(3, Optional[int])
Out: 3

In : typedload.load(None, Optional[int])
Out: None
```

### Ambiguity

Ambiguity can sometimes be fixed by enabling `failonextra` or disabling `basiccast`.

```python
Point2d = Tuple[float, float]
Point3d = Tuple[float, float, float]

# This is not what we wanted, the 3rd coordinate is lost
In : typedload.load((1,1,1), Union[Point2d, Point3d])
Out: (1.0, 1.0)

# Make the loading more strict!
In : typedload.load((1,1,1), Union[Point2d, Point3d], failonextra=True)
Out: (1.0, 1.0, 1.0)
```

But in some cases it cannot be simply solved, when the types in the Union are too similar. In this case the only solution is to rework the codebase.

```python
# A casting must be done, str was chosen, but could have been int
In : typedload.load(1.1, Union[str, int])
Out: '1.1'


class A(NamedTuple):
    x: int=1

class B(NamedTuple):
    y: str='a'

# Both A and B accept an empty constructor
In : typedload.load({}, Union[A, B])
Out: A(x=1)
```

#### Finding ambiguity

Typedload can't solve certain ambiguities, but setting `uniondebugconflict=True` will help detect them.

```python
In : typedload.load({}, Union[A, B], uniondebugconflict=True)
TypedloadTypeError: Value of dict could be loaded into typing.Union[__main__.A, __main__.B] multiple times
```

So this setting can be used to find ambiguities and manually correct them.

*NOTE*: The setting slows down the loading of unions, so it is recommended to use it only during tests or when designing the data structures, but not in production.


typing.TypedDict
----------------

```python
class A(TypedDict):
    val: str

In : typedload.load({'val': 3}, A)
Out: {'val': '3'}

In : typedload.load({'val': 3,'aaa':2}, A)
Out: {'val': '3'}

In : typedload.load({'val': 3,'aaa':2}, A, failonextra=True)
Exception: TypedloadValueError
```

From dict to dict, but it makes sure that the types are as expected.

It also supports non-total TypedDict (since 2.7).

```python
class A(TypedDict, total=False):
    val: str

In : typedload.load({}, A)
Out: {}
```

**NotRequired** can also be used (since 2.17).

```python
class A(TypedDict):
    val: str
    vol: NotRequired[int]

In : typedload.load({'val': 'a'}, A)
Out: {'val': 'a'}
```

typing.Set, typing.Frozenset
----------------------------

```python
In : typedload.load([1, 4, 99], set[float])
Out: {1.0, 4.0, 99.0}

In : typedload.load(range(12), Set[int])
Out: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}

In : typedload.load(range(12), frozenset[float])
Out: frozenset({0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0})
```

Loads an iterable inside a `set` or a `frozenset`.

Always dumped as a list.

typing.Any
----------

```python
typedload.load(obj, typing.Any)
```

This will just return `obj` without doing any check or transformation.

To work with `dump()`, `obj` needs to be of a supported type, or an handler is needed.

typing.NewType
--------------

```python
T = typing.NewType('T', str)
typedload.load('ciao', T)
```

Allows the use of NewType to define already handled types.

String constructed
------------------

Loaders and dumpers have a set of `strconstructed`.

Those are types that accept a single `str` parameter in their constructor and have a `__str__` method that returns that parameter.

For those types, a specific handler is not needed and they can just be added to the `strconstructed` set.

The preset ones are:

### pathlib.Path

```python
In : typedload.load('/tmp/', Path)
Out: PosixPath('/tmp')

In : typedload.load('/tmp/file.txt', Path)
Out: PosixPath('/tmp/file.txt')
```

Loads a string as a `Path`; when dumping it goes back to being a string.

### ipaddress.IPv*Address/Network/Interface

* `ipaddress.IPv4Address`
* `ipaddress.IPv6Address`
* `ipaddress.IPv4Network`
* `ipaddress.IPv6Network`
* `ipaddress.IPv4Interface`
* `ipaddress.IPv6Interface`

```python
In : typedload.load('10.1.1.3', IPv4Address)
Out: IPv4Address('10.1.1.3')
```

Loads a string as an one of those classes, and dumps back to string.

argparse.Namespace
------------------

This is converted to a dictionary and can be loaded into NamedTuple/dataclass.

Dates
-----

### `datetime.timedelta`
Represented as a float of seconds.


### `datetime.date` `datetime.time` `datetime.datetime`

When loading, it is possible to pass a string in ISO 8601, or a list of ints that will be passed to the constructor.

When dumping, the default is to dump a list of ints, unless `isodates=True` is set in the dumper object, in which case an ISO 8601 string will be returned instead.

The format with the list of ints is deprecated and kept for backward compatibility. Everybody should use the ISO 8601 strings.

The format with the list of ints does not support timezones.
