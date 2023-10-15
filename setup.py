from setuptools import setup

setup(
    name="pylatexpand",
    python_requires=">=3.10.3",
    version="1.0",
    packages=["pylatexpand"],
    entry_points={
        "console_scripts": ["pylatexpand=bin:main"],
    },
)
