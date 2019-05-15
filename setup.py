import os
import re

from setuptools import setup

_init_file = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "stateful_test", "__init__.py"
)
with open(_init_file, 'rt') as fl:
    version = re.search(r"__version__ = \"(.*?)\"", fl.read()).group(1)

setup(
    name="stateful_test",
    version=version,
    author="Pedro Iatzky",
    author_email="iatzkypedro@gmail.com",
    description="A simpleframework for performing integration tests",
    packages=["stateful_test"],
    python_requires=">=3.5",
    install_requires=[
        'gevent>=1.4.0',
    ],
    extras_require={
        'dev': [
            'pytest>=3',
            'requests>=2.9.1',
        ]
    },
    entry_points={
        'console_scripts': [
            'stateful_test = stateful_test.main:main'
        ]
    }
)
