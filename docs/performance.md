Performance
===========

The tests are done on my PC.

`typedload` manages to win quite a few benchmarks despite the competitors are compiled to binary `.so` files. Probably compiling it would make it win hands down. Feel free to help!

Negative values mean that the library could not do the test or returned incorrect values.

Using Python 3.11
-----------------

* `typedload` ![Downloads](https://pepy.tech/badge/typedload)
* `pydantic` ![Downloads](https://pepy.tech/badge/pydantic) is always slower
* `apischema` ![Downloads](https://pepy.tech/badge/apischema) is slower for nested data and faster otherwise
* `jsons` ![Downloads](https://pepy.tech/badge/jsons) is very slow and fails half the tests
* `dataclasses-json` ![Downloads](https://pepy.tech/badge/dataclasses-json) fails all the tests but is faster in one (yay)

![performance chart](3.11_realistic_union_of_objects_as_namedtuple.svg "Title")
![performance chart](3.11_load_list_of_floats_and_ints.svg "Title")
![performance chart](3.11_load_list_of_lists.svg "Title")
![performance chart](3.11_load_list_of_NamedTuple_objects.svg "Title")
![performance chart](3.11_load_big_dictionary.svg "Title")
![performance chart](3.11_load_list_of_ints.svg "Title")


Run the tests
-------------

Generate the performance chart locally.

```bash
python3 -m venv perfvenv
. perfvenv/bin/activate
pip install apischema pydantic attrs dataclasses-json jsons
export PYTHONPATH=$(pwd)
make gnuplot
```
