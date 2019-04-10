from setuptools import setup

setup(name='ccmcmd',
    version='0.1.0',
    description='CCM Team helper commands',
    long_description='CCM Team helper commands for various internal services.',
    url='https://git.ccmteam.com/projects/SM/repos/ccmcmd',
    author='AJ',
    author_email='ajambu@collectivei.com',
    license='MIT',
    packages=['ccmcmd'],
    classifiers=[
        'Development Status :: 1 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Helper Commands :: Functions',
    ],
    keywords='ccm team helper icinga consul functions',
    install_requires=[
        'pyyaml',
        'requests',
        'texttable',
    ],
    scripts=['bin/ccmcmd'],
    zip_safe=False)
