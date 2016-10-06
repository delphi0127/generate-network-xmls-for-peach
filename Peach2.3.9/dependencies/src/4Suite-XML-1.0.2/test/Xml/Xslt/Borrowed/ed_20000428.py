#Erik Dasque's <edasque@silverstream.com> RDFtoRSS converter problem, 28 April 2000

from Xml.Xslt import test_harness

source_1 = """<?xml version="1.0" standalone="yes"?>
<rdf:RDF xmlns="http://my.netscape.com/rdf/simple/0.9/"
     xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
>
  <channel>
    <title>JavaWorld</title>
    <link>http://www.javaworld.com</link>
    <description>
      Add JavaWorld to your My Netscape page! The
      JavaWorld channel lets you stay on top of the latest
      developer tips, tutorials, news, and resources offered by
      JavaWorld.
    </description>
  </channel>
  <image>
    <title>JavaWorld Logo</title>
    <url>http://www.javaworld.com/icons/jw-mynetscape.gif</url>
    <link>http://www.javaworld.com</link>
  </image>
  <item>
    <title>&quot;Streaming JavaWorld&quot; -- the streaming audio news and talk for Java project managers</title>
    <link>http://www.javaworld.com/common/jw-streaming.html?myns</link>
  </item>
  <item>
    <title>Streaming JavaWord: An audio program for Java project managers and programmers</title>
    <link>http://www.javaworld.com/common/jw-streaming.html?myns</link>
  </item>
  <item>
    <title>Programming Java Devices: An Overview</title>
    <link>http://www.javaworld.com/jw-07-1999/jw-07-device.html?myns</link>
  </item>
  <textinput>
    <title>GO!</title>
    <description>Search JavaWorld</description>
    <name>col=jw&amp;qt</name>
    <link>http://search.javaworld.com/query.html</link>
  </textinput>
</rdf:RDF>"""

sheet_1 = """<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
  <xsl:copy>
    <rss>
      <xsl:apply-templates select="//channel"/>
    </rss>
  </xsl:copy>
</xsl:template>

<xsl:template match="channel">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
	<xsl:apply-templates select="//image"/>
	<xsl:apply-templates select="//item"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="channel/title">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="channel/link">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="channel/description">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="//image">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="image/title">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="image/url">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="image/link">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="item">
 <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="item/title">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="item/link">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>"""

sheet_2 = """<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:myns="http://my.netscape.com/rdf/simple/0.9/"
exclude-result-prefixes="myns"
>

<xsl:template match="/">
  <xsl:copy>
    <rss>
      <xsl:apply-templates select="//myns:channel"/>
    </rss>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:channel">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
    <xsl:apply-templates select="//myns:image"/>
    <xsl:apply-templates select="//myns:item"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:channel/myns:title">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:channel/myns:link">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:channel/myns:description">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="//myns:image">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:image/myns:title">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:image/myns:url">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:image/myns:link">
<xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:item">
 <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:item/myns:title">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="myns:item/myns:link">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>
"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<rss/>"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<rss><channel xmlns='http://my.netscape.com/rdf/simple/0.9/'>
    <title>JavaWorld</title>
    <link>http://www.javaworld.com</link>
    <description>
      Add JavaWorld to your My Netscape page! The
      JavaWorld channel lets you stay on top of the latest
      developer tips, tutorials, news, and resources offered by
      JavaWorld.
    </description>
  <image>
    <title>JavaWorld Logo</title>
    <url>http://www.javaworld.com/icons/jw-mynetscape.gif</url>
    <link>http://www.javaworld.com</link>
  </image><item>
    <title>"Streaming JavaWorld" -- the streaming audio news and talk for Java project managers</title>
    <link>http://www.javaworld.com/common/jw-streaming.html?myns</link>
  </item><item>
    <title>Streaming JavaWord: An audio program for Java project managers and programmers</title>
    <link>http://www.javaworld.com/common/jw-streaming.html?myns</link>
  </item><item>
    <title>Programming Java Devices: An Overview</title>
    <link>http://www.javaworld.com/jw-07-1999/jw-07-device.html?myns</link>
  </item></channel></rss>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='With default namespace')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='With named namespace')
    return
    
