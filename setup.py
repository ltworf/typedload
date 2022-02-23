#!/usr/bin/python3
# This file is auto generated. Do not modify
from distutils.core import setup
setup(
    name='typedload',
    version='2.16',
    description='Load and dump data from json-like format into typed data structures',
    long_description="=========\ntypedload\n=========\n\nLoad and dump json-like data into typed data structures in Python3, enforcing\na schema on the data.\n\nThis module provides an API to load dictionaries and lists (usually loaded\nfrom json) into Python's NamedTuples, dataclass, sets, enums, and various\nother typed data structures; respecting all the type-hints and performing\ntype checks or casts when needed.\n\nIt can also dump from typed data structures to json-like dictionaries and lists.\n\nIt is very useful for projects that use Mypy and deal with untyped data\nlike json, because it guarantees that the data will follow the specified schema.\n\nIt is released with a GPLv3 license.\n\n\n=======\nExample\n=======\n\nFor example this dictionary, loaded from a json:\n\n\n>>>\ndata = {\n    'users': [\n        {\n            'username': 'salvo',\n            'shell': 'bash',\n            'sessions': ['pts/4', 'tty7', 'pts/6']\n        },\n        {\n            'username': 'lop'\n        }\n    ],\n}\n\n\n\nCan be treated more easily if loaded into this type:\n\n\n>>>\n@dataclasses.dataclass\nclass User:\n    username: str\n    shell: str = 'bash'\n    sessions: List[str] = dataclasses.field(default_factory=list)\n>>>\nclass Logins(NamedTuple):\n    users: List[User]\n\n\nAnd the data can be loaded into the structure with this:\n\n\n>>>\nt_data = typedload.load(data, Logins)\n\n\nAnd then converted back:\n\n\n>>>\ndata = typedload.dump(t_data)\n\n\n===============\nSupported types\n===============\n\nSince this is not magic, not all types are supported.\n\nThe following things are supported:\n\n * Basic python types (int, str, bool, float, NoneType)\n * NamedTuple\n * Enum\n * Optional[SomeType]\n * List[SomeType]\n * Dict[TypeA, TypeB]\n * Tuple[TypeA, TypeB, TypeC] and Tuple[SomeType, ...]\n * Set[SomeType]\n * Union[TypeA, TypeB]\n * dataclass (requires Python 3.7)\n * attr.s\n * ForwardRef (Refer to the type in its own definition)\n * Literal (requires Python 3.8)\n * TypedDict (requires Python 3.8)\n * datetime.date, datetime.time, datetime.datetime\n * Path\n * IPv4Address, IPv6Address\n * typing.Any\n * typing.NewType\n\n==========\nUsing Mypy\n==========\n\nMypy and similar tools work without requiring any plugins.\n\n\n>>>\n# This is treated as Any, no checks done.\ndata = json.load(f)\n>>>\n# This is treated as Dict[str, int]\n# but there will be runtime errors if the data does not\n# match the expected format\ndata = json.load(f)  # type: Dict[str, int]\n>>>\n# This is treated as Dict[str, int] and an exception is\n# raised if the actual data is not Dict[str, int]\ndata = typedload.load(json.load(f), Dict[str, int])\n\n\nSo when using Mypy, it makes sense to make sure that the type is correct,\nrather than hoping the data will respect the format.\n\n=========\nExtending\n=========\n\nType handlers can easily be added, and existing ones can be replaced, so the library is fully cusomizable and can work with any type.\n\nInheriting a base class is not required.\n\n=======\nInstall\n=======\n\n* `pip install typedload`\n* `apt install python3-typedload`\n* Latest and greatest .deb file is in [releases](https://github.com/ltworf/typedload/releases)\n\n=============\nDocumentation\n=============\n\n* [Online documentation](https://ltworf.github.io/typedload/)\n* In the docs/ directory\n\nThe tests are hard to read but provide more in depth examples of\nthe capabilities of this module.\n\n=======\nUsed by\n=======\n\nAs dependency, typedload is used by those entities. Feel free to add to the list.\n\n* Several universities around the world\n",
    url='https://ltworf.github.io/typedload/',
    author="Salvo 'LtWorf' Tomaselli",
    author_email='tiposchi@tiscali.it',
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='typing types mypy json',
    packages=['typedload'],
    package_data={"typedload": ["py.typed", "__init__.pyi"]},
)
