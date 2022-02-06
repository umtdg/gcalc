import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="gcalc",
    version="0.0.4",
    author="Umut Dag",
    author_email="umut.dag@ulakhaberlesme.com.tr",
    description="Simple grade calculator via command line",
    long_description="Long description",
    long_description_content_type="text/markdown",
    url="https://github.com/umtdg/gcalc",
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    packages=setuptools.find_packages("."),
    python_requires=">=3.9",
    install_requires=[
        "readline",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "gcalc=gcalc:main",
        ]
    }
)
