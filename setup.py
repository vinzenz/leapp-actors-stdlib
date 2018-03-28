from setuptools import find_packages, setup

setup(
    name='leapp',
    packages=find_packages(),
    install_requires=['requests', 'six'],
    entry_points='''
        [console_scripts]
        snactor=leapp.snactor:main
        leapp=leapp.cli:main
    '''
)
