"""
typedload
Module to load data into typed data structures
"""

# Copyright (C) 2018-2023 Salvo "LtWorf" Tomaselli
#
# typedload is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>


import datetime
from enum import Enum
import ipaddress
from itertools import compress, count, repeat
from functools import reduce
from pathlib import Path
import re
from typing import *

from .exceptions import *
from .typechecks import *
from .typechecks import discriminatorliterals
from .helpers import tname


__all__ = [
    'Loader',
]


T = TypeVar('T')


class Loader:
    """
    A loader object that recursively loads data into
    the desired type.

    basictypes: a set of types that are considered as
        building blocks for everything else and do not
        need to be converted further.
        If you are not loading from json, you probably
        want to add bytes to the set.

    failonextra: Disabled by default.
        When enabled, the loader will raise exceptions if
        there are fields in the data that are not being used
        by the type.

    basiccast: Enabled by default.
        When disabled, instead of trying to perform casts,
        exceptions will be raised.
        Since many json seem to encode numbers as strings,
        to avoid extra complications this functionality is
        provided.
        If you know that your original data is encoded
        properly, it is better to disable this.

    dictequivalence: Enabled by default.
        Automatically convert dict-like classes to dictionary
        when loading. This enables them to be loaded into other
        classes.
        At the moment it supports:
            argparse.Namespace

    raiseconditionerrors: Enabled by default.
        Raises exceptions when evaluating a condition from an
        handler. When disabled, the exceptions are not raised
        and the condition is considered False.

    uniondebugconflict: Disabled by default
        When enabled, all the possible types for the unions
        are evaluated instead of stopping at the first that works.
        If more than one type in the union works, an error is raised
        because the types are conflicting and the union might return
        different types with the same input value.
        This option makes the loading slower and is only to be used when
        debugging issues.

    mangle_key: Defaults to 'name'
        Specifies which key is used into the metadata dictionaries
        to perform name-mangling.

    handlers: This is the list that the loader uses to
        perform its task.
        The type is:
        List[
            Tuple[
                Callable[[Type[T]], bool],
                Callable[['Loader', Any, Type[T]], T]
            ]
        ]

        The elements are: Tuple[Condition,Loader]
        Condition(type) -> Bool
        Loader(loader, value, type) -> type

        In most cases, it is sufficient to append new elements
        at the end, to handle more types.

        There is an internal cache to speed up lookup, so after the
        first call to load, this should no longer be modified.

    strconstructed: Set of types to construct from a string.

    frefs: Dictionary to resolve ForwardRef.
        Something like
        class Node(NamedTuple):
            next: Optional['Node']

        requires a ForwardRef (also in python3.7), which means that the type
        is stored as string and must be resolved at runtime.

        This dictionary contains the names of the types as keys, and the
        actual types as values.

        A loader object by default starts with an empty dictionary and
        fills it with the types it encounters, but it is possible to
        manually add more types to the dictionary.

        Setting this to None disables any support for ForwardRef.

        Reusing the same loader object on unrelated types might cause
        failures, if the types are different but use the same names.

    pep563: Set to true to use __future__.annotations
        WARNING: DEPRECATED Support for this might be removed in any future
        release without notice.

        Check deferred evaluation in the documentation for more details.

        This will make typedload much slower.

        This PEP is broken and superseeded by PEP649.

        Do not report bugs about this "feature". It's not here to stay.

    These parameters can be set as named arguments in the constructor
    or they can be set later on.

    The constructor will accept any named argument, but only the documented
    ones have any effect. This is to allow custom handlers to have their
    own parameters as well.

    Because internal caches are used, after the first call to load() these properties
    should no longer be modified.

    Using unions is complicated. The best is to use tagged unions using a Literal field.
    If the types in the union are too similar to each other, it is easy to obtain an unexpected type.
    """

    def __init__(self, **kwargs) -> None:
        # Types that do not need conversion
        self.basictypes = {int, bool, float, str, NONETYPE}

        # If true, it attempts to do casting of basic types
        # otherwise an exception is raised
        self.basiccast = True

        # Raise errors if the value has more data than the
        # type expects.
        # By default the extra data is ignored.
        self.failonextra = False

        # Raise errors if the condition fails
        self.raiseconditionerrors = True

        # Forward refs dictionary
        self.frefs = {}  # type: Optional[Dict[str, Type]]

        # Enable conversion of dict-like things to dicts, before loading
        self.dictequivalence = True

        # Which key is used in metadata to perform name mangling
        self.mangle_key = 'name'

        # Fail if multiple types work within the union
        self.uniondebugconflict = False

        # Objects loaded from a string
        self.strconstructed = {
            Path,
            ipaddress.IPv4Address,
            ipaddress.IPv6Address,
            ipaddress.IPv4Network,
            ipaddress.IPv6Network,
            ipaddress.IPv4Interface,
            ipaddress.IPv6Interface
        }

        # Bah
        self.pep563 = False

        # The list of handlers to use to load the data.
        # It gets iterated in order, and the first condition
        # that matches is used to load the value.
        self.handlers = [
            (is_nonetype, _noneload),
            (is_union, _unionload),
            (lambda type_: type_ in self.basictypes, _basicload),
            (is_enum, _enumload),
            (is_tuple, _tupleload),
            (is_list, lambda l, value, type_: _iterload(l, value, type_, list)),
            (is_dict, _dictload),
            (is_set, lambda l, value, type_: _iterload(l, value, type_, set)),
            (is_frozenset, lambda l, value, type_: _iterload(l, value, type_, frozenset)),
            (is_namedtuple, _namedtupleload),
            (is_dataclass, _dataclassload),
            (is_forwardref, _forwardrefload),
            (is_literal, _literalload),
            (is_typeddict, _typeddictload),
            (lambda type_: type_ in {datetime.date, datetime.time, datetime.datetime}, _datetimeload),
            (is_pattern, _patternload),
            (lambda type_: type_ == datetime.timedelta, _timedeltaload),
            (lambda type_: type_ in self.strconstructed, _strconstructload),
            (is_attrs, _attrload),
            (is_any, _anyload),
            (is_newtype, _newtypeload),
        ]  # type: List[Tuple[Callable[[Any], bool], Callable[[Loader, Any, Any], Any]]]

        for k, v in kwargs.items():
            setattr(self, k, v)

        self._indexcache = {}  # type: Dict[Any, Callable[[Loader, Any, Any], Any]]

        self._objfieldscache = {}  # type: Dict[Type, Tuple[Set[str], Set[str], Dict[str, Type], Dict[str, str]]]

        self._unionload_discriminatorcache = {}  # type: Dict[Type, Tuple[Optional[str], Optional[Dict[Any, Type]]]]

    def index(self, type_: Type[T]) -> int:
        """
        Returns the index in the handlers list
        that matches the given type.

        If no condition matches, ValueError is raised.
        """
        for i, cond in ((q[0], q[1][0]) for q in enumerate(self.handlers)):
            try:
                match = cond(type_)
            except Exception:
                if self.raiseconditionerrors:
                    raise
                match = False
            if match:
                return i
        raise ValueError('No matching condition found')

    def load(self, value: Any, type_: Type[T], *, annotation: Optional[Annotation] = None) -> T:
        """
        Loads value into the typed data structure.

        TypeError is raised if there is no known way to treat type_,
        otherwise all errors raise a ValueError.

        annotation is used by recursive calls to track which path was
        being executed in case of exceptions.

        It is only needed when calling load recursively from
        a custom handler.
        """
        cached_f = self._indexcache.get(type_)

        if cached_f is not None:
            func = cached_f
        else:
            try:
                index = self.index(type_)
            except ValueError:
                raise TypedloadTypeError(
                    'Cannot deal with value of type %s' % tname(type_),
                    value=value,
                    type_=type_
                )

            func = self._indexcache[type_] = self.handlers[index][1]

            # Add type to known types, to resolve ForwardRef later on
            if self.frefs is not None and hasattr(type_, '__name__'):
                typename = type_.__name__
                if typename not in self.frefs:
                    self.frefs[typename] = type_

        try:
            return func(self, value, type_)
        except Exception as e:
            assert isinstance(e, TypedloadException)
            e.trace.insert(0, TraceItem(value, type_, annotation))
            raise e


