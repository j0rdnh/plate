from setuptools import setup, find_packages

setup(
    name='Plate',
    version='0.1.0',
    description='CLI tool to create and use templates',
    author='Jordan Hauser',
    author_email='jordan@jhauser.com',
    url='',
    license='MIT',
    packages=find_packages(),
    package_data={
        '': ['*.md', '*.cfg']
    },
    install_requires=[
        'Click'
    ],
    entry_points='''
    [console_scripts]
    plate=plate.plate:cli
    '''
)
