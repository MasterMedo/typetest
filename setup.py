from setuptools import setup, find_packages


def get_packages():
    data = []
    with open("requirements.txt", "r") as file:
        for package in file.readlines():
            data.append(package.strip())
    return data


setup(
    name="TypeTest",
    version="0.2",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'typetest-cli = cli.cli:start',
        ]
    },
    install_requires=get_packages(),
    url="https://github.com/filipnovacki/typetest",

)
