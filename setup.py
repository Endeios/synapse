from setuptools import setup, find_packages
setup(
    name = "pirate",
    version = "0.1",
    packages = find_packages(),
    install_requires = ['zmq>=0'],
    entry_points={
        'console_scripts': [
            'service = skullz.service:start',
            'client  = skullz.client:start',
            'server  = skullz.server:start',
        ],
#        'gui_scripts': [
#            'baz = my_package_gui:start_func',
#        ]
    }
)
