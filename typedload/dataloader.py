"""
typedload
Module to load data into typed data structures
"""

# Copyright (C) 2018-2019 Salvo "LtWorf" Tomaselli
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
from typing import *
# It is for some reason not imported with * on Python 3.5.2
from typing import FrozenSet

from .exceptions import *
from .typechecks import *


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

    These parameters can be set as named arguments in the constructor
    or they can be set later on.

    The constructor will accept any named argument, but only the documented
    ones have any effect. This is to allow custom handlers to have their
    own parameters as well.

    There is support for:
        * Basic python types (int, str, bool, float, NoneType)
        * NamedTuple
        * Enum
        * Optional[SomeType]
        * List[SomeType]
        * Dict[TypeA, TypeB]
        * Tuple[TypeA, TypeB, TypeC]
        * Set[SomeType]
        * Union[TypeA, TypeB]
        * ForwardRef

    Using unions is complicated. If the types in the union are too
    similar to each other, it is easy to obtain an unexpected type.
    """

    def __init__(self, **kwargs):
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

        # The list of handlers to use to load the data.
        # It gets iterated in order, and the first condition
        # that matches is used to load the value.
        self.handlers = [
            (is_nonetype, _noneload),
            (is_union, _unionload),
            (lambda type_: type_ in self.basictypes, _basicload),
            (is_enum, _enumload),
            (is_tuple, _tupleload),
            (is_list, _listload),
            (is_dict, _dictload),
            (is_set, _setload),
            (is_frozenset, _frozensetload),
            (is_namedtuple, _namedtupleload),
            (is_dataclass, _namedtupleload),
            (is_forwardref, _forwardrefload),
            (lambda type_: type_ in {datetime.date, datetime.time, datetime.datetime}, _datetimeload),
        ]  # type: List[Tuple[Callable[[Type[T]], bool], Callable[['Loader', Any, Type[T]], T]]]

        for k, v in kwargs.items():
            setattr(self, k, v)

    def index(self, type_: Type[T]) -> int:
        """
        Returns the index in the handlers list
        that matches the given type.

        If no condition matches, ValueError is raised.
        """
        for i, cond in ((q[0], q[1][0]) for q in enumerate(self.handlers)):
            try:
                match = cond(type_)
            except:
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
        """
        try:
            index = self.index(type_)
        except ValueError:
            raise TypedloadTypeError(
                'Cannot deal with value of type %s' % type_,
                value=value,
                type_=type_
            )

        # Add type to known types, to resolve ForwardRef later on
        if self.frefs is not None and hasattr(type_, '__name__'):
            tname = type_.__name__
            if tname not in self.frefs:
                self.frefs[tname] = type_

        func = self.handlers[index][1]

        if self.dictequivalence:
            # Convert argparse.Namespace to dictionary
            if hasattr(value, '_get_kwargs'):
                value = {k: v for k,v in value._get_kwargs()}

        try:
            return func(self, value, type_)
        except Exception as e:
            assert isinstance(e, TypedloadException)
            e.trace.insert(0, TraceItem(value, type_, annotation))
            raise e


def _forwardrefload(l: Loader, value: Any, type_: type) -> Any:
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


def _basicload(l: Loader, value: Any, type_: type) -> Any:
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
            raise TypedloadValueError('Not of type %s' % type_, value=value, type_=type_)
    return value


def _listload(l: Loader, value, type_) -> List:
    """
    This loads into something like List[int]
    """
    t = type_.__args__[0]
    try:
        return [l.load(v, t, annotation=Annotation(AnnotationType.INDEX, i)) for i, v in enumerate(value)]
    except TypeError as e:
        if isinstance(e, TypedloadException):
            raise
        raise TypedloadTypeError(str(e), value=value, type_=type_)


def _dictload(l: Loader, value, type_) -> Dict:
    """
    This loads into something like Dict[str,str]

    Recursively loads both keys and values.
    """
    key_type, value_type = type_.__args__
    try:
        return {
            l.load(k, key_type, annotation=Annotation(AnnotationType.KEY, k)): l.load(v, value_type, annotation=Annotation(AnnotationType.VALUE, v))
            for k, v in value.items()}
    except AttributeError as e:
        raise TypedloadAttributeError(str(e), type_=type_, value=value)


def _setload(l: Loader, value, type_) -> Set:
    """
    This loads into something like Set[int]
    """
    t = type_.__args__[0]
    return {l.load(i, t) for i in value}


def _frozensetload(l: Loader, value, type_) -> FrozenSet:
    """
    This loads into something like FrozenSet[int]
    """
    t = type_.__args__[0]
    return frozenset(l.load(i, t) for i in value)


