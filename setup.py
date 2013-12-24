# -*- coding: utf-8 -*-
"""
Flask-SL
----------------

Impliments basic recognition of Second Life® based (LSL) requests.

"""
from setuptools import setup


setup(
    name='Flask-SL',
    version='0.0.3',
    url='https://github.com/nivardus/flask-sl',
    download_url = 'https://github.com/nivardus/flask-sl/archive/v0.0.3.tar.gz',
    license='MIT',
    author='Bennett Goble',
    author_email='nivardus@gmail.com',
    description='Basic recognition of Second Life® requests.',
    long_description=__doc__,
    py_modules=['flask_sl'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'netaddr'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Games/Entertainment :: Simulation'
    ]
)