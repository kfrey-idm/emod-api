import setuptools
from setuptools.extension import Extension
import emod_api

with open("README.md", "r") as fh:
    long_description = fh.read()
    ext_name = "emod_api"

with open("requirements.txt", "r") as requirements_file:
    requirements = requirements_file.read().split("\n")

setuptools.setup(
    name=ext_name,
    version=emod_api.__version__,
    author="Daniel Bridenbecker",
    author_email="dbridenbecker@idmod.org",
    description="IDM's EMOD API support scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/InstituteforDiseaseModeling/emod-api",
    packages=setuptools.find_packages(exclude=["tests","emod_api/dtk_tools"]),
    include_package_data=True,
    setup_requires=['wheel'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
