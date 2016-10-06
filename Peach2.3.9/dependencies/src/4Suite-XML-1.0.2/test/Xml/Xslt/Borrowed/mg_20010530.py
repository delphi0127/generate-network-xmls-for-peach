# -*- coding: iso-8859-1 -*-
#Matt Gushee had problems with xml:lang

from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:param name="currentLanguage" select="'en'"/>

  <!-- Removed definition for charEncoding variable. -->

  <xsl:output method="html" encoding="utf-8"/>

  <xsl:template match="/">
  <!--
    <xsl:message><xsl:value-of select="$currentLanguage"/></xsl:message>
  -->
    <xsl:apply-templates select="*[lang($currentLanguage) or not(@xml:lang)]"/>
  </xsl:template>

  <xsl:template match="*">
  <!--
    <xsl:message>Processing: <xsl:value-of select="name()"/></xsl:message>
  -->
    <xsl:copy>
      <xsl:for-each select="@*[name() != 'id']">
	<xsl:copy/>
      </xsl:for-each>
      <xsl:apply-templates
	select="*[lang($currentLanguage) or not(@xml:lang)] | text()"/>
    </xsl:copy>
  </xsl:template>
    
</xsl:stylesheet>"""

source_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<!--
<!DOCTYPE html PUBLIC
  "-//W3C//DTD XHTML 1.1//EN"
  "/usr/local/share/xml/xhtml/xhtml11.dtd"
>
-->
<html xmlns="http://www.w3.org/1999/xhtml"
  version="-//W3C//DTD XHTML 1.1//EN"
  xml:lang="en">
  <head>
    <title>Welcome</title>
  </head>

  <body xml:lang="en">
    <h1 xml:lang="en">Welcome</h1>
    <h1 xml:lang="ja">ã‚ˆã†ã“ã</h1>
    <hr/>
    <p xml:lang="en">
The Kaiwa Club is an informal group for people who want to practice
Japanese conversation. We welcome members at all levels of
proficiency.
</p>
    <p xml:lang="ja">
ä¼šè©±å€¶æ¥½éƒ¨ã¯æ—¥æœ¬èªžã®ä¼šè©±ã‚’ç·´ç¿’ã—ãŸã„äººã®ãŸã‚ã®ã‚¤ãƒ³ãƒ•ã‚©ãƒ¼ãƒžãƒ«ãªã‚°ãƒ«ãƒ¼ãƒ—ã§
ã”ã–ã„ã¾ã™ã€‚ãƒ¬ãƒ™ãƒ«ã¯ã‹ã‹ã‚ã‚‰ãšã€æ–°ã—ã„ä¼šå“¡ã‚’å¤§æ­“è¿Žã—ã¦ãŠã‚Šã¾ã™ã€‚
</p>
  </body>
</html>
"""

# NOTE - we need to readd source_2 as a Base64 encoded block
# We cannot mix UTF-16 and UTF-8 in the same file
source_2 = """\
"""

source_3 = """\
<?xml version="1.0" encoding="UTF-8"?>
<!--
<!DOCTYPE html PUBLIC
  "-//W3C//DTD XHTML 1.1//EN"
  "/usr/local/share/xml/xhtml/xhtml11.dtd"
>
-->
<html xmlns="http://www.w3.org/1999/xhtml"
  version="-//W3C//DTD XHTML 1.1//EN"
  xml:lang="en">
  <head>
    <title>Welcome</title>
  </head>

  <body xml:lang="en">
    <h1 xml:lang="en">Welcome</h1>
    <h1 xml:lang="ja">¤è¤¦¤³¤½</h1>
    <hr />
    <p xml:lang="en">
The Kaiwa Club is an informal group for people who want to practice
Japanese conversation. We welcome members at all levels of
proficiency.
</p>
    <p xml:lang="ja">
²ñÏÃ¶æ³ÚÉô¤ÏÆüËÜ¸ì¤Î²ñÏÃ¤òÎý½¬¤·¤¿¤¤¿Í¤Î¤¿¤á¤Î¥¤¥ó¥Õ¥©¡¼¥Þ¥ë¤Ê¥°¥ë¡¼¥×¤Ç
¤´¤¶¤¤¤Þ¤¹¡£¥ì¥Ù¥ë¤Ï¤«¤«¤ï¤é¤º¡¢¿·¤·¤¤²ñ°÷¤òÂç´¿·Þ¤·¤Æ¤ª¤ê¤Þ¤¹¡£
</p>
  </body>
</html>
"""

#source_1 + sheet_1 with parameter currentLanguage=en
saxon_output_1 = """\
<html xmlns="http://www.w3.org/1999/xhtml" version="-//W3C//DTD XHTML 1.1//EN" xml:lang="en">
   
   <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
   
      
      <title>Welcome</title>
      
   </head>
   
   
   <body xml:lang="en">
      
      <h1 xml:lang="en">Welcome</h1>
      
      
      <hr>
      
      <p xml:lang="en">
         The Kaiwa Club is an informal group for people who want to practice
         Japanese conversation. We welcome members at all levels of
         proficiency.
         
      </p>
      
      
   </body>
   
</html>"""

