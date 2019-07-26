import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graphene-framework",
    version="0.0.2",
    author="Dmitrii Donetskii",
    author_email="donetskiydmitriy@gmail.com",
    description="Framework based on graphene",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Donnyyyyy/graphene-superstructure",
    packages=setuptools.find_packages(),
    install_requires=[
        "graphene==2.1.7",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
