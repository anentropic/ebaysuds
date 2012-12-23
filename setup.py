from distutils.core import setup

setup(
    name='EbaySuds',
    version='0.3.2',
    packages=['ebaysuds',],
    license='LGPL v3',
    long_description=open('pypi.rst').read(),
    author="Anentropic",
    author_email="ego@anentropic.com",
    url="https://github.com/anentropic/ebaysuds",
    install_requires=[
        "suds == 0.4",
    ],
)