def _tupleload(l: Loader, value, type_) -> Tuple:
    """
    This loads into something like Tuple[int,str]
    """
    if HAS_TUPLEARGS:
        args = type_.__args__
    else:
        args = type_.__tuple_params__

    if len(args) == 2 and args[1] == ...: # Tuple[something, ...]
        return tuple(l.load(i, args[0]) for i in value)
    else: # Tuple[something, something, somethingelse]
        if l.failonextra and len(value) > len(args):
            raise TypedloadValueError('Value is too long for type %s' % type_, value=value, type_=type_)
        elif len(value) < len(args):
            raise TypedloadValueError('Value is too short for type %s' % type_, value=value, type_=type_)
        return tuple(l.load(v, t, annotation=Annotation(AnnotationType.INDEX, i)) for i, (v, t) in enumerate(zip(value, args)))


def _namedtupleload(l: Loader, value: Dict[str, Any], type_) -> Tuple:
    """
    This loads a Dict[str, Any] into a NamedTuple.
    """
    if not hasattr(type_, '__dataclass_fields__'):
        fields = set(type_._fields)
        optional_fields = set(getattr(type_, '_field_defaults', {}).keys())
        type_hints = type_._field_types
    else:
        #dataclass
        import dataclasses
        fields = set(type_.__dataclass_fields__.keys())
        optional_fields = {k for k,v in type_.__dataclass_fields__.items() if not (isinstance(getattr(v, 'default', dataclasses._MISSING_TYPE()), dataclasses._MISSING_TYPE) and isinstance(getattr(v, 'default_factory', dataclasses._MISSING_TYPE()), dataclasses._MISSING_TYPE))}
        type_hints = {k: v.type for k,v in type_.__dataclass_fields__.items()}

        #Name mangling

        # Prepare the list of the needed name changes
        transforms = []  # type: List[Tuple[str, str]]
        for field in fields:
            if type_.__dataclass_fields__[field].metadata:
                name = type_.__dataclass_fields__[field].metadata.get('name')
                if name:
                    transforms.append((field, name))
        # Do the needed name changes
        if transforms:
            value = value.copy()
            for pyname, dataname in transforms:
                if dataname in value:
                    tmp = value[dataname]
                    del value[dataname]
                    value[pyname] = tmp

    necessary_fields = fields.difference(optional_fields)
    try:
        vfields = set(value.keys())
    except AttributeError as e:
        raise TypedloadAttributeError(str(e), value=value, type_=type_)

    if necessary_fields.intersection(vfields) != necessary_fields:
        raise TypedloadValueError(
            'Value does not contain fields: %s which are necessary for type %s' % (
                necessary_fields.difference(vfields),
                type_
            ),
            value=value,
            type_=type_,
        )

    fieldsdiff = vfields.difference(fields)
    if l.failonextra and len(fieldsdiff):
        extra = ', '.join(fieldsdiff)
        raise TypedloadValueError(
            'Dictionary has unrecognized fields: %s and cannot be loaded into %s' % (extra, type_),
            value=value,
            type_=type_,
        )

    params = {}
    for k, v in value.items():
        if k not in fields:
            continue
        params[k] = l.load(
            v,
            type_hints[k],
            annotation=Annotation(AnnotationType.FIELD, k),
        )
    return type_(**params)


def _unionload(l: Loader, value, type_) -> Any:
    """
    Loads a value into a union.

    Basically this iterates all the types inside the
    union, until one that doesn't raise an exception
    is found.

    If no suitable type is found, an exception is raised.
    """
    try:
        args = uniontypes(type_)
    except AttributeError:
        raise TypedloadAttributeError('The typing API for this Python version is unknown')

    # Do not convert basic types, if possible
    if type(value) in args.intersection(l.basictypes):
        return value

    exceptions = []

    # Try all types
    for t in args:
        try:
            return l.load(value, t, annotation=Annotation(AnnotationType.UNION, t))
        except Exception as e:
            exceptions.append(e)
    raise TypedloadValueError(
        'Value could not be loaded into %s' % type_,
            value=value,
            type_=type_,
            exceptions=exceptions
    )


def _enumload(l: Loader, value, type_) -> Enum:
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
    except:
        pass

    # Try with the typing hints
    for _, t in get_type_hints(type_).items():
        try:
            return type_(l.load(value, t))
        except:
            pass
    raise TypedloadValueError(
        'Value could not be loaded into %s' % type_,
        value=value,
        type_=type_
    )


def _noneload(l: Loader, value, type_) -> None:
    """
    Loads a value that can only be None,
    so it fails if it isn't
    """
    if value is None:
        return None
    raise TypedloadValueError('Not None', value=value, type_=type_)


def _datetimeload(l: Loader, value, type_) -> Union[datetime.date, datetime.time, datetime.datetime]:
    return type_(*value)
