from setuptools import setup, find_packages
import re
import os

base_path = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(base_path, 'README.md')).read()

# Get the version (borrowed from SQLAlchemy)
with open(os.path.join(base_path, "src", "hac", "__version__.py")) as fp:
    VERSION = (
        re.compile(r""".*__VERSION__ = ["'](.*?)['"]""", re.S).match(fp.read()).group(1)
    )

version = VERSION

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(
    name='hac',
    version=version,
    description="",
    long_description=README,
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[req for req in requirements if req[:2] != "# "],
    entry_points={
        'console_scripts':
            ['hac=hac:main']
    }
)
