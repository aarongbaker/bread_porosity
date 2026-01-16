"""
Setup configuration for Bread Porosity Analysis Tool.
Enables installation via: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [line.strip() for line in requirements_path.read_text().split('\n') 
                   if line.strip() and not line.startswith('#')]

setup(
    name="bread-porosity-analyzer",
    version="1.0.0",
    author="Bread Analysis Team",
    description="Standardized bread porosity measurement using transmitted light and image processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/bread-porosity",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bread-porosity=analyze:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    keywords="bread porosity image-analysis computer-vision food-science",
    project_urls={
        "Documentation": "https://github.com/your-username/bread-porosity/blob/main/README.md",
        "Source": "https://github.com/your-username/bread-porosity",
        "Issues": "https://github.com/your-username/bread-porosity/issues",
    },
)
