Comparisons
===========

In this section we compare typedload to other similar libraries.

In general, the advantages of typedload over competing libraries are:

* Works with existing codebase and uses standard types. No inheritance or decorators
* Easy to use
* Easy to extend, even with objects from 3rd party libraries
* Stable API, breaking changes only happen on major releases (it has happened once since 2018 and most users didn't notice)
* Supports Union properly
* Works on python 3.5 (until typedload <= 2.20)
* Mypy and similar work without plugins
* Can use and convert camelCase and snake_case
* Functional approach
* Pure Python, no compiling
* Very small, it's fast for automated tests to extract and install compared to huge binary libraries

### It works with existing codebase

Most libraries require your classes to extend or use decorators from the library itself.

This means that types from other libraries or non supported stdlib classes can never be used.

It also means that mypy will just work out of the box, rather than requiring plugins.

Instead, typedload works fine with the type annotations from the `typing` module and will work without requiring any changes to the datatypes.

It also works on python 3.5 (until version 2.20), so projects running on LTS distributions can use it.

### It is easy to extend

Since there can be situations that are highly domain specific, typedload allows to extend its functionality to support more types or replace the existing code to handle special cases.

### Support of Union

Other libraries tend to either be very slow or just give completely [wrong results](https://pydantic-docs.helpmanual.io/) when Union are involved.

# Functional approach

You can load a `List[YourType]`, while pydantic can only load a single object that then will contain the list.


apischema
---------

Found [here](https://github.com/wyfo/apischema)

It's the only viable alternative to typedload that I've encountered.

* Settings are global, a submodule changing a setting will affect the entire application
* Type checks are disabled by default
* It reuses the same objects in the output, so changing the data might result in subtle bugs if the input data is used again
* No native support for attrs (but can be manually added by the user)
* Faster than typedload for flat data structures, slower otherwise


pydantic
--------

Found [here](https://pydantic-docs.helpmanual.io/)

* [The author calls you a liar if your pure python library is faster](https://news.ycombinator.com/item?id=36639943)
* [Breaks API all the time, between minor releases.](https://docs.pydantic.dev/latest/changelog/) (43 times in 2 major versions so far)
* [They hate](https://github.com/pydantic/pydantic/pull/3264) [benchmarks](https://github.com/pydantic/pydantic/pull/3881) [that show](https://github.com/pydantic/pydantic/pull/1810) [it's slow](https://github.com/pydantic/pydantic/pull/1525). [So they removed them altogether](https://github.com/pydantic/pydantic/pull/3973)
* It needs a mypy plugin, and for some kinds of classes it does no static checks whatsoever.
* Is now related to a company that will need some way to monetize, eventually


#### Version 1
* One of the slowest libraries that exist in this space
* `int | float` might decide to cast a `float` to `int`, or an `int` to `float`

#### Version 2
* Somehow manages to be slower than pure python in certain benchmarks, despite months of work to rewrite it in rust
* Took them several years to make a version 2 where types on BaseModel finally mean the same thing that they mean in the rest of python
* Took them several years to implement unions to catch up with typedload

jsons
-----

Found [here](https://github.com/ramonhagenaars/jsons)

* Type safety is not a goal of this project
* It is buggy:
    * This returns an int `jsons.load(1.1, Union[int, float])`
    * This returns a string `jsons.load(1, Union[str, int])`
    * This raises an exception `jsons.load(1.0, int | float)`
* It is incredibly slow (40x slower in certain cases)
  For this reason it has been removed from the benchmarks.
* [Does not support `Literal`](https://github.com/ramonhagenaars/jsons/issues/170)
* Can't load iterables as lists
* Exceptions do not have information to find the incorrect data

#### Quick test

```python
# Needed because jsons can't load directly from range()
data = [i for i in range(3000000)]

# This took 2.5s with jsons and 200ms with typedload
load(data, list[int])

# This took 20s with jsons and 500ms with typedload
# And it converted all the ints to float!
load(data, list[Union[float,int]])
```

dataclasses-json
----------------

Found [here](https://github.com/lidatong/dataclasses-json)

*It is completely useless for type safety and very slow. I can't understand why it has users.*

* It is incredibly slow (20x slower in certain cases)
  For this reason it has been removed from the benchmarks.
* It doesn't enforce type safety (it will be happy to load whatever inside an int field)
* Requires to decorate all the classes
* It is not extensible
* Has dependencies (marshmallow, marshmallow-enum, typing-inspect)
* Very complicated way for doing lists

#### Quick test

```python
# Just to show how unreliable this is
@dataclass_json
@dataclass
class Data:
    data: list[int]

Data.from_dict({'data': ["4", None, ..., ('qwe',), 1.1]})
# This returns:
# Data(data=['4', None, Ellipsis, ('qwe',), 1.1])
# despite data is supposed to be a list of int
```

msgspec
-------

Found [here](https://jcristharif.com/msgspec/)

* Implemented in C, won't run on PyPy
* Supports tagged Unions partially only when inheriting from its Struct type
  Mypy will not typecheck those classes.
  To use unions you must give up static typechecking.
* Doesn't support unions between regular dataclass/NamedTuple/Attrs/TypedDict
* Doesn't support untagged Unions
* Doesn't support multiple tags (e.g. `tag=Literal[1, 2]`)
* Extended using a single function that must handle all cases
* Can't replace type handlers
