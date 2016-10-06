<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
>

  <!-- Generate XHTML -->
  <xsl:output method="xml"/>

  <xsl:template match="/">
    <html>
    <head><title>Address Book</title>
    </head>
    <body>
    <h1><xsl:text>Tabulate Just Names and Phone Numbers</xsl:text></h1>
    <table><xsl:apply-templates/></table>
    </body>
    </html>
  </xsl:template>

  <xsl:template match="ENTRY">
    <tr>
      <xsl:apply-templates select='NAME'/>
      <td>
        <xsl:apply-templates select='PHONENUM'/>
      </td>
    </tr>
  </xsl:template>

  <xsl:template match="NAME">
    <td align="center">
      <b><xsl:apply-templates/></b>
    </td>
  </xsl:template>

  <xsl:template match="PHONENUM">
    <xsl:text>(</xsl:text>
    <xsl:value-of select="@DESC"/>
    <xsl:text>) </xsl:text>
    <xsl:apply-templates/>
    <xsl:if test="not(position()=last())">
      <br/>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
