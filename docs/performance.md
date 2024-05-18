[THE PROJECT MIGRATED TO CODEBERG](https://ltworf.codeberg.page/typedload/)

Performance
===========

Negative values mean that the library could not do the test or returned incorrect values.

The tests are done on my PC. The following libraries are tested:

* `typedload`, the 3 most recent versions
* `pydantic2` years of work to rewrite it in Rust, still managing to lose some benchmarks 😅
* `apischema` is slower for nested data and faster otherwise

Using Python 3.11
-----------------

![performance chart](3.11_realistic_union_of_objects_as_namedtuple.svg "Load realistic union of objects")
![performance chart](3.11_load_list_of_floats_and_ints.svg "Load list of floats and ints")
![performance chart](3.11_load_list_of_lists.svg "Load list of lists")
![performance chart](3.11_load_list_of_NamedTuple_objects.svg "Load list of NamedTuple")
![performance chart](3.11_load_big_dictionary.svg "Load big dictionary")
![performance chart](3.11_load_list_of_ints.svg "Load list of ints")
![performance chart](3.11_dump_objects.svg "Dump objects")
![performance chart](3.11_fail_load_list_of_floats_and_ints.svg "Load list of floats and ints which raises an exception")
![performance chart](3.11_fail_realistic_union_of_objects_as_namedtuple.svg "Load realistic union of objects which raises an exception")


Using Pypy 7.3.12
-----------------

![performance chart](3.9_realistic_union_of_objects_as_namedtuple.svg "Load realistic union of objects")
![performance chart](3.9_load_list_of_floats_and_ints.svg "Load list of floats and ints")
![performance chart](3.9_load_list_of_lists.svg "Load list of lists")
![performance chart](3.9_load_list_of_NamedTuple_objects.svg "Load list of NamedTuple")
![performance chart](3.9_load_big_dictionary.svg "Load big dictionary")
![performance chart](3.9_load_list_of_ints.svg "Load list of ints")
![performance chart](3.9_dump_objects.svg "Dump objects")
![performance chart](3.9_fail_load_list_of_floats_and_ints.svg "Load list of floats and ints which raises an exception")
![performance chart](3.9_fail_realistic_union_of_objects_as_namedtuple.svg "Load realistic union of objects which raises an exception")


Run the tests
-------------

Generate the performance chart locally.

```bash
python3 -m venv perfvenv
. perfvenv/bin/activate
pip install apischema pydantic attrs
export PYTHONPATH=$(pwd)
make gnuplot
```
