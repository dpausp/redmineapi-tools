from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))


def find_version():
    with open(os.path.join(here, 'redmineapitools/VERSION')) as version_file:
        return version_file.read().strip()


setup(
    name="redmineapitools",
    version=find_version(),
    description="Some Python tools for working with the Redmine REST API using python-redmine",
    url='https://github.com/dpausp/redmineapi-tools',
    author='Tobias dpausp',
    author_email='dpausp@posteo.de',
    # Choose your license
    license='License :: OSI Approved :: BSD License',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='redmine api rest python-redmine',
    packages=["redmineapitools"],
    tests_require=["pytest-httpretty", "pytest"],
    install_requires=["python-redmine"],
    setup_requires=["setuptools-git"],
    include_package_data=True,
)
