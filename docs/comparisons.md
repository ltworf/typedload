Comparisons
===========

In this section we compare typedload to other similar libraries.

In general, the advantages of typedload over competing libraries are:

* Works with existing codebase
* Easy to extend
* Supports Union
* Works on python 3.5

### It works with existing codebase

Most libraries require your classes to extend or use decorators from the library itself.

Instead, typedload works fine with the type annotations from the `typing` module and will work without requiring any changes to the datatypes.

It also works on python 3.5, so projects running on LTS distributions can use it.

### It is easy to extend

Since there can be situations that are highly domain specific, typedload allows to extend its functionality to support more types or replace the existing code to handle special cases.

### Support of Union

Seems to be very rare in this domain, but unions are very common in real world datasets.


pydantic
--------

Found [here](https://pydantic-docs.helpmanual.io/)

* Slower than typedload for complex data (but faster for simple non-nested data)
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
