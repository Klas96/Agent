#!/usr/bin/env python3
"""
Setup script for PocketFlow.
"""

from setuptools import setup, find_packages

setup(
    name="pocketflow",
    version="0.1.0",
    description="A minimalist LLM framework for Agents, Task Decomposition, RAG, etc",
    author="PocketFlow Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "flask",
        "sqlalchemy",
        "pyyaml",
        "requests",
        "python-dotenv",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
) 