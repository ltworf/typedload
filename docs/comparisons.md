Comparisons
===========

In this section we compare typedload to other similar libraries.

In general, the advantages of typedload over competing libraries are:

### It works with existing codebase

Most libraries require your classes to extend or use decorators from the library itself.
Instead, typedload works fine with the type annotations from the `typing` module and will work without requiring changes to the datatypes.

### It is easy to extend

Since there can be situations that are highly domain specific, typedload allows to extend its functionality to support more types or replace the existing code to handle special cases.


pydantic
--------

Found [here](https://pydantic-docs.helpmanual.io/)

* Slower than typedload for complex data (but faster for simple non-nested data)
* Requires all the classes to derive from a superclass
* Does not work with mypy:
    * [Abuses python typing annotation to mean something different, breaking linters](https://pydantic-docs.helpmanual.io/usage/models/#required-optional-fields)
    * [Uses float=None without using Optional in its own documentation](https://pydantic-docs.helpmanual.io/usage/models/#recursive-models).
* Does not handle Union, Set, Path

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
