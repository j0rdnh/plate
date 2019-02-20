from setuptools import setup, find_packages
from os import path


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Plate',
    version='0.2.1',
    description='CLI tool to create and use templates',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jordan Hauser',
    author_email='jordan@jhauser.com',
    license='MIT',
    url='https://github.com/j0rdnh/plate',
    packages=find_packages(),
    package_data={
        '': ['*.md', '*.cfg']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'Click'
    ],
    entry_points={
        'console_scripts': [
            'plate=plate.plate:cli'
        ]
    }
)
