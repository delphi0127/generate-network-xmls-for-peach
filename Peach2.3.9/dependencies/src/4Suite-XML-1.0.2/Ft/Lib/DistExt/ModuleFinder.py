########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/DistExt/ModuleFinder.py,v 1.1.2.1 2006/09/24 22:51:19 jkloth Exp $
"""
Utilities to help applications using modulefinder get all of the modules
and data files used throughout 4Suite.

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os
from distutils.util import convert_path, subst_vars

from Ft import GetConfigVar
from Ft.Lib import ImportUtil
from Ft.Lib.DistExt import Dist, Install, InstallConfig

def AddHiddenModules(finder):
    # save the original set of module found by modulefinder
    default_modules = finder.modules.copy()

    # add any modules that cannot be found directly by ModuleFinder
    have_imported = True
    while have_imported:
        have_imported = False
        for name in HIDDEN_IMPORTS:
            if name in finder.modules:
                for name in HIDDEN_IMPORTS[name]:
                    if name not in finder.modules:
                        finder.import_hook(name)
                        have_imported = True

    # ensure that all the encodings are found/loaded
    if 'encodings' in finder.modules:
        finder.import_hook('encodings', None, ['*'])

    # get the modules that are not found by the default search
    modules = []
    for name in finder.modules:
        if name not in default_modules:
            modules.append(name)
    return modules

def GetModuleIncludes(modules):
    use_resources = GetConfigVar('RESOURCEBUNDLE')
    source_vars = {}
    for config_name, var_name in InstallConfig.CONFIG_MAPPING.items():
        source_vars[var_name] = GetConfigVar(config_name.upper())
    target_vars = Install.GetBundleScheme()
    includes = []
    for module in DATA_FILES:
        if module in modules:
            for filespec in DATA_FILES[module]:
                source = subst_vars(convert_path(filespec), source_vars)
                if use_resources:
                    resource = ImportUtil.OsPathToResource(source)
                    source = ImportUtil.GetResourceFilename(module, resource)
                target = subst_vars(convert_path(filespec), target_vars)[1:]
                includes.append((source, target))
    return includes

# This mapping lists a C-extension module's imports.  Any updates to an
# extension module's imports should be reflected in this mapping as well.
# This mapping also is used for pure-Python modules that use __import__
# to dynamically load modules.
HIDDEN_IMPORTS = {
    # add those from Python itself
    '__main__' : ['warnings', 'codecs', 'zipimport', 'unicodedata'],
    'codecs' : ['encodings'],
    'cPickle' : ['copy_reg'],
    'datetime' : ['time'],
    'parser' : ['copy_reg'],
    'time' : ['_strptime'],
    'zipimport' : ['zlib'],

    'Ft.Lib.DistExt.Dist' : [ 'Ft.Lib.DistExt.' + name
                              for name in Dist.Dist.command_mapping.values()
                              if name is not None
                              ],
    'Ft.Ods.Parsers.OqlParserc' : ['re'],
    'Ft.Rdf.Parsers.Versa.VersaParserc' : ['cmd',
                                           'Ft.Rdf.Parsers.Versa.ResourceExpressions',
                                           'Ft.Rdf.Parsers.Versa.BooleanExpressions',
                                           'Ft.Rdf.Parsers.Versa.Traversal',
                                           'Ft.Rdf.Parsers.Versa.Literals',
                                           'Ft.Rdf.Parsers.Versa.DataTypes',
                                           'Ft.Rdf.Parsers.Versa.NamedExpressions',
                                           'Ft.Lib.boolean',
                                           ],
    'Ft.Xml.cDomlettec' : ['cStringIO',
                           'gc',
                           'xml.dom',
                           'Ft.Lib.Uri',
                           'Ft.Xml',
                           'Ft.Xml.cDomlette',
                           'Ft.Xml.XInclude',
                           'Ft.Xml.XPath.Util',
                           ],
    'Ft.Xml.Lib.cStringWriter' : ['cStringIO'],
    'Ft.Xml.XPath.XPathParserc' : ['cmd',
                                   'Ft.Xml.XPath.ParsedAbsoluteLocationPath',
                                   'Ft.Xml.XPath.ParsedRelativeLocationPath',
                                   'Ft.Xml.XPath.ParsedPredicateList',
                                   'Ft.Xml.XPath.ParsedStep',
                                   'Ft.Xml.XPath.ParsedAxisSpecifier',
                                   'Ft.Xml.XPath.ParsedNodeTest',
                                   'Ft.Xml.XPath.ParsedAbbreviatedAbsoluteLocationPath',
                                   'Ft.Xml.XPath.ParsedAbbreviatedRelativeLocationPath',
                                   'Ft.Xml.XPath.ParsedExpr',
                                   ],
    'Ft.Xml.XPath._conversions' : ['Ft.Lib.boolean',
                                   'Ft.Lib.number',
                                   ],
    'Ft.Xml.XPointer.XPointerParserc' : ['cmd',
                                         'Ft.Xml.XPointer.XPointer',
                                         ],
    'Ft.Xml.XPointer.XPtrExprParserc' : ['cmd',
                                         'Ft.Xml.XPath.ParsedAbsoluteLocationPath',
                                         'Ft.Xml.XPath.ParsedRelativeLocationPath',
                                         'Ft.Xml.XPath.ParsedPredicateList',
                                         'Ft.Xml.XPath.ParsedStep',
                                         'Ft.Xml.XPath.ParsedAxisSpecifier',
                                         'Ft.Xml.XPath.ParsedNodeTest',
                                         'Ft.Xml.XPath.ParsedAbbreviatedAbsoluteLocationPath',
                                         'Ft.Xml.XPath.ParsedAbbreviatedRelativeLocationPath',
                                         'Ft.Xml.XPath.ParsedExpr',
                                         ],
    'Ft.Xml.Xslt.AvtParserc' : ['cmd',
                                'Ft.Xml.XPath.ParsedAbsoluteLocationPath',
                                'Ft.Xml.XPath.ParsedRelativeLocationPath',
                                'Ft.Xml.XPath.ParsedPredicateList',
                                'Ft.Xml.XPath.ParsedStep',
                                'Ft.Xml.XPath.ParsedAxisSpecifier',
                                'Ft.Xml.XPath.ParsedNodeTest',
                                'Ft.Xml.XPath.ParsedAbbreviatedAbsoluteLocationPath',
                                'Ft.Xml.XPath.ParsedAbbreviatedRelativeLocationPath',
                                'Ft.Xml.XPath.ParsedExpr',
                                ],
    'Ft.Xml.Xslt.StylesheetHandler' : ['Ft.Xml.Xslt.ApplyTemplatesElement',
                                       'Ft.Xml.Xslt.ApplyImportsElement',
                                       'Ft.Xml.Xslt.AttributeElement',
                                       'Ft.Xml.Xslt.AttributeSetElement',
                                       'Ft.Xml.Xslt.CallTemplateElement',
                                       'Ft.Xml.Xslt.ChooseElement',
                                       'Ft.Xml.Xslt.CopyElement',
                                       'Ft.Xml.Xslt.CopyOfElement',
                                       'Ft.Xml.Xslt.CommentElement',
                                       'Ft.Xml.Xslt.ElementElement',
                                       'Ft.Xml.Xslt.ForEachElement',
                                       'Ft.Xml.Xslt.IfElement',
                                       'Ft.Xml.Xslt.MessageElement',
                                       'Ft.Xml.Xslt.NumberElement',
                                       'Ft.Xml.Xslt.ParamElement',
                                       'Ft.Xml.Xslt.ProcessingInstructionElement',
                                       'Ft.Xml.Xslt.SortElement',
                                       'Ft.Xml.Xslt.Stylesheet',
                                       'Ft.Xml.Xslt.TemplateElement',
                                       'Ft.Xml.Xslt.TextElement',
                                       'Ft.Xml.Xslt.VariableElement',
                                       'Ft.Xml.Xslt.ValueOfElement',
                                       'Ft.Xml.Xslt.WithParamElement',
                                       'Ft.Xml.Xslt.OtherXslElement',
                                       'Ft.Xml.Xslt.WhitespaceElements',
                                       ],
    'Ft.Xml.Xslt.XPatternParserc' : ['cmd',
                                     'Ft.Xml.XPath.ParsedAbsoluteLocationPath',
                                     'Ft.Xml.XPath.ParsedRelativeLocationPath',
                                     'Ft.Xml.XPath.ParsedPredicateList',
                                     'Ft.Xml.XPath.ParsedStep',
                                     'Ft.Xml.XPath.ParsedAxisSpecifier',
                                     'Ft.Xml.XPath.ParsedNodeTest',
                                     'Ft.Xml.XPath.ParsedAbbreviatedAbsoluteLocationPath',
                                     'Ft.Xml.XPath.ParsedAbbreviatedRelativeLocationPath',
                                     'Ft.Xml.XPath.ParsedExpr',
                                     'Ft.Xml.Xslt.XPatterns',
                                     ],
    'Ft.Xml.ThirdParty.Xvif.iframe' : [#'Ft.Xml.ThirdParty.Xvif.iFrameXPath',
                                       #'Ft.Xml.ThirdParty.Xvif.iFrameRegExp',
                                       'Ft.Xml.ThirdParty.Xvif.iFrameRNG',
                                       'Ft.Xml.ThirdParty.Xvif.iFrameXSLT',
                                       'Ft.Xml.ThirdParty.Xvif.iFrameTypes',
                                       'Ft.Xml.ThirdParty.Xvif.iFrameRegFrag',
                                       ],
    'Ft.Xml.ThirdParty.Xvif.rng' : ['Ft.Xml.ThirdParty.Xvif.rngCoreTypeLib',
                                    'Ft.Xml.ThirdParty.Xvif.wxsTypeLib',
                                    ],
    }

DATA_FILES = {
    'Ft.Lib.DistExt.BuildDocs' : ['$data/Data/Stylesheets/docbook_html.xslt',
                                  '$data/Data/Stylesheets/docbook_html.css',
                                  '$data/Data/Stylesheets/sdocbook_html.xslt',
                                  '$data/Data/Stylesheets/sdocbook_html.css',
                                  '$data/Data/Stylesheets/modules_html.xslt',
                                  '$data/Data/Stylesheets/modules.css',
                                  '$data/Data/Stylesheets/extensions_html.xslt',
                                  '$data/Data/Stylesheets/extensions.xslt',
                                  '$data/Data/Stylesheets/commandline_html.xslt',
                                  '$data/Data/Stylesheets/commandline.xslt',
                                  ],
    'Ft.Lib.DistExt.BuildScripts' : ['$lib/Ft/Lib/DistExt/stubmain.exe',
                                     ],
    'Ft.Xml.Catalog' : ['$data/default.cat',
                        '$data/Schemata/catalog.dtd',
                        '$data/Schemata/sdocbook.dtd',
                        '$data/Schemata/xbel-1.0.dtd',
                        '$data/Schemata/xhtml1-strict.dtd',
                        '$data/Schemata/xhtml1-transitional.dtd',
                        '$data/Schemata/xhtml-lat1.ent',
                        '$data/Schemata/xhtml-special.ent',
                        '$data/Schemata/xhtml-symbol.ent',
                        '$data/Schemata/xsa.dtd',
                        ],
    }
