# import pathlib
# from setuptools import setup, find_packages

# # The directory containing this file
# HERE = pathlib.Path(__file__).parent

# # The text of the README file
# README = (HERE / "README.md").read_text()

# # This call to setup() does all the work
# setup(
#     name="sbr",
#     version="1.0.0",
#     description="Access the SportsbookReview GraphQL endpoint.",
#     long_description=README,
#     long_description_content_type="text/markdown",
#     url="https://github.com/JeMorriso/SBR",
#     author="Jeremy Morrison",
#     author_email="jeremy.morrison36@gmail.com",
#     license="MIT",
#     classifiers=[
#         "License :: OSI Approved :: MIT License",
#         "Programming Language :: Python :: 3",
#         "Programming Language :: Python :: 3.8",
#     ],
#     packages=find_packages(where="pysbr"),
#     keywords="sportsbookreview betting api gambling sports graphql odds",
#     include_package_data=True,
#     install_requires=["gql", "pandas", "pytz", "pyyaml"],
#     # entry_points={
#     #     "console_scripts": [
#     #         "realpython=reader.__main__:main",
#     #     ]
#     # },
# )
