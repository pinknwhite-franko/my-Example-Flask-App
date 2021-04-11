from setuptools import setup

setup(
    name='app',
    packages=['app'],
    debug=True,
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)