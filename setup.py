from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="instancehub",
    version="1.0.0",
    author="Krishna Mohan",
    author_email="krishna273422@gmail.com",
    description="A powerful CLI tool for managing cloud instances, monitoring systems, and handling services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krishna273422/instancehub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "instancehub=instancehub.cli:main",
            "ih=instancehub.cli:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "instancehub": ["config/*.yaml", "templates/*.txt"],
    },
)
