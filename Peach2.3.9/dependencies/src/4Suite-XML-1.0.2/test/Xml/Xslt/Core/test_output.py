from Xml.Xslt import test_harness

specs = {'XML' : [], 'HTML' : [], 'Text' : []}

# XML Output [1] - defaults
sheet = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="xml" version="1.0"/>

  <xsl:template match="/">
    <docelem>
    <foo>
      <xsl:text>]]</xsl:text>
      <xsl:text>></xsl:text>
    </foo>
    <bar>
      <xsl:text>]</xsl:text>
      <xsl:text>></xsl:text>
    </bar>
    <foobar>
      <xsl:text>&lt;&amp;]]</xsl:text>
      <xsl:text>!</xsl:text>
    </foobar>
    </docelem>
  </xsl:template>

</xsl:stylesheet>"""

source = """<foo>dummy</foo>"""

expected = """<?xml version='1.0' encoding='UTF-8'?>
<docelem><foo>]]&gt;</foo><bar>]></bar><foobar>&lt;&amp;]]!</foobar></docelem>"""

specs['XML'].append((sheet, source, expected))

# XML Output [2] - standalone no
sheet = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="xml" version="1.0" standalone="no"/>
  <xsl:output doctype-system="Xml/Core/addr_book.dtd"/>

  <xsl:template match="/">
    <foo/>
  </xsl:template>

</xsl:stylesheet>"""

source = """<foo>dummy</foo>"""

expected = """<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<!DOCTYPE foo SYSTEM "Xml/Core/addr_book.dtd">
<foo/>"""

specs['XML'].append((sheet, source, expected))

# XML Output [3] - system doctype 
sheet = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="xml" version="1.0" standalone="no"
  doctype-system="Xml/Core/addr_book.dtd"/>

  <xsl:template match="/">
    <foo/>
  </xsl:template>

</xsl:stylesheet>"""

source = """<foo>dummy</foo>"""

expected = """<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<!DOCTYPE foo SYSTEM "Xml/Core/addr_book.dtd">
<foo/>"""

specs['XML'].append((sheet, source, expected))

# XML Output [4] - cdata elements
sheet = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:spam="http://spam.com"
  version="1.0"
>

  <xsl:output method="xml" cdata-section-elements="foo spam:bar"/>

  <xsl:template match='/'>
    <docelem>
    <foo>
      <![CDATA[<foo output>]]>
    </foo>
    <spam:bar>
      <![CDATA[<bar output>]]>
    </spam:bar>
    <bar>
      <![CDATA[<plain bar output>]]>
    </bar>
    <xsl:apply-templates/>
    </docelem>
  </xsl:template>

  <xsl:template match='@*|node()' priority='-1'>
    <xsl:copy>
      <xsl:apply-templates select='@*|node()'/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>"""

source = """<out xmlns:spam="http://spam.com"><foo><![CDATA[<source foo output>]]></foo><spam:bar><![CDATA[<source bar output>]]></spam:bar></out>"""

expected = """<?xml version='1.0' encoding='UTF-8'?>
<docelem xmlns:spam='http://spam.com'><foo><![CDATA[
      <foo output>
    ]]></foo><spam:bar><![CDATA[
      <bar output>
    ]]></spam:bar><bar>
      &lt;plain bar output>
    </bar><out><foo><![CDATA[<source foo output>]]></foo><spam:bar><![CDATA[<source bar output>]]></spam:bar></out></docelem>"""

specs['XML'].append((sheet, source, expected))


# HTML Output [1] - defaults
sheet = """<?xml version="1.0" encoding='iso-8859-1'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html"/>

  <xsl:template match="/">
    <html><body><p>spam &#150;&#160;&#255; eggs</p></body></html>
  </xsl:template>

</xsl:stylesheet>"""


source = """<foo>dummy</foo>"""

expected = """<html>
  <body>
    <p>spam \226&nbsp;&yuml; eggs</p>
  </body>
</html>"""

