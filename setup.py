import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycomet",
    version="0.0.6",
    install_requires=[
        'Click',
        'pyyaml',
        'pystache',
        'jsonschema',
        'python-terraform'
    ],
    entry_points='''
        [console_scripts]
        comet=comet.comet:cli
    ''',
    author="Gabe Levasseur",
    author_email="gabriel.m.levasseur@gmail.com",
    description="A CLI tool to manage Terraform Components",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CodeSherpas/comet",
    packages=["comet"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
