from setuptools import setup, find_packages


def get_description():
    with open("README.md", "r") as file:
        desc = file.read()
    return desc


def get_packages():
    data = []
    with open("requirements.txt", "r") as file:
        for package in file.readlines():
            data.append(package.strip())
    return data


long_description = get_description()

setup(
    name="TypeTest",
    version="0.2",
    description="Typing application",
    keywords="typing test speed fast",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    entry_points={
        'console_scripts': [
            'typetest-cli = cli.cli:start',
        ]
    },
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=get_packages(),
    url="https://github.com/filipnovacki/typetest",

)