#source_1 + sheet_1 with parameter currentLanguage=en
# output is xml-ish due to non-null namespace
expected_1 = """<html xmlns="http://www.w3.org/1999/xhtml" version="-//W3C//DTD XHTML 1.1//EN" xml:lang="en">\n  <head>\n    <title>Welcome</title>\n  </head>\n\n  <body xml:lang="en">\n    <h1 xml:lang="en">Welcome</h1>\n    \n    <hr/>\n    <p xml:lang="en">\nThe Kaiwa Club is an informal group for people who want to practice\nJapanese conversation. We welcome members at all levels of\nproficiency.\n</p>\n    \n  </body>\n</html>"""

#source_1 + sheet_1 with parameter currentLanguage=ja
expected_2 = ""

sheet_2 = """\
<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" encoding="utf-8"/>
	<xsl:param name="currentLanguage" select="'en'"/>
	<xsl:template match="/">
		<xsl:apply-templates
			select="*[lang($currentLanguage)
				or not(@xml:lang)]"/>
	</xsl:template>
	<xsl:template match="*">
		<xsl:copy>
			<xsl:for-each select="@*">
				<xsl:copy/>
			</xsl:for-each>
			<xsl:apply-templates
				select="*[lang($currentLanguage)
				or not(@xml:lang)] | text()"/>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="text()">
		<xsl:value-of select="."/>
	</xsl:template>
</xsl:stylesheet>
"""

source_4 = """\
<?xml version="1.0" encoding="utf-8"?>
<!--
<!DOCTYPE html PUBLIC
  "-//W3C//DTD XHTML 1.1//EN"
  "xhtml11.dtd"
>
-->
<html xmlns="http://www.w3.org/1999/xhtml" version="-//W3C//DTD XHTML
      1.1//EN">
  <head>
    <title>Welcome</title>
  </head>

  <body>
    <h1 xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">Welcome</h1>
    <h1 xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">ã‚ˆã†ã“ã</h1>
    <hr xmlns="http://www.w3.org/1999/xhtml"/>
    <p xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
The Kaiwa Club is an informal group for people who want to practice
Japanese conversation. We welcome members at all levels of
proficiency.
</p>
    <p xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">
ä¼šè©±å€¶æ¥½éƒ¨ã¯æ—¥æœ¬èªžã®ä¼šè©±ã‚’ç·´ç¿’ã—ãŸã„äººã®ãŸã‚ã®ã‚¤ãƒ³ãƒ•ã‚©ãƒ¼ãƒžãƒ«ãªã‚°ãƒ«ãƒ¼ãƒ—ã§
ã”ã–ã„ã¾ã™ã€‚ãƒ¬ãƒ™ãƒ«ã¯ã‹ã‹ã‚ã‚‰ãšã€æ–°ã—ã„ä¼šå“¡ã‚’å¤§æ­“è¿Žã—ã¦ãŠã‚Šã¾ã™ã€‚
</p>
  </body>
</html>
"""

# NOTE - we need to readd source_5 as a Base64 encoded block
# We cannot mix UTF-16 and UTF-8 in the same file
source_5 = """\
"""


source_6 = """\
<?xml version="1.0" encoding="euc-jp"?>
<!--
<!DOCTYPE html PUBLIC
  "-//W3C//DTD XHTML 1.1//EN"
  "xhtml11.dtd"
>
-->
<html xmlns="http://www.w3.org/1999/xhtml" version="-//W3C//DTD XHTML
      1.1//EN">
  <head>
    <title>Welcome</title>
  </head>

  <body>
    <h1 xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">Welcome</h1>
    <h1 xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">¤è¤¦¤³¤½</h1>
    <hr xmlns="http://www.w3.org/1999/xhtml"/>
    <p xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
The Kaiwa Club is an informal group for people who want to practice
Japanese conversation. We welcome members at all levels of
proficiency.
</p>
    <p xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">
²ñÏÃ¶æ³ÚÉô¤ÏÆüËÜ¸ì¤Î²ñÏÃ¤òÎý½¬¤·¤¿¤¤¿Í¤Î¤¿¤á¤Î¥¤¥ó¥Õ¥©¡¼¥Þ¥ë¤Ê¥°¥ë¡¼¥×¤Ç
¤´¤¶¤¤¤Þ¤¹¡£¥ì¥Ù¥ë¤Ï¤«¤«¤ï¤é¤º¡¢¿·¤·¤¤²ñ°÷¤òÂç´¿·Þ¤·¤Æ¤ª¤ê¤Þ¤¹¡£
</p>
  </body>
</html>
"""

expected_3 = """\
"""

