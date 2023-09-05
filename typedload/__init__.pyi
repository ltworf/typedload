from typing import Set, TypeVar, Type, Any, Optional, Dict, List, Tuple, Callable

from .dataloader import Loader
from .datadumper import Dumper

# Load and dump take **kwargs for backwards-compatibility.
# This interface file intentionally omits **kwargs so that
# typos can be caught by static type checkers.
# If you want to extend Loader or Dumper in a type-safe manner
# you should subclass them (instead of using **kwargs).

__all__ = [
    'dataloader',
    'load',
    'datadumper',
    'dump',
    'typechecks',
]

T = TypeVar('T')

def load(
    value: Any,
    type_: Type[T],
    basictypes: Set[Type[Any]] = ...,
    basiccast: bool = ...,
    failonextra: bool = ...,
    raiseconditionerrors: bool = ...,
    frefs: Optional[Dict[str, Type[Any]]] = ...,
    dictequivalence: bool = ...,
    mangle_key: str = ...,
    uniondebugconflict: bool = ...,
    strconstructed: Set[Type[Any]] = ...,
    handlers: List[
        Tuple[Callable[[Any], bool], Callable[[Loader, Any, Type[Any]], Any]]
    ] = ...,
    pep563: bool = ...,
) -> T: ...

def dump(
    value: Any,
    hidedefault: bool = ...,
    isodates: bool = ...,
    raiseconditionerrors: bool = ...,
    mangle_key: str = ...,
    handlers: List[Tuple[Callable[[Any], bool], Callable[['Dumper', Any], Any]]] = ...,
    strconstructed: Set[Type[Any]] = ...,
) -> Any: ...
