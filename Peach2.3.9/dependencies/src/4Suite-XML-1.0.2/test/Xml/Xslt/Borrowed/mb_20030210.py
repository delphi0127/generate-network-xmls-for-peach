from Xml.Xslt import test_harness

source_1 = """<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <title>Test</title>
  </head>
  <body>
    <h1>Test</h1>
    <p>XML Line 1<br/>XML Line 2<br xmlns=""/>XML Line 3 after HTML br</p>
    <script language="JavaScript">
        /*
            1 &amp; 2 are &lt; 3 but > 0
        */
</script>
    <p xmlns="">HTML line 1<br/>HTML line 2<script language="JavaScript">
        /*
            1 &amp; 2 are &lt; 3 but > 0
        */
</script></p>
  </body>
</html>"""

sheet_1 = """<xsl:transform
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="html" indent="no"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="@*|node()">
      <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
      </xsl:copy>
    </xsl:template>

</xsl:transform>"""

sheet_2 = """<xsl:transform
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="html" indent="yes"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="@*|node()">
      <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
      </xsl:copy>
    </xsl:template>

</xsl:transform>"""

# indent=no
expected_1 = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"><head><title>Test</title></head><body><h1>Test</h1><p>XML Line 1<br/>XML Line 2<br xmlns="">XML Line 3 after HTML br</p><script language="JavaScript">
        /*
            1 &amp; 2 are &lt; 3 but &gt; 0
        */
</script><p xmlns="">HTML line 1<br>HTML line 2<script language="JavaScript">
        /*
            1 & 2 are < 3 but > 0
        */
</script></p></body></html>"""


# indent=yes
expected_2 = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <title>Test</title>
  </head>
  <body>
    <h1>Test</h1>
    <p>XML Line 1
      <br/>XML Line 2
      <br xmlns="">XML Line 3 after HTML br
    </p>
    <script language="JavaScript">
        /*
            1 &amp; 2 are &lt; 3 but &gt; 0
        */
</script>
    <p xmlns="">HTML line 1
      <br>HTML line 2<script language="JavaScript">
        /*
            1 & 2 are < 3 but > 0
        */
</script></p>
  </body>
</html>"""

source_3 = """<?xml version="1.0"?><dummy/>"""

sheet_3 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" indent="yes"/>

  <xsl:template match="/">
    <html>
      <body>
        <h1>indented html</h1>
        <p>html indented 1&#10;html indented 2&#10;html indented 3</p>
        <div class="screen">
          <pre>html not indented 1&#10;html not indented 2<span xmlns="http://foo/bar"><i><b>xml span, i, b, this text, br, p.i., not indented</b></i><br/><xsl:processing-instruction name="foo">bar</xsl:processing-instruction></span><p>still xml, no indenting here either</p>
            <span xmlns="">html not indented 3<br/><p>html still not indented</p>&#10;html on new line but still not indented</span>
          </pre>
          <p>html indented<span xmlns="http://foo/bar"><i><b>xml indented<pre xmlns="">html not indented 1&#10;and 2</pre> back to xml indented</b></i></span>html indented again&#10;and again</p>
        </div>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>"""

expected_3 = """<html>
  <body>
    <h1>indented html</h1>
    <p>html indented 1
html indented 2
html indented 3</p>
    <div class="screen">
      <pre>html not indented 1
html not indented 2<span xmlns="http://foo/bar"><i><b>xml span, i, b, this text, br, p.i., not indented</b></i><br/><?foo bar?></span><p>still xml, no indenting here either</p><span>html not indented 3<br><p>html still not indented</p>
html on new line but still not indented</span></pre>
      <p>html indented
        <span xmlns="http://foo/bar">
          <i>
            <b>xml indented<pre xmlns="">html not indented 1
and 2</pre> back to xml indented</b>
          </i>
        </span>html indented again
and again
      </p>
    </div>
  </body>
</html>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
        title="mixed XML and HTML in HTML output; indent=no")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
        title="mixed XML and HTML in HTML output; indent=yes")

    source = test_harness.FileInfo(string=source_3)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
        title="deeply mixed XML and HTML in HTML output; indent=yes")

    return
