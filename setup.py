from setuptools import setup

setup(
    name="pylatexpand",
    python_requires="~=3.11",
    version="1.0",
    packages=["pylatexpand"],
    install_requires=[],
    entry_points={
        "console_scripts": ["pylatexpand=bin:main"],
    },
)
