from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('VERSION') as f:
    version = f.read().strip()

setup(
    name='merc',
    version=version,
    description='analyze JSON from a parsed Rocket League replay',
    long_description=readme,
    author='Rusty Fausak',
    author_email='rustyfausak@gmail.com',
    url='https://github.com/rustyfausak/merc',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