def _forwardrefload(l: Loader, value: Any, type_) -> Any:
    """
    This resolves a ForwardRef.

    It just looks up the type in the dictionary of known types
    and loads the value using that.
    """
    if l.frefs is None:
        raise TypedloadException('ForwardRef resolving is disabled for the loader', value=value, type_=type_)
    tname = type_.__forward_arg__  # type: ignore
    t = l.frefs.get(tname)
    if t is None:
        raise TypedloadValueError(
            "ForwardRef '%s' unknown" % tname,
            value=value,
            type_=type_
        )
    return l.load(value, t, annotation=Annotation(AnnotationType.FORWARDREF, tname))


def _anyload(l: Loader, value: Any, type_) -> Any:
    return value


def _literalload(l: Loader, value: Any, type_) -> Any:
    """
    Checks if the value is within the allowed literals and
    returns it.
    """
    if value in type_.__args__:
        return value
    raise TypedloadValueError('Not one of the allowed values in %s' % tname(type_), value=value, type_=type_)


def _basicload(l: Loader, value: Any, type_) -> Any:
    """
    This converts a value into a basic type.

    In theory it does nothing, but it performs type checking
    and raises if conditions fail.

    It also attempts casting, if enabled.
    """

    if type(value) != type_:
        if l.basiccast:
            try:
                return type_(value)
            except ValueError as e:
                raise TypedloadValueError(str(e), value=value, type_=type_)
            except TypeError as e:
                raise TypedloadTypeError(str(e), value=value, type_=type_)
            except Exception as e:
                raise TypedloadException(str(e), value=value, type_=type_)
        else:
            raise TypedloadValueError('Got %s of type %s, expected %s' % (repr(value), tname(type(value)), tname(type_)), value=value, type_=type_)
    return value


