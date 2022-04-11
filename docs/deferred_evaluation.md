Deferred evaluation
===================

[PEP 563](https://peps.python.org/pep-0563/) defines deferred evaluation of types.

It will most likely be superseeded by [PEP 649](https://peps.python.org/pep-0649/) because of the following issues:

* `eval()` is slow
* `eval()` might not be present to save space
* only works for types defined at module level

It is enabled with `from __future__ import annotations`.

When it is enabled you must set `pep563=True` in your loader object, to (hopefully) make it keep working (it will not work in many corner cases).

```python
from __future__ import annotations

class A(NamedTuple):
    a: Optional[int]


load({'a':1}, A)
# TypedloadValueError: ForwardRef 'Optional[int]' unknown

load({'a':1}, A, pep563=True)
# A(a=1)
```

If you have such a simple case it will work fine. In more complicated cases it will not work. In those cases the solution is to not do the import.

This feature will most likely be removed once the decision for the newer PEP is settled.

It is not part of Python and you should not expect that typedload will keep it.
