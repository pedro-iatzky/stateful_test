from setuptools import setup


setup(
    name="stateful_test",
    version="0.1",
    author="Pedro Iatzky",
    author_email="iatzkypedro@gmail.com",
    description="A simpleframework for performing integration tests",
    packages=["stateful_test"],
    python_requires=">=3.5",
    extras_require={
        'dotenv': ['python-dotenv'],
        'dev': [
            'pytest>=3'
        ]
    },
    entry_points={
        'console_scripts': [
            'stateful_test = stateful_test.main:main'
        ]
    }
)
