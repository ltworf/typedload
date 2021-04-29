Errors in typedload
===================

All exceptions are subclasses of `TypedloadException`.

To make sure of that, there is an assertion in place that will fail if a type handler is misbehaving and raising the wrong type of exception.

The exceptions have a clear user message, but they offer an API to expose precise knowledge of the problem.

String trace
------------

By default when an error occurrs the path within the data structure is shown.

```python
from typing import *
import typedload

class Thing(NamedTuple):
    value: int

class Data(NamedTuple):
    field1: List[Thing]
    field2: Tuple[Thing, ...]


typedload.load({'field1': [{'value': 12}, {'value': 'a'}], 'field2': []}, Data)
```

```python
TypedloadValueError: invalid literal for int() with base 10: 'a'
Path: .field1.[1].value
```

The path in the string description tells where the wrong value was found.

Trace
-----

To be able to locate where in the data an exception happened, `TypedloadException` has the `trace` property, which contains a list `TraceItem`, which help to track where the exception happened.

This can be useful to do more clever error handling.

For example:

```python
try:
    typedload.load([1, 2, 'a'], List[int])
except Exception as e:
    print(e.trace[-1])
```

Will raise an exception and print the last element in the trace

```python
TraceItem(value='a', type_=<class 'int'>, annotation=Annotation(annotation_type=<AnnotationType.INDEX: 'index'>, value=2))
```

Another example, with an object:

```python

class O(NamedTuple):
    data: List[int]

try:
    typedload.load({'data': [1, 2, 'a']}, O)
except Exception as e:
    for i in e.trace:
        print(i)
```

Will print the entire trace:

```python
TraceItem(value={'data': [1, 2, 'a']}, type_=<class '__main__.O'>, annotation=None)
TraceItem(value=[1, 2, 'a'], type_=typing.List[int], annotation=Annotation(annotation_type=<AnnotationType.FIELD: 'field'>, value='data'))
TraceItem(value='a', type_=<class 'int'>, annotation=Annotation(annotation_type=<AnnotationType.INDEX: 'index'>, value=2))
```

And checking the `annotation` field it is possible to find out that the issue happened in *data* at index *2*.

Union
-----

Because it is normal for a union of n types to generate n-1 exceptions, a union which fails generated n exceptions.

Typedload has no way of knowing which of those is the important exception that was expected to succeed and instead puts all the exceptions inside the `exception` field of the parent exception.

So all the sub exceptions can be investigated to decide which one is the most relevant one.


Raise exceptions in custom handlers
-----------------------------------

To find the path where the wrong value was found, typedload needs to trace the execution by using annotations.

This is used in handlers that do recursive calls to the loader.

See the source code of the handlers for Union and NamedTuple to see how this is done.
