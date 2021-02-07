"""
typedload
Exceptions
"""

# Copyright (C) 2018-2020 Salvo "LtWorf" Tomaselli
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
    ('value', Union[str, int, Type]),
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
    def __init__(
            self,
            description: str,
            trace: Optional[List[TraceItem]] = None,
            value: Any=None,
            type_: Optional[Type] = None,
            exceptions: Optional[List[Exception]] = None) -> None:
        super().__init__(description)
        self.trace = trace if trace else []
        self.value = value
        self.type_ = type_
        self.exceptions = exceptions if exceptions else []

    @property
    def path(self) -> str:
        '''
        Compact representation of where in the data the exception happened
        '''
        path = []
        for i in self.trace:
            if i.annotation:
                path.append('[%d]' % i.annotation[1] if isinstance(i.annotation[1], int) else str(i.annotation[1]))
            else:
                path.append(str(None))
        if path and path[0] == str(None):
            path[0] = ''
        return '.'.join(path)

    @property
    def strtrace(self):
        '''
        Returns a string representation of the stacktrace where the exception happened.
        '''
        def compress_value(v: Any) -> str:
            v = repr(v)
            if len(v) > 30:
                return v[:27] + '...'
            return v
        e = '%s\nValue: %s\nType: %s\n' % (
            super().__str__(),
            compress_value(self.value),
            self.type_
        )
        if self.trace:
            e += '\nLoad trace:\n'
        for i in self.trace[-2:]:
            e += 'Type: %s ' % i.type_
            if i.annotation:
                e += 'Annotation: (%s %s) ' % (i.annotation[0], i.annotation[1])
            e += 'Value: %s\n' % compress_value(i.value)
        return e

    def __str__(self) -> str:
        return '\n'.join(self.args) + '\nPath: ' + self.path


class TypedloadValueError(TypedloadException, ValueError):
    """
    Exception class, subclass of ValueError.
    See the documentation of TypedloadException for more details.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class TypedloadTypeError(TypedloadException, TypeError):
    """
    Exception class, subclass of TypeError.
    See the documentation of TypedloadException for more details.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class TypedloadAttributeError(TypedloadException, AttributeError):
    """
    Exception class, subclass of AttributeError.
    See the documentation of TypedloadException for more details.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
