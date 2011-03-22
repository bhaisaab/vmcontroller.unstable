'''
VMController is a general purpose virtual machine controller written in Python.
vmcontroller.common is the common package between the vmcontroller.host and vmcontroller.guest package.
'''

try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

#from vmcontroller.common import __version__

name = 'vmcontroller.common'
version = '0.2.0'

setup(
    name=name,
    version=version,
    description='Virtual Machine Controller',
    long_description=__doc__,
    keywords='hypervisor virtual-machine controller',
    license='BSD',
    author='David Garcia Quintas, Rohit Yadav',
    author_email='dgquintas@gmail.com, rohityadav89@gmail.com',
    url='http://code.google.com/p/vmcontroller',
    packages=find_packages(exclude=['ez_setup', 'distribute_setup', 'tests', 'tests.*']),
    package_data={'vmcontroller': ['config/*.cfg*', 'tests/resources/*']},
    namespace_packages=['vmcontroller'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'distribute',
        'setuptools',
        'twisted',
        'stomper==0.2.2',
        'netifaces',
        'coilmq',
        'simplejson',
        'inject',
        'uuid'
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