def _dictload(l: Loader, value: Any, type_) -> Dict:
    """
    This loads into something like Dict[str,str]

    Recursively loads both keys and values.
    """
    key_type, value_type = type_.__args__


    key_type_basic = key_type in l.basictypes
    value_type_basic = value_type in l.basictypes

    key_handler = l._indexcache.get(key_type)
    if key_handler is not None:
        key_f = key_handler
    else:
        try:
            key_f = l._indexcache[key_type] = l.handlers[l.index(key_type)][1]
        except ValueError:
            raise TypedloadValueError(
                'Cannot deal with value of type %s (key of %s)' % (tname(key_type), tname(type_)),
                value=value,
                type_=key_type
            )

    # Same thing for the value
    value_handler = l._indexcache.get(value_type)
    if value_handler is not None:
        value_f = value_handler
    else:
        try:
            key_f = l._indexcache[value_type] = l.handlers[l.index(value_type)][1]
        except ValueError:
            raise TypedloadValueError(
                'Cannot deal with value of type %s (value of %s)' % (tname(value_type), tname(type_)),
                value=value,
                type_=value_type
            )

    value = _dictequivalence(l, value)

    # Try fast load
    try:
        return {
            k if key_type_basic and isinstance(k, key_type) else key_f(l, k, key_type): \
            v if value_type_basic and isinstance(v, value_type) else value_f(l, v, value_type) \
            for k, v in value.items()
        }
    except Exception:
        # Failed, do the slow method with exception tracking
        pass

    try:
        return {
            l.load(k, key_type, annotation=Annotation(AnnotationType.KEY, k)): l.load(v, value_type, annotation=Annotation(AnnotationType.VALUE, v))
            for k, v in value.items()}
    except AttributeError as e:
        raise TypedloadAttributeError(str(e), type_=type_, value=value)


