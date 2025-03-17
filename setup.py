"""
Setup script para instalar a CLI CLLM.
"""
from setuptools import setup, find_packages
import os
import re

with open(os.path.join("cllm", "__init__.py"), "r") as f:
    version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", f.read())
    if version_match:
        version = version_match.group(1)
    else:
        version = "0.0.0"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="cllm",
    version=version,
    description="CLI to interact with LLM models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ivan Alvarenga",
    author_email="ivan.alvarenga@proto.me",
    url="https://github.com/ialvarenga/cllm",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cllm=cllm.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)