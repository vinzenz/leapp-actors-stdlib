from setuptools import find_packages, setup

setup(
    name='leapp-actor-standard-library',
    packages=find_packages(),
    install_requires=['click', 'marshmallow', 'requests'],
    entry_points='''
        [console_scripts]
        snactor=leapp.tool:main
    '''
)
