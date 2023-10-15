from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    name="pylatexpand",
    python_requires=">=3.10.3",
    version="1.0",
    entry_points={
        "console_scripts": ["pylatexpand=bin:main"],
    },
)
