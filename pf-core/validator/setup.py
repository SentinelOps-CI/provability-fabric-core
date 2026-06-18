from setuptools import find_packages, setup

setup(
    name="pf-core-validator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "jsonschema>=4.21.0",
        "referencing>=0.35.0",
    ],
    entry_points={"console_scripts": ["pf=pf_core.cli:main"]},
)
