# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mysolatcli',
    version='1.0.0',

    description='CLI for Malaysia Solat Time',
    long_description=long_description,

    url='https://github.com/zeroryuki/mysolatcli',

    author='Zero Ryuki',
    author_email='zeroryuki@gmail.com',

    license='ISC',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3.8',
    ],

    entry_points = {
        'console_scripts': ['mysolatcli=mysolatcli.__main__:main']
    },

    keywords='solatcli',

    packages=find_packages(),

    install_requires=['requests', 'argparse', 'tabulate', 'pyjq'],
)
