from Ft.Xml.Xslt import Error

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:test="ex:test"
  xmlns="ex:test"
  exclude-result-prefixes="test"
  version="1.0"
>

  <xsl:import href="namespace-alias.xsl" />

  <xsl:template match="/">
    <testing/>
  </xsl:template>
</xsl:stylesheet>
"""

namespace_alias_xsl = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/XSL/TransformAlias"
  exclude-result-prefixes="xsl"
  version="1.0"
>

  <xsl:namespace-alias stylesheet-prefix="#default" result-prefix="xsl" />

</xsl:stylesheet>
"""

expected_1 = """<?xml version="1.0" encoding="UTF-8"?>
<testing xmlns="ex:test"/>
"""

def Test(tester):

    styfactory = test_harness.GetMappingFactory({
        'namespace-alias.xsl' : namespace_alias_xsl,
        })

    source = test_harness.FileInfo(string="<dummy/>")
    sty = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          title='circular xsl:import (direct)',
                          stylesheetInputFactory=styfactory)
    return
