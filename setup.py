"""Compatibility shim for older versions of pip.

Package metadata lives in pyproject.toml. This file lets pip versions without
PEP 660 editable-install support install the project during local development.
"""

from setuptools import setup


setup(
    name="capcut-subtitles",
    version="0.1.0",
    packages=["capcut_subtitles"],
    install_requires=["tomli>=2.0; python_version < '3.11'"],
    entry_points={
        "console_scripts": [
            "subtitles=capcut_subtitles.cli:main",
            "capcut-subtitles=capcut_subtitles.cli:main",
        ]
    },
)
