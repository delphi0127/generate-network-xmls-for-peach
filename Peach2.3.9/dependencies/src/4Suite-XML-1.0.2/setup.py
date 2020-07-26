#!/usr/bin/env python
########################################################################
# $Header: /var/local/cvsroot/4Suite/setup.py,v 1.40.2.5 2006/10/20 18:26:15 jkloth Exp $
"""
The main installation specification

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

# Create a dummy __config__ module to pass some setup-only values
# to the Ft module (and to allow for bypassing the check in Ft/__init__.py)
import os, sys, imp
if os.path.exists(os.path.join('Ft', '__init__.py')):
    config_module = 'Ft.__config__'
    module = sys.modules[config_module] = imp.new_module(config_module)
    module.NAME = '4Suite'
    module.VERSION = '1.0'
    module.DATADIR = os.path.abspath(os.path.join('Ft', 'Data'))
    # If we want localizations during setup, we need to set this to the
    # directory containing that message catalog hierarchy.
    module.LOCALEDIR = None


# Perform requested setup action(s)
import glob
from Ft.Lib.DistExt import setup

# The keywords given to setup() here are those that are in common between
# the various "packages" defined by the packages/*.pkg files
setup(
    # PackageManager specific
    package_files=glob.glob(os.path.join('packages', '*.pkg')),

    # 'PC' is only used for developing 4Suite
    validate_templates=['prune PC',
                        ],

    # Used by Windows binary installer (bdist_inno)
    license_file='COPYRIGHT',

    # Fields used in package metadata 1.0 (PEP 241 / Python 2.1+):
    name='4Suite',
    #version='1.0rc1',
    #description='An open-source platform for XML and RDF processing',
    #long_description=('4Suite is a Python-based toolkit for XML and RDF '
    #                  'application development. It features a library of '
    #                  'integrated tools for XML processing, implementing '
    #                  'open technologies such as DOM, RDF, XSLT, XInclude, '
    #                  'XPointer, XLink, XPath, XUpdate, RELAX NG, and '
    #                  'XML/SGML Catalogs. Layered upon this is an XML and '
    #                  'RDF data repository and server, which supports '
    #                  'multiple methods of data access, query, indexing, '
    #                  'transformation, rich linking, and rule processing, '
    #                  'and provides the data infrastructure of a full '
    #                  'database system, including transactions, '
    #                  'concurrency, access control, and management tools. '
    #                  'It also supports HTTP, SOAP, RPC, and FTP, plus '
    #                  'APIs in Python and XSLT.\n'
    #                  '\n'
    #                  "4Suite's license_ is based on the ASL_.\n"
    #                  '\n'
    #                  '.. _license: http://4suite.org/COPYRIGHT\n'
    #                  '.. _ASL: http://www.apache.org/licenses/LICENSE-1.1\n'
    #                  ),
    author='Fourthought, Inc.',
    maintainer='Fourthought, Inc.',
    author_email='4suite@4suite.org',
    maintainer_email='4suite@4suite.org',
    url='http://4suite.org/',
    copyright = 'Fourthought, Inc., 2006',

    options={'build_docs' : {'build_dir' : os.path.join('docs', 'xml'),
                             'inplace' : True,
                             },
             },

    keywords=['Python', '4Suite'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    requires_python=['>=2.2.1'],
    )
