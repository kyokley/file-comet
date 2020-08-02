from setuptools import setup, find_packages

setup(
    name="File Comet",

    version="0.1",

    description="Quickly share a single file over HTTP",
    long_description="Quickly share a single file over HTTP",

    url="https://github.com/kyokley/file-comet",

    author="Kevin Yokley",
    author_email="kyokley2@gmail.com",

    license="MIT",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
    ],

    packages=find_packages(),

    install_requires=[
    ],

    entry_points={
        "console_scripts": [
            "comet = server:main",
        ],
    },
)
