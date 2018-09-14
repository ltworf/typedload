# typedload
# Exceptions

# Copyright (C) 2018 Salvo "LtWorf" Tomaselli
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


from enum import Enum
from typing import Any, List, NamedTuple, Optional, Type, Union


class AnnotationType(Enum):
    """
    The types of annotation, used by different loaders.

    FIELD is the name of a field
    INDEX is the numerical index of a value, in subscriptable objects-
    """
    FIELD = 'field'
    INDEX = 'index'
    FORWARDREF = 'forwardref'
    KEY = 'key'
    VALUE = 'value'
    UNION = 'union'


Annotation = NamedTuple('Annotation', [
    ('annotation_type', AnnotationType),
    ('value', Union[str, int]),
])


TraceItem = NamedTuple('TraceItem', [
    ('value', Any),
    ('type_', Type),
    ('annotation', Optional[Annotation]),
])


class TypedloadException(Exception):
    """
    Exception which exposes some extra fields.

    trace:
        It is a list of all the recursive invocations of load(), with the
        parameters used.
        Very useful to locate the issue.
        The annotation is used by complex loaders that call load() more than
        once, to indicate in which step the error occurred.
        For example a list loader will use it to indicate the index which had
        the exception, and a NamedTuple loader will use it to indicate the name
        of the field which generated the exception.

    value:
        contains the value that could not be loaded.

    type_:
        contains the type in which the value could not be loaded.

    exceptions:
        A list of exceptions that happened during the loading.
        This is for now only used by the Union loader, to list all the
        exceptions that occurred during the various attempts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.trace = []  # type: List[TraceItem]
        self.value = kwargs.get('value')  # type: Any
        self.type_ = kwargs.get('type_')  # type: Optional[Type]
        self.exceptions = kwargs.get('exceptions', [])  # type: List[Exception]

    def __str__(self) -> str:
        def compress_value(v: Any) -> str:
            v = str(v)
            if len(v) > 80:
                return v[:77] + '...'
            return v
        e = '%s\nValue: %s\nType: %s\n' % (
            super().__str__(),
            compress_value(self.value),
            self.type_
        )
        if self.trace:
            e += '\nLoad trace:\n'
        for i in self.trace:
            e += 'Type: %s ' % i.type_
            if i.annotation:
                e += 'Annotation: (%s %s) ' % (i.annotation[0], i.annotation[1])
            e += 'Value: %s\n' % compress_value(i.value)
        return e


class TypedloadValueError(TypedloadException, ValueError):
    """
    Exception class, subclass of ValueError.
    See the documentation of TypedloadException for more details.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TypedloadTypeError(TypedloadException, TypeError):
    """
    Exception class, subclass of TypeError.
    See the documentation of TypedloadException for more details.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TypedloadAttributeError(TypedloadException, AttributeError):
    """
    Exception class, subclass of AttributeError.
    See the documentation of TypedloadException for more details.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
