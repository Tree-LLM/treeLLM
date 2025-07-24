# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="treellm",
    version="0.1.0",
    author="TreeLLM Team",
    author_email="team@treellm.com",
    description="AI Agent 기반 논문 분석 시스템",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/treellm/treellm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "dataclasses",
        "typing",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.9.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "web": ["streamlit>=1.28.0", "fastapi>=0.104.0", "uvicorn>=0.24.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "mypy>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "treellm=treellm_system:main",
        ],
    },
)