uche_sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:param name="currentLanguage" select="'en'"/>

  <xsl:output method="html" encoding="utf-8"/>

  <xsl:template match="*">
    <xsl:choose>
      <xsl:when test="@xml:lang">
        <!-- Don't shift context -->
        <xsl:apply-templates select="." mode="select-lang"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:for-each select="@*[name() != 'id']">
            <xsl:copy/>
          </xsl:for-each>
          <xsl:apply-templates/>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="*" mode="select-lang">
    <xsl:if test="lang($currentLanguage)">
      <xsl:copy>
        <xsl:for-each select="@*[name() != 'id']">
          <xsl:copy/>
        </xsl:for-each>
        <xsl:apply-templates mode="select-lang"/>
      </xsl:copy>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>"""

uche_source_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<!--
<!DOCTYPE html PUBLIC
  "-//W3C//DTD XHTML 1.1//EN"
  "/usr/local/share/xml/xhtml/xhtml11.dtd"
>
-->
<html xmlns="http://www.w3.org/1999/xhtml"
  version="-//W3C//DTD XHTML 1.1//EN"
>
  <head>
    <title xml:lang="en">Welcome</title>
  </head>

  <body>
    <h1 xml:lang="en">Welcome</h1>
    <h1 xml:lang="ja">ã‚ˆã†ã“ã</h1>
    <hr/>
    <p xml:lang="en">
The Kaiwa Club is an informal group for people who want to practice
Japanese conversation. We welcome members at all levels of
proficiency.
</p>
    <p xml:lang="ja">
ä¼šè©±å€¶æ¥½éƒ¨ã¯æ—¥æœ¬èªžã®ä¼šè©±ã‚’ç·´ç¿’ã—ãŸã„äººã®ãŸã‚ã®ã‚¤ãƒ³ãƒ•ã‚©ãƒ¼ãƒžãƒ«ãªã‚°ãƒ«ãƒ¼ãƒ—ã§
ã”ã–ã„ã¾ã™ã€‚ãƒ¬ãƒ™ãƒ«ã¯ã‹ã‹ã‚ã‚‰ãšã€æ–°ã—ã„ä¼šå“¡ã‚’å¤§æ­“è¿Žã—ã¦ãŠã‚Šã¾ã™ã€‚
</p>
  </body>
</html>
"""

# output is xml-ish because of non-null namespace
uche_expected_1 = """<html xmlns="http://www.w3.org/1999/xhtml" version="-//W3C//DTD XHTML 1.1//EN">\n  <head>\n    <title xml:lang="en">Welcome</title>\n  </head>\n\n  <body>\n    <h1 xml:lang="en">Welcome</h1>\n    \n    <hr/>\n    <p xml:lang="en">\nThe Kaiwa Club is an informal group for people who want to practice\nJapanese conversation. We welcome members at all levels of\nproficiency.\n</p>\n    \n  </body>\n</html>"""

uche_expected_2 = """\
<html version='-//W3C//DTD XHTML 1.1//EN'>
  <head>
  <body>
    <h1 xml:lang="ja">ã‚ˆã†ã“ã</h1>
    <hr>
    <p xml:lang="ja">
ä¼šè©±å€¶æ¥½éƒ¨ã¯æ—¥æœ¬èªžã®ä¼šè©±ã‚’ç·´ç¿’ã—ãŸã„äººã®ãŸã‚ã®ã‚¤ãƒ³ãƒ•ã‚©ãƒ¼ãƒžãƒ«ãªã‚°ãƒ«ãƒ¼ãƒ—ã§
ã”ã–ã„ã¾ã™ã€‚ãƒ¬ãƒ™ãƒ«ã¯ã‹ã‹ã‚ã‚‰ãšã€æ–°ã—ã„ä¼šå“¡ã‚’å¤§æ­“è¿Žã—ã¦ãŠã‚Šã¾ã™ã€‚
</p>
  </body>
</html>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          topLevelParams={'currentLanguage' : 'en'},
                          title='Selector sheet 1, source 1, lang=en')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          topLevelParams={'currentLanguage' : 'ja'},
                          title='Selector sheet 1, source 1, lang=ja')

    source = test_harness.FileInfo(string=uche_source_1)
    sheet = test_harness.FileInfo(string=uche_sheet_1)
    test_harness.XsltTest(tester, source, [sheet], uche_expected_1,
                          topLevelParams={'currentLanguage' : 'en'},
                          title="Uche's selector sheet 1, source 1, lang=en")

# Don't run until we can try on Matt's console to avoid terminal corruption
##    source = test_harness.FileInfo(string=uche_source_1)
##    sheet = test_harness.FileInfo(string=uche_sheet_1)
##    test_harness.XsltTest(tester, source, [sheet], uche_expected_2,
##                          topLevelParams={'currentLanguage' : 'ja'})
##                          title="Uche's selector sheet 1, source 1, lang=ja")
    return
