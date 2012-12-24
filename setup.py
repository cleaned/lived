#!/usr/bin/env python3
#
#

import os
import sys

if sys.version_info.major < 3: print("you need to run LIFE  with python3") ; os._exit(1)

try: use_setuptools()
except: pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    print("L I F E needs the distribute package to be installed, look in the bootstrap directory if it cannot be installed system-wide")
    os._exit(1)

import life

setup(
    name='life',
    version='%s' % life.__version__,
    url='https://github.com/feedbackflow/life',
    author='Bart Thate',
    author_email='feedbackflow@gmail.com',
    description='L I F E - life monitoring software',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    requires=['distribute', ],
    scripts=['bin/life',
            ],
    packages=['life',
              'life.plugs'],
    long_description = """ L I F E - keep track of what you are doing - https://github.com/feedbackflow/life """,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
