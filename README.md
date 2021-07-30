# Data Science Tools

![](https://github.com/earthastronaut/data_science_tools/workflows/Project%20Tests/badge.svg)
[![](docs/badges/coverage.svg)](/docs/coverage.report)
![](docs/badges/mypy.svg)

This is a toolbox of various functions that are useful for data science work. 

# Install

Include this package by adding to requirements.txt

```
git+https://github.com/earthastronaut/data_science_tools@master#egg=data_science_tools
```

# Contributing

Set up for development create a virtualenvironment and run `make requirements`
to install requirements and this package. 

The CI/CD runs `make lint` and `make test` to check the code and run unittests.
Please run these prior to making pull requests.

The version is stored in `data_science_tools/__init__.py` and should be updated 
for significant changes. There's a `make version_tag` which will `git tag` with
the version.

Optionally, if you use vscode you can copy the `.vscode/example_settings.json` to
`.vscode/settings.json` to use the magic linting tools. 