def _tupleload(l: Loader, value: Any, type_) -> Tuple:
    """
    This loads into something like Tuple[int,str]
    """
    args = type_.__args__

    if len(args) == 2 and args[1] == ...: # Tuple[something, ...]
        return _iterload(l, value, type_, tuple)

    # Tuple[something, something, somethingelse]
    if isinstance(value, dict):
        raise TypedloadTypeError('Unable to load dictionary as a tuple', value=value, type_=type_)
    if l.failonextra and len(value) > len(args):
        raise TypedloadValueError('Value is too long for type %s' % tname(type_), value=value, type_=type_)
    elif len(value) < len(args):
        raise TypedloadValueError('Value is too short for type %s' % tname(type_), value=value, type_=type_)

    ctr = count(1)  # Keep track of the position in the tuple

    try:
        return tuple(v if t in l.basictypes and type(v) == t else h(l, v, t)
            for v, h, t in zip(
                compress(value, ctr),
                (l._indexcache.get(t) or l.handlers[l.index(t)][1] for t in args),
                args
            )
        )
    except TypedloadException as e:
        index = next(ctr) - 2
        annotation = Annotation(AnnotationType.INDEX, index)
        e.trace.insert(0, TraceItem(value, type_, annotation))
        raise e
    except TypeError as e:
        raise TypedloadTypeError(str(e), value=value, type_=type_)
    except Exception as e:
        raise TypedloadTypeError('Exception is not a subclass of TypedloadException. Make sure all handlers only raise TypedloadException')


def _mangle_names(namesmap: Dict[str, str], value: Dict[str, Any], failonextra: bool) -> Dict[str, Any]:
    """
    Mangling names of a dictionary.

    The dictionary is copied internally.

    Namesmap is the mapping to be applied, in the format [dataname] = pyname
    """
    if not namesmap:
        return value
    r = {}

    # Disallow the python names if they are in the map
    skip = set(namesmap.values())

    for k, v in value.items():
        if k in skip and k not in namesmap:
            if failonextra:
                raise ValueError('Extra field: %s' % k)
            else:
                continue
        if k in namesmap:
            k = namesmap[k]
        r[k] = v
    return r


def _dataclassload(l: Loader, value: Dict[str, Any], type_) -> Any:
    """
    This loads a Dict[str, Any] into a NamedTuple.
    """
    cached = l._objfieldscache.get(type_)
    if cached:
        fields, necessary_fields, type_hints, transforms = cached
    else:
        fields = set(type_.__dataclass_fields__.keys())
        necessary_fields = {k for k,v in type_.__dataclass_fields__.items() if
                            v.init == True and # Is a field for the constructor
                            v.default == v.default_factory # Has no default or factory
                            }
        if l.pep563:
            type_hints = get_type_hints(type_)
        else:
            type_hints = {k: v.type for k,v in type_.__dataclass_fields__.items()}

        #Name mangling

        # Prepare the list of the needed name changes
        transforms = {}
        for pyname in fields:
            if type_.__dataclass_fields__[pyname].metadata:
                name = type_.__dataclass_fields__[pyname].metadata.get(l.mangle_key)
                if name:
                    transforms[name] = pyname
        l._objfieldscache[type_] = (fields, necessary_fields, type_hints, transforms)

    try:
        value = _mangle_names(transforms, value, l.failonextra)
    except ValueError as e:
        raise TypedloadValueError(str(e), value=value, type_=type_)
    except AttributeError as e:
        raise TypedloadAttributeError(str(e), value=value, type_=type_)

    return _objloader(l, fields, necessary_fields, type_hints, value, type_)


def _dictequivalence(l: Loader, value: Any) -> Any:
    '''
    Helper function to convert classes that are functionally
    the same as a dict into a dict.

    At the moment the only class that can be converted is
    argparse.Namespace.

    in all other cases this simply returns value.
    '''
    # Convert argparse.Namespace to dictionary
    if l.dictequivalence and hasattr(value, '_get_kwargs'):
        return {k: v for k,v in value._get_kwargs()}
    return value


