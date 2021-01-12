import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="python-sbr",
    version="0.2.0",
    description="Access the SportsbookReview GraphQL endpoint.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/JeMorriso/PySBR",
    author="Jeremy Morrison",
    author_email="jeremy.morrison36@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "tests.*"]),
    keywords="""
        sportsbookreview sportsbook review betting api gambling sports graphql odds
        lines moneyline
    """,
    include_package_data=True,
    install_requires=["gql", "pandas", "pytz", "pyyaml"],
)
