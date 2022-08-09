import re

from setuptools import setup, find_packages

with open('README.md') as fh:
    long_description = fh.read()

with open('./aio_mongo_dm/__init__.py') as f:
    version = (
        re.search(
            r"__version__ = '([^']+)",
            f.read()
        ).group(1)
    )


install_requires = [
    'motor >= 3.0'
]

setup(
    name='aio-mongo-dm',
    version=version,
    description='asynchronous lightweight ODM for MongoDB based on motor',
    keywords='asynchronous mongodb motor odm',
    url='http://github.com/kavinbj/aioMongoDM',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='kavinbj',
    author_email='kwfelix@163.com',
    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Framework :: AsyncIO',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries'
    ],
    packages=find_packages(exclude=["example", "tests"]),
    install_requires=install_requires,
    setup_requires=['pytest-asyncio', 'flake8'],
    tests_require=['pytest-asyncio'],
    package_data={},
    python_requires='>=3.7'
)
