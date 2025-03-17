from setuptools import setup, find_packages

setup(
    name="hottopoteto-linguistics",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "hottopoteto.packages": [
            "linguistics=hottopoteto_linguistics:register",
        ],
    },
    install_requires=["hottopoteto"],
)
