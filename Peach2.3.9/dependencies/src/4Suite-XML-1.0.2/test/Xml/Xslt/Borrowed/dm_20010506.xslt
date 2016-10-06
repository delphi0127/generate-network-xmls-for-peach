<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version='1.0'>
    
  <xsl:output method="html"/>
    
  <xsl:variable name="html.stylesheet"></xsl:variable>
  <xsl:variable name="html.stylesheet.type"></xsl:variable>
    
  <xsl:template match="/">
    <html>
    START
    <xsl:if test="$html.stylesheet">
      <link rel="stylesheet"
            href="{$html.stylesheet}"
            type="{$html.stylesheet.type}"/>
    </xsl:if>
    END
    </html>
  </xsl:template>

</xsl:stylesheet>
