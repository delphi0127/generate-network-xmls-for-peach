#Alexandre Fayolle's <alf@logilab.com> output bug with 4DOM + 4XSLT
from Xml.Xslt import test_harness


sheet_1 = """<?xml version="1.0"?>

<xsl:transform xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>
  <xsl:strip-space elements='*'/>

  <xsl:template match='rss'>
    <html-body>
      <h1>
        <xsl:apply-templates select="channel"/>
      </h1>
    </html-body>
  </xsl:template>

  <xsl:template match='channel'>
    <h2>
      <xsl:value-of select='./title'/>
    </h2>
    <table>
      <tr>
        <td>Description:</td>
        <td>
          <xsl:value-of select='./description'/>
        </td>
      </tr>
<tr>
<td>URL:</td>
<td>
<xsl:apply-templates mode='multilink' select='link'/>
</td>
</tr>
</table>
<xsl:apply-templates select='item'/>
</xsl:template>

<xsl:template match='item'>
<h3>
<xsl:apply-templates select='title'/>
</h3>
<table>
<xsl:apply-templates mode='first' select='description'/>
<xsl:apply-templates mode='first' select='link'/>
</table>
</xsl:template>
<xsl:template match='title'>
<xsl:value-of select='.'/>
</xsl:template>

<xsl:template match='link'>
<xsl:element name='a'>
<xsl:attribute name='href'>
<xsl:value-of select='.'/>
</xsl:attribute>
<xsl:value-of select='.'/>
</xsl:element>
</xsl:template>

<xsl:template mode='multi' match='*'>
<xsl:value-of select='.'/>
</xsl:template>

<xsl:template mode='first' match='description'>
<tr>
<td>
Description:
</td>
<td>
<xsl:apply-templates mode='multi'
select='../description'/>
</td>
</tr>
</xsl:template>
<xsl:template mode='multilink' match='*'>
<xsl:element name='a'>
<xsl:attribute name='href'>
<xsl:value-of select='.'/>
</xsl:attribute>
<xsl:value-of select='.'/>
</xsl:element>
</xsl:template>

<xsl:template mode='first' match='link'>
<tr>
<td>
More detail at:
</td>
<td>
<xsl:apply-templates mode='multilink' select='../link'/>
</td>
</tr>
</xsl:template>

</xsl:transform>
"""

# external DTD reference commented out by us;
# the DTD isn't used in this instance
source_1 = """<?xml version="1.0"?>
<!--DOCTYPE rss PUBLIC "-//Netscape Communications//DTD RSS 0.91//EN"
"http://my.netscape.com/publish/formats/rss-0.91.dtd"-->
<rss version="0.91">

<channel>
<title>freshmeat.net</title>
<link>http://freshmeat.net</link>
<description>the one-stop-shop for all your Linux software needs</description>
<language>en-us</language>

<item>
<title>Alzabo 0.06a</title>
<link>http://freshmeat.net/news/2000/07/19/964065475.html</link>
<description>Perl data modelling tool and RDBMS-OO mapper.</description>
</item>

<item>
<title>HLmaps 0.90</title>
<link>http://freshmeat.net/news/2000/07/19/964065450.html</link>
<description>A Perl/CGI script for Half-Life servers to present a list of loaded maps</description>
</item>

<textinput>
<title>quick finder</title>
<description>Use the text input below to search the freshmeat application database</description>
<name>query</name>
<link>http://core.freshmeat.net/search.php3</link>
</textinput>
</channel>
</rss>
"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<html-body><h1><h2>freshmeat.net</h2><table><tr><td>Description:</td><td>the one-stop-shop for all your Linux software needs</td></tr><tr><td>URL:</td><td><a href='http://freshmeat.net'>http://freshmeat.net</a></td></tr></table><h3>Alzabo 0.06a</h3><table><tr><td>
Description:
</td><td>Perl data modelling tool and RDBMS-OO mapper.</td></tr><tr><td>
More detail at:
</td><td><a href='http://freshmeat.net/news/2000/07/19/964065475.html'>http://freshmeat.net/news/2000/07/19/964065475.html</a></td></tr></table><h3>HLmaps 0.90</h3><table><tr><td>
Description:
</td><td>A Perl/CGI script for Half-Life servers to present a list of loaded maps</td></tr><tr><td>
More detail at:
</td><td><a href='http://freshmeat.net/news/2000/07/19/964065450.html'>http://freshmeat.net/news/2000/07/19/964065450.html</a></td></tr></table></h1></html-body>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='output bug')
    return
