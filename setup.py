from setuptools import setup

setup(
    name='Plate',
    version='0.1.0',
    description='CLI templater',
    author='Jordan Hauser',
    license='MIT',
    py_modules=['plate'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        plate=plate:cli
    '''
)