def _objloader(l: Loader, fields: Set[str], necessary_fields: Set[str], type_hints, value: Any, type_) -> Any:
    '''
    Helper function to load dict-like data into an object.
    '''
    try:
        vfields = set(value.keys())
    except AttributeError as e:
        newvalue = _dictequivalence(l, value)

        if newvalue is value:
            raise TypedloadAttributeError(str(e), value=value, type_=type_)
        else:
            value = newvalue
            vfields = set(value.keys())

    if len(necessary_fields.intersection(vfields)) != len(necessary_fields):
        raise TypedloadValueError(
            'Value does not contain fields: %s which are necessary for type %s' % (
                necessary_fields.difference(vfields),
                tname(type_)
            ),
            value=value,
            type_=type_,
        )

    if l.failonextra and len(extra_fields := vfields.difference(fields)):
        extra = ', '.join(extra_fields)
        raise TypedloadValueError(
            'Dictionary has unrecognized fields: %s and cannot be loaded into %s' % (extra, tname(type_)),
            value=value,
            type_=type_,
        )

    params = {}
    for k, v in value.items():
        if k not in fields:
            # Field in value is not in the type
            continue

        # loading field directly, skipping load()
        field_type = type_hints[k]
        cached_loader = l._indexcache.get(field_type)
        if cached_loader:
            loader_f = cached_loader
        else:
            try:
                loader_f = l._indexcache[field_type] = l.handlers[l.index(field_type)][1]
            except ValueError:
                raise TypedloadTypeError(
                    'Cannot deal with value of type %s' % tname(field_type),
                    value=value,
                    type_=field_type
                )
        try:
            params[k] = loader_f(l, v, field_type)
        except TypedloadException as e:
            annotation=Annotation(AnnotationType.FIELD, k)
            e.trace.insert(0, TraceItem(value, type_, annotation))
            raise e
    try:
        return type_(**params)
    except TypeError as e:
        raise TypedloadTypeError(e)
    except ValueError as e:
        raise TypedloadValueError(e)


def _namedtupleload(l: Loader, value: Any, type_) -> Any:
    """
    This loads a Dict[str, Any] into a NamedTuple.
    """
    if l.pep563:
        type_hints = get_type_hints(type_)
    else:
        type_hints = type_.__annotations__
    fields = set(type_hints.keys())
    optional_fields = set(getattr(type_, '_field_defaults', {}).keys())
    necessary_fields = fields.difference(optional_fields)

    return _objloader(l, fields, necessary_fields, type_hints, value, type_)


def _typeddictload(l: Loader, value: Any, type_) -> Any:
    """
    This loads a Dict[str, Any] into a NamedTuple.
    """
    if l.pep563:
        type_hints = get_type_hints(type_)
    else:
        type_hints = type_.__annotations__
    fields = set(type_hints.keys())

    if hasattr(type_, '__required_keys__') and hasattr(type_, '__optional_keys__'):
        # TypedDict, since 3.9
        necessary_fields = set(type_.__required_keys__)
    elif not type_.__total__:
        necessary_fields = set()
    else:
        necessary_fields = fields

    # Resolve the NotRequired stuff
    for k, v in type_hints.items():
        if is_notrequired(v):
            type_hints[k] = notrequiredtype(v)
            necessary_fields.discard(k)

    return _objloader(l, fields, necessary_fields, type_hints, value, type_)


