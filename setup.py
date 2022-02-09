"""
Setup file for xsequence Package
------------------
xsequence: Package to manage particle accelerator lattices and interface to different simulation codes
"""


import pathlib

import setuptools

MODULE_NAME = "xsequence"
# The directory containing this file
TOPLEVEL_DIR = pathlib.Path(__file__).parent.absolute()
ABOUT_FILE = TOPLEVEL_DIR / MODULE_NAME / "__init__.py"
README = TOPLEVEL_DIR / "README.md"


def about_package(init_posixpath: pathlib.Path) -> dict:
    """
    Return package information defined with dunders in __init__.py as a dictionary, when
    provided with a PosixPath to the __init__.py file.
    """
    about_text: str = init_posixpath.read_text()
    return {
        entry.split(" = ")[0]: entry.split(" = ")[1].strip('"')
        for entry in about_text.strip().split("\n")
        if entry.startswith("__")
    }


ABOUT_XSEQUENCE = about_package(ABOUT_FILE)

with README.open("r") as docs:
    long_description = docs.read()

# Dependencies for the package itself
DEPENDENCIES = [
    "numpy>=1.19.0",
    "scipy>=1.5.0",
    "pandas>=1.0",
    "matplotlib>=3.3.2",
    "cpymad>=1.8.1", 
    "xtrack@https://github.com/xsuite/xtrack/tarball/main", 
    "accelerator-toolbox",
    "xdeps@https://github.com/xsuite/xdeps/tarball/main",
    "lark",
    "rich",
    ]

# Extra dependencies
EXTRA_DEPENDENCIES = {
    "test": ["pytest>=5.2", "pytest-cov>=2.9"],
    "doc": ["sphinx", "sphinx_rtd_theme"],
}

EXTRA_DEPENDENCIES.update({"all": [elem for list_ in EXTRA_DEPENDENCIES.values() for elem in list_]})

setuptools.setup(
    name=ABOUT_XSEQUENCE["__title__"],
    version=ABOUT_XSEQUENCE["__version__"],
    description=ABOUT_XSEQUENCE["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=ABOUT_XSEQUENCE["__author__"],
    author_email=ABOUT_XSEQUENCE["__author_email__"],
    url=ABOUT_XSEQUENCE["__url__"],
    packages=setuptools.find_packages(include=(MODULE_NAME,)),
    include_package_data=True,
    python_requires=">=3.6",
    license=ABOUT_XSEQUENCE["__license__"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    install_requires=DEPENDENCIES,
    tests_require=EXTRA_DEPENDENCIES["test"],
    extras_require=EXTRA_DEPENDENCIES,
)
