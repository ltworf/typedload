2.17
====
* Support for NotRequired
* Document performance testing

2.16
====
* Add is_optional function
* Support new style union (A | B)
* Experimental support for PEP563 `__future__.annotations`.
  **READ ABOUT DEFERRED EVALUATION IN THE DOCUMENTATION.**

2.15
====
* Union fails immediately when a non typedload exception is found
* New `make html` target to generate the website
* Updated CONTRIBUTING file, with details about new licenses from the FSF
* Handle typing.NewType

2.14
====
* Fix bug where AttributeError from name mangling caused an AssertionError

2.13
====
* Separate and simpler handlers for NamedTuple, dataclass, attrs, TypedDict
* Allow duck typing when loading attr (allow any dict-like class to be used)
* Minor performance improvements

2.12
====
* Add `uniondebugconflict` flag to detect unions with conflicts.

2.11
====
* Make newer mypy happy

2.10
====
* Fix setup.py referring to a non-existing file when installing with pip

2.9
===
* Use README on pypi.org
* Tiny speed improvement
* Expanded and improved documentation

2.8
===
* Better report errors for `Enum`
* Improve support for inheritance with mixed totality of `TypedDict` (requires Python 3.9)

2.7
===
* failonextra triggers failure when dropping fields in mangling
* Support for `total=False` in `TypedDict`
* Support `init=False` in `dataclass` field

2.6
===
* Handle `Any` types as passthrough
* Easy way to handle types loaded from and dumped to `str`
* Improve how exceptions are displayed

2.5
===
* Fix dump for attr classes with factory
* Let name mangling use arbitrary metadata fields rather than just `name`

2.4
===
* Support for `ipaddress.IPv4Address`, `ipaddress.IPv6Address`,
  `ipaddress.IPv4Network`, `ipaddress.IPv6Network`,
  `ipaddress.IPv4Interface`, `ipaddress.IPv6Interface`.

2.3
===
* Better type sorting in `Union`
  This helps when using `Union[dataclass, str]`

2.2
===
* Add Python3.9 to the supported versions
* Prevent loading dict as `List`, `Tuple`, `Set`
  This helps when using `Union[Dict, List]` to take the correct
  type.

2.1
===
* Written new usage example
* typechecks internals now pass with more mypy configurations
* Fix `import *`

2.0
===
* Breaking API change: handlers can only be modified before the first load
* Breaking API change: plugins removed (attr support is by default)
* Exceptions contain more information
* Greatly improve performances with iterables types
* Support for `pathlib.Path`

1.20
====
* Drop support for Python 3.5.2 (3.5 series is still supported)
* Support `TypedDict`
* More precise type annotation of `TypedloadException` and `Annotation` fields
* Deprecate the plugin to handle `attr.s` and make it always supported.
  This means that there will be no need for special code.
* Fix datetime loader raising exceptions with the wrong type

1.19
====
* Add support for `Literal`.

1.18
====
* Improved documentation
* Debian builds are now done source only

1.17
====
* Prefer the same type in union loading

1.16
====
* New `uniontypes()` function.
* Make list and dictionary loaders raise the correct exceptions
* Able to load from `argparse.Namespace`

1.15
====
* Add support for `FrozenSet[T]`.
* Define `__all__` for typechecks.
* Add name mangling support in dataclass, to match attrs.
* Add support for `datetime.date`, `datetime.time`, `datetime.datetime`

1.14
====
* Add support for `Tuple[t, ...]`

1.13
====
* Fix bug in loading attr classes and passing random crap.
  Now the proper exception is raised.
* New module to expose the internal type checks functions

1.12
====
* Support fields with factory for dataclass

1.11
====
* Fixed problem when printing sub-exceptions of failed unions
* Improve documentation

1.10
====
* Make mypy happy again

1.9
===
* Support `ForwardRef`
* Add a new Exception type with more details on the error (no breaking API changes)

1.8
===
* Make mypy happy again

1.7
===
* Make mypy happy again

1.6
===
* Run tests on older python as well
* Support for dataclass (Since python 3.7)
* Added methods to find the appropriate handlers

1.5
===
* Improve handling of unions
* Better continuous integration
* Support python 3.7

1.4
===
* Add support for name mangling in attr plugin
* Parameters can be passed as kwargs
* Improved exception message for `NamedTuple` loading

1.3
===
* Add support for Python < 3.5.3

1.2
===
* Ship the plugins in pypy

1.1
===
* Able to load and dump old style `NamedTuple`
* Support for Python 3.5
* Target to run mypy in makefile
* Refactor to support plugins. The API is still compatible.
* Plugin for the attr module, seems useful in Python 3.5

1.0
===
* Has a setting to hide default fields or not, in dumps
* Better error reporting
* Add file for PEP 561

0.9
===
* Initial release
