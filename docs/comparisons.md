Comparisons
===========

In this section we compare typedload to other similar libraries.

In general, the advantages of typedload over competing libraries are:

* Works with existing codebase and uses standard types. No inheritance or decorators
* Easy to extend, even with objects from 3rd party libraries
* Supports Union
* Works on python 3.5
* Mypy and similar work without plugins
* Can use and convert camelCase and snake_case
* Functional approach
* Pure Python, no compiling

### It works with existing codebase

Most libraries require your classes to extend or use decorators from the library itself.

This means that types from other libraries or non supported stdlib classes can never be used.

It also means that mypy will just work out of the box, rather than requiring plugins.

Instead, typedload works fine with the type annotations from the `typing` module and will work without requiring any changes to the datatypes.

It also works on python 3.5, so projects running on LTS distributions can use it.

### It is easy to extend

Since there can be situations that are highly domain specific, typedload allows to extend its functionality to support more types or replace the existing code to handle special cases.

### Support of Union

Seems to be very rare in this domain, but unions are very common in real world datasets.

# Functional approach

You can load a `List[YourType]`, while pydantic can only load a single object that then will contain the list.


apischema
---------

Found [here](https://github.com/wyfo/apischema)

* It reuses the same objects in the output, so changing the data might result in subtle bugs if the input data is used again
* Doesn't support as many python versions as typedload (currently no 3.11 and no 3.5)
* No native support for attrs


pydantic
--------

Found [here](https://pydantic-docs.helpmanual.io/)

* [They change API all the time, between minor releases.](https://pypi.org/project/pydantic/1.9.1/)
* Slower than typedload
* Requires all the classes to derive from a superclass
* Does not work with mypy:
    * [Abuses python typing annotation to mean something different, breaking linters](https://pydantic-docs.helpmanual.io/usage/models/#required-optional-fields)
    * [Uses float=None without using Optional in its own documentation](https://pydantic-docs.helpmanual.io/usage/models/#recursive-models).
* Union might do casting when casting is not needed.


dataclasses-json
----------------

Found [here](https://github.com/lidatong/dataclasses-json)

* 20x slower than typedload
* Does not check types
* Requires to decorate all the classes
* It is not extensible
* Doesn't support Union (and other types)
* Has dependencies (marshmallow, marshmallow-enum, typing-inspect)
* Very complicated way for doing lists