def _unionload(l: Loader, value: Any, type_) -> Any:
    """
    Loads a value into a union.

    Basically this iterates all the types inside the
    union, until one that doesn't raise an exception
    is found.

    If no suitable type is found, an exception is raised.
    """
    args = uniontypes(type_)

    value_type = type(value)

    # Do not convert basic types, if possible
    if value_type in l.basictypes and value_type in args:
        return value

    exceptions = []

    # Give a score to the types
    sorted_args = list(args)  # type: List[Type]
    sorted_args.sort(key=lambda i: i in l.basictypes)

    # For object types, bump up the type whose literal is matching
    if hasattr(value, 'get'):
        # Seems we have an object
        # Bump up if the Literal field matches
        discriminatorscache = l._unionload_discriminatorcache.get(type_)  # type: Optional[Tuple[Optional[str], Optional[Dict[Any, Type]]]]

        # First time generate the deep inspection for literal
        if discriminatorscache is None:
            # type → {key: valueset}
            data = {t: discriminatorliterals(t) for t in args}
            # shared keys that have literals in every object of the union
            keys = reduce(lambda a, b: a.intersection(b), (set(v.keys()) for v in data.values()))  # type: Set[str]

            cachedict = {}
            if keys:
                key = keys.pop()
                for t, d in data.items():
                    for literal in d[key]:
                        cachedict[literal] = t
                discriminatorscache = key, cachedict
            else:
                discriminatorscache = None, None
            l._unionload_discriminatorcache[type_] = discriminatorscache

        # Cache is created, use it
        # It's a tuple key, {value: type}
        if discriminatorscache[1]:
            preferredtype = discriminatorscache[1].get(value.get(discriminatorscache[0]))
            if preferredtype:
                # Place best value on top
                sorted_args.remove(preferredtype)
                sorted_args.insert(0, preferredtype)

    # Try all types
    loaded_count = 0
    r = None
    for t in sorted_args:
        try:
            # Skip calling load()
            handler = l._indexcache.get(t)
            if handler is not None:
                f = handler
            else:
                try:
                    f = l._indexcache[t] = l.handlers[l.index(t)][1]
                except ValueError:
                    raise TypedloadValueError(
                        'Cannot deal with value of type %s (key of %s)' % (tname(t), tname(type_)),
                        value=value,
                        type_=t
                    )

            r = f(l, value, t)
            loaded_count += 1
            if not l.uniondebugconflict:
                # Do not try more if we are not debugging
                break
        except TypedloadException as e:
            annotation = Annotation(AnnotationType.UNION, t)
            e.trace.insert(0, TraceItem(value, type_, annotation))
            exceptions.append(e)

    if loaded_count == 1:
        # Loaded only once, all good
        return r
    elif loaded_count == 0:
        # Could not be loaded
        raise TypedloadValueError(
            'Value of %s could not be loaded into %s' % (tname(value_type), tname(type_)),
                value=value,
                type_=type_,
                exceptions=exceptions
        )
    else:
        # Loaded more than once, conflict
        raise TypedloadTypeError(
            'Value of %s could be loaded into %s %d times' % (tname(value_type), tname(type_), loaded_count),
                value=value,
                type_=type_,
                exceptions=exceptions
        )


def _enumload(l: Loader, value: Any, type_) -> Enum:
    """
    This loads something into an Enum.

    It tries with basic types first.

    If that fails, it tries to look for type annotations inside the
    Enum, and tries to use those to load the value into something
    that is compatible with the Enum.

    Of course if that fails too, a ValueError is raised.
    """
    try:
        # Try naïve conversion
        return type_(value)
    except Exception:
        pass

    # Try with the typing hints
    exceptions = []
    for _, t in get_type_hints(type_).items():
        try:
            return type_(l.load(value, t, annotation=Annotation(AnnotationType.UNION, t)))
        except Exception as e:
            exceptions.append(e)
    if len(type_.__members__) <= 10 and all(type(i.value) in l.basictypes for i in type_.__members__.values()):
        lst = '\nValue %s not between: ' % repr(value) + \
        ', '.join(repr(i.value) for i in type_.__members__.values())
    else:
        lst = ''
    raise TypedloadValueError(
        'Value of %s could not be loaded into %s%s' % (tname(type(value)), tname(type_), lst),
        value=value,
        type_=type_,
        exceptions=exceptions
    )


def _noneload(l: Loader, value: Any, type_) -> None:
    """
    Loads a value that can only be None,
    so it fails if it isn't
    """
    if value is None:
        return None
    raise TypedloadValueError('Not None', value=value, type_=type_)


def _datetimeload(l: Loader, value: Any, type_) -> Union[datetime.date, datetime.time, datetime.datetime]:
    try:
        if isinstance(value, str):
            return type_.fromisoformat(value)
        else:
            # This might be removed at some point in the future, but it will break data compatibility
            return type_(*value)
    except TypeError as e:
        raise TypedloadTypeError(str(e), type_=type_, value=value)
    except ValueError as e:
        raise TypedloadValueError(str(e), type_=type_, value=value)


