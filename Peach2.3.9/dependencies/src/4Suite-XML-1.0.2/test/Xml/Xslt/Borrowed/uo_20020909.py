"""
Behavior of node copy to result tree
"""

from Xml.Xslt import test_harness


SOURCE_1="""<?xml version="1.0" encoding="utf-8"?>
<doc xmlns="urn:bogus-1">
  <elem/>
</doc>"""



SHEET_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:transform
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:b1="urn:bogus-1"
>

  <xsl:output method="xml" encoding="iso-8859-1" indent="yes"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
    doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"/>

  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
      <xsl:apply-templates/>
    </html>
  </xsl:template>

  <xsl:template match="b1:elem">
    <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
      <rdf:Description ID="spam"/>
    </rdf:RDF>
  </xsl:template>

</xsl:transform>
"""

expected = """<?xml version='1.0' encoding='iso-8859-1'?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns='http://www.w3.org/1999/xhtml' xmlns:b1='urn:bogus-1' lang='en-US' xml:lang='en-US'>
  <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
    <rdf:Description ID='spam'/>
  </rdf:RDF>
</html>
"""

def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title="Namespace nodes copied out at different levels")
    return

