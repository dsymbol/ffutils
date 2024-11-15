from setuptools import find_packages, setup

setup(
    name="ffutils",
    version="",
    packages=find_packages(),
    url="https://github.com/dsymbol/ffutils",
    license="OSI Approved :: MIT License",
    author="dsymbol",
    description="Utilities for working with ffmpeg",
    install_requires=["rich==13.9.4", "platformdirs==4.3.6", "requests"],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