specs['HTML'].append((sheet, source, expected))

# HTML Output [2] - system doctype 
sheet = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html" doctype-system="Xml/Core/addr_book.dtd"/>

  <xsl:template match="/">
    <foo/>
  </xsl:template>

</xsl:stylesheet>"""

source = """<foo>dummy</foo>"""

expected = """<!DOCTYPE foo SYSTEM "Xml/Core/addr_book.dtd">
<foo></foo>"""

specs['HTML'].append((sheet, source, expected))

# HTML Output [3] - system and public doctype
sheet = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"
    doctype-system="Xml/Core/addr_book.dtd"
    doctype-public="public-id"/>

  <xsl:template match="/">
    <foo/>
  </xsl:template>

</xsl:stylesheet>"""

source = """<foo>dummy</foo>"""

expected = """<!DOCTYPE foo PUBLIC "public-id" "Xml/Core/addr_book.dtd">
<foo></foo>"""

specs['HTML'].append((sheet, source, expected))

# HTML Output [4] - bit 'o twist (US ASCII encoding)
sheet = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                >
<xsl:output method="html" encoding="us-ascii"/>

<xsl:template match="/">
<html>
  [&#160;]
</html>
</xsl:template >
</xsl:stylesheet>
"""

source = """<foo>dummy</foo>"""

expected = """<html>
  [&nbsp;]
</html>
"""
specs['HTML'].append((sheet, source, expected))

# HTML Output [5] - no version (default='4.0')
sheet = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                >
<xsl:output method="html"/>

<xsl:template match="/">
<html>
  [&#x391;]
</html>
</xsl:template >
</xsl:stylesheet>
"""

source = """<foo>dummy</foo>"""

expected = """<html>
  [&Alpha;]
</html>
"""
specs['HTML'].append((sheet, source, expected))

# HTML Output [6] - version='3.2'
sheet = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                >
<xsl:output method="html" version="3.2"/>

<xsl:template match="/">
<html>
  [&#x391;]
</html>
</xsl:template >
</xsl:stylesheet>
"""

source = """<foo>dummy</foo>"""

expected = """<html>
  [&#913;]
</html>
"""
specs['HTML'].append((sheet, source, expected))

# HTML Output [7] - version='4.0'
sheet = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                >
<xsl:output method="html" version="4.0"/>

<xsl:template match="/">
<html>
  [&#x391;]
</html>
</xsl:template >
</xsl:stylesheet>
"""

source = """<foo>dummy</foo>"""

expected = """<html>
  [&Alpha;]
</html>
"""
specs['HTML'].append((sheet, source, expected))

# HTML Output [8] - version='10.1'
sheet = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                >
<xsl:output method="html" version="10.1"/>

<xsl:template match="/">
<html>
  [&#x391;]
</html>
</xsl:template >
</xsl:stylesheet>
"""

source = """<foo>dummy</foo>"""

expected = """<html>
  [&Alpha;]
</html>
"""
specs['HTML'].append((sheet, source, expected))


# Text Output [1] - xsl:text stuff
sheet = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="text" encoding="iso-8859-1"/>

  <xsl:template match="/">
    <xsl:text/>a<xsl:text> </xsl:text>b<xsl:text>&#160;</xsl:text>c<xsl:text>&#10;</xsl:text>d<xsl:text/>
  </xsl:template>

</xsl:stylesheet>"""

source = """<foo>dummy</foo>"""

expected = "a b\240c\012d"

specs['Text'].append((sheet, source, expected))


def Test(tester):
    for (method, tests) in specs.items():
        test = 1
        for (sheet, source, expected) in tests:
            source = test_harness.FileInfo(string=source)
            sheet = test_harness.FileInfo(string=sheet)
            test_harness.XsltTest(tester, source, [sheet], expected,
                                  title="%s output method test %d" % (method, test))
            test = test + 1
    return
