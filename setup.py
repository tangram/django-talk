import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-talk',
    version='0.9b',
    packages=['talk'],
    include_package_data=True,
    license='MIT License',
    description='A simple, smooth private messaging app for Django',
    long_description=README,
    url='https://github.com/tangram/django-talk',
    author='Eirik Krogstad',
    author_email='eirikkr@gmail.com',
    install_requires=[
        'django-autocomplete-light',
        'mistune',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Framework :: Django",
    ],
)
