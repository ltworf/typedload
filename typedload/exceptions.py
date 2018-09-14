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
    FIELD = 'field'
    INDEX = 'index'


Annotation = NamedTuple('Annotation', [
    ('annotation_type', AnnotationType),
    ('value', Union[str, int]),
])


TraceItem = NamedTuple('TraceItem', [
    ('value', Any),
    ('type', Type),
    ('annotation', Optional[Annotation]),
])


class TypedloadException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.trace = []  # type: List[TraceItem]
        self.value = kwargs.get('value')  # type: Any
        self.type_ = kwargs.get('type_')  # type: Optional[Type]
        self.exceptions = kwargs.get('exceptions', [])  # type: List[Exception]


class TypedloadValueError(TypedloadException, ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TypedloadTypeError(TypedloadException, TypeError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TypedloadAttributeError(TypedloadException, AttributeError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
