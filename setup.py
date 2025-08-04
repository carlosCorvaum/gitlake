from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = {}
with open("gitlake/__version__.py") as fp:
    exec(fp.read(), version)

setup(
    name="gitlake",
    version=version['__version__'],
    author="Carlos Corvaum",
    author_email="carloscorvaum@icloud.com",
    description="Framework para usar repositorios git como data-lake",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carloscorvaum/gitlake",
    package_dir={"": "gitlake"},
    packages=find_packages(where="gitlake"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.30.0",
        "pandas>=2.0.0",
        "pyarrow>=21.0.0",
    ],
    include_package_data=True,
)
