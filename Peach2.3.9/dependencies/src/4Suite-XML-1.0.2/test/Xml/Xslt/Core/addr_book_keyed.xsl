<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <!-- Pretty much a silly bit of overkill for key usage, but executes the basic test -->

  <xsl:key name='name' match='ENTRY' use='NAME'/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
	<TR>
	<xsl:apply-templates select='NAME'/>
	</TR>
  </xsl:template>

  <xsl:template match="NAME">
    <TD ALIGN="CENTER">
      <B ID='{key("name", .)/EMAIL}'><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
