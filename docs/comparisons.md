Comparisons
===========

In this section we compare typedload to other similar libraries.

In general, the advantages of typedload over competing libraries are:

* Works with existing codebase and uses standard types. No inheritance or decorators
* Easy to use
* Easy to extend, even with objects from 3rd party libraries
* Stable API, breaking changes only happen on major releases (it has happened once since 2018)
* Supports Union properly
* Works on python 3.5 (typedload <= 2.20)
* Mypy and similar work without plugins
* Can use and convert camelCase and snake_case
* Functional approach
* Pure Python, no compiling

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

* [They change API all the time, between minor releases.](https://pypi.org/project/pydantic/1.9.1/)
* [Unions behave non-deterministically by default and require a flag to behave normally](https://docs.pydantic.dev/usage/model_config/#smart-union)
* Slow, despite being compiled
* Requires all the classes to derive from a superclass, existing code needs to be modified, external libraries are harder to use directly
* Does not work with mypy:
    * [Abuses python typing annotation to mean something different, breaking linters](https://pydantic-docs.helpmanual.io/usage/models/#required-optional-fields)
    * [Uses float=None without using Optional in its own documentation](https://pydantic-docs.helpmanual.io/usage/models/#recursive-models).
* [Author refuses to include unfavorable comparisons](https://github.com/pydantic/pydantic/pull/1525)

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


* Decodes json directly, which is faster, but it means it can't be used with bson, yaml, and whatever else
* Very rudimental support for unions, so it can't run the performance tests

```python
TypeError: Type unions may not contain more than one dataclass type - type `A | B` is not supported
```
