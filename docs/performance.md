Performance
===========

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