def _patternload(l: Loader, value: Any, type_) -> re.Pattern:
    if hasattr(type, "__args__"):
        (input_type,) = type_.__args__
        if input_type in {bytes, str} and type(value) != input_type:
            raise TypedloadValueError('Got %s of type %s, expected %s' % (repr(value), tname(type(value)), tname(type_)), value=value, type_=type_)
    try:
        return re.compile(value)
    except re.error as e:
        raise TypedloadException(str(e), value=value, type_=type_)
    except TypeError as e:
        raise TypedloadTypeError(str(e), value=value, type_=type_)


def _timedeltaload(l: Loader, value, type_) -> datetime.timedelta:
    try:
        return type_(0, value)
    except TypeError as e:
        raise TypedloadTypeError(str(e), type_=type_, value=value)

def _get_attr_converter_type(c: "Callable"):
    """
    c is a converter function passed to an attr field

    it is supposed to have 1 parameter only

    If it's typed, return the type of the parameter. Otherwise return Any
    """
    hints = get_type_hints(c)
    if len(hints) > 0 and len(hints) <= 2:
        if 'return' in hints:
            del hints['return']
        return next(iter(hints.values()))
    return Any


def _attrload(l: Loader, value: Any, type_) -> Any:
    from attr._make import _Nothing as NOTHING

    fields = {i.name for i in type_.__attrs_attrs__}
    necessary_fields = set()
    type_hints = {i.name: (_get_attr_converter_type(i.converter) if i.converter else i.type) for i in type_.__attrs_attrs__}
    namesmap = {}  # type: Dict[str, str]

    for attribute in type_.__attrs_attrs__:
        if attribute.default is NOTHING and attribute.init:
            necessary_fields.add(attribute.name)

        # Manage name mangling
        if l.mangle_key in attribute.metadata:
            namesmap[attribute.metadata[l.mangle_key]] = attribute.name

    try:
        value = _mangle_names(namesmap, value, l.failonextra)
    except ValueError as e:
        raise TypedloadValueError(str(e), value=value, type_=type_)
    except AttributeError as e:
        raise TypedloadAttributeError(str(e), value=value, type_=type_)

    return _objloader(l, fields, necessary_fields, type_hints, value, type_)


def _strconstructload(l: Loader, value, type_):
    """
    Loader for all the types taking a string as single constructor parameter
    """
    try:
        return type_(value)
    except ValueError as e:
        raise TypedloadValueError(str(e), type_=type_, value=value)
    except TypeError as e:
        raise TypedloadTypeError(str(e), type_=type_, value=value)
    except Exception as e:
        raise TypedloadException(str(e), type_=type_, value=value)


def _newtypeload(l: Loader, value: Any, type_) -> Any:
    return l.load(value, type_.__supertype__)


def _iterload(l: Loader, value: Any, type_, function) -> Any:
    """
    Generic code to load iterables.

    function is for example list, tuple, set. The call to
    generate the destination type from an iterable.
    """
    if isinstance(value, dict):
        raise TypedloadTypeError('Unable to load dictionary as an iterable', value=value, type_=type_)
    t = type_.__args__[0]

    # Get function pointer for the handler
    cached_f = l._indexcache.get(t)

    if cached_f:
        f = cached_f
    else:
        try:
            f = l._indexcache[t] = l.handlers[l.index(t)][1]
        except ValueError:
            raise TypedloadTypeError(
                'Cannot deal with value of type %s' % tname(t),
                value=value,
                type_=t,
            )

    # load calling the handler directly, skipping load()
    try:
        ctr = count(1)
        if t in l.basictypes:
            return function((i if isinstance(i, t) else f(l, i, t) for i in compress(value, ctr)))
        elif is_union(t) and (types := set(uniontypes(t))).issubset(l.basictypes):
            return function((i if type(i) in types else f(l, i, t) for i in compress(value, ctr)))
        else:
            return function(map(f, repeat(l), compress(value, ctr), repeat(t)))
    except TypedloadException as e:
        index = next(ctr) - 2
        annotation = Annotation(AnnotationType.INDEX, index)
        e.trace.insert(0, TraceItem(value, type_, annotation))
        raise e
    except TypeError as e:
        raise TypedloadTypeError(str(e), value=value, type_=type_)
    except Exception as e:
        raise TypedloadTypeError('Exception is not a subclass of TypedloadException. Make sure all handlers only raise TypedloadException')
