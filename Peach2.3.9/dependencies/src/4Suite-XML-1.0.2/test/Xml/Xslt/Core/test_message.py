from Xml.Xslt import test_harness

import cStringIO, sys

tests = []

# -- test one --------------------------------------------------------
title = "xsl:message in top-level variable"
sheet = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml"/>
  <xsl:variable name="foo">
    <bar>world</bar>
    <xsl:message terminate="no">Legal xsl:message in top-level variable template</xsl:message>
  </xsl:variable>
  <xsl:template match="/"><result>hello</result></xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version="1.0" encoding="UTF-8"?>
<result>hello</result>"""

messages = """\
STYLESHEET MESSAGE:
Legal xsl:message in top-level variable template
END STYLESHEET MESSAGE
"""
tests.append({'title' : title,
              'sheet' : sheet,
              'expected' : expected,
              'messages' : messages})

# -- test two --------------------------------------------------------
title = "xsl:message in regular template body"

sheet = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml"/>
  <xsl:template match="/">
    <result>hello</result>
    <xsl:message terminate="no">Legal xsl:message in regular template body</xsl:message>
  </xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version="1.0" encoding="UTF-8"?>
<result>hello</result>"""

messages = """\
STYLESHEET MESSAGE:
Legal xsl:message in regular template body
END STYLESHEET MESSAGE
"""

tests.append({'title' : title,
              'sheet' : sheet,
              'expected' : expected,
              'messages' : messages})

# -- test three ------------------------------------------------------
title = "xsl:message deep in stylesheet processing"

sheet = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
        <xsl:element name='TR'>
        <xsl:apply-templates select='NAME'/>
        </xsl:element>
  </xsl:template>

  <xsl:template match="NAME">
    <xsl:element name='TD'>
    <xsl:attribute name='ALIGN'>CENTER</xsl:attribute>
      <xsl:message>We're in the thick of processing NAME elements</xsl:message>
      <B><xsl:apply-templates/></B>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
"""

expected = """<HTML>
  <HEAD>
    <META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""

messages = """\
STYLESHEET MESSAGE:
We're in the thick of processing NAME elements
END STYLESHEET MESSAGE
STYLESHEET MESSAGE:
We're in the thick of processing NAME elements
END STYLESHEET MESSAGE
STYLESHEET MESSAGE:
We're in the thick of processing NAME elements
END STYLESHEET MESSAGE
"""

tests.append({'title' : title,
              'sheet' : sheet,
              'expected' : expected,
              'messages' : messages})

# -- test four --------------------------------------------------------
title = "message in XML form"
sheet = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml"/>
  <xsl:variable name="foo">
    <bar>world</bar>
    <xsl:message terminate="no"><msg>XML <code>xsl:message</code> in top-level variable template</msg></xsl:message>
  </xsl:variable>
  <xsl:template match="/"><result>hello</result></xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version="1.0" encoding="UTF-8"?>
<result>hello</result>"""

messages = """\
STYLESHEET MESSAGE:
<msg>XML <code>xsl:message</code> in top-level variable template</msg>
END STYLESHEET MESSAGE
"""
tests.append({'title' : title,
              'sheet' : sheet,
              'expected' : expected,
              'messages' : messages})

# -- test function ---------------------------------------------------

def Test(tester):

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")

    for testinfo in tests:
        tester.startGroup(testinfo['title'])
        sheet = test_harness.FileInfo(string=testinfo['sheet'])
        sys.stderr = output_stream = cStringIO.StringIO()
        try:
            test_harness.XsltTest(tester, source, [sheet], testinfo['expected'])
        finally:
            sys.stderr = sys.__stderr__
        tester.startTest('Verifying message output')
        tester.compare(testinfo['messages'], output_stream.getvalue())
        tester.testDone()
        tester.groupDone()

    return
