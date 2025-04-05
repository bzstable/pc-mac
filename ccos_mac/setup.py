from setuptools import setup, find_packages

setup(
    name="ccos",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "httpx",
        "pydantic"
    ],
    entry_points={
        "console_scripts": [
            "ccos=claude_code.cli:app"
        ]
    }
) 