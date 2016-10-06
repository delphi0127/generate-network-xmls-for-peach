<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:variable name='spam' select='"imported"'/>

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

  <xsl:template match="ADDRBOOK">
    <xsl:text>ADDRBOOK from imported: </xsl:text>
    <xsl:value-of select='$spam'/>
  </xsl:template>

  <xsl:template match="ENTRY">
    <xsl:text>ENTRY from imported: </xsl:text>
	<TR>
      <xsl:value-of select='@ID'/>
	  <xsl:apply-templates select='NAME | PHONENUM'/>
	</TR>
  </xsl:template>

  <xsl:template match="NAME">
    <xsl:text>NAME from imported: </xsl:text>
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
