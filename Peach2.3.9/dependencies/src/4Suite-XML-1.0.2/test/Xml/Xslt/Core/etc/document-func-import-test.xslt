<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:embedded="http://doesnt/matter">

 <xsl:output method="xml" encoding="utf-8"/>

 <xsl:variable name="node" select="document('')"/>

 <embedded:data>
    <a/>
    <b/>
 </embedded:data>

 <xsl:template match="a">
   <xsl:element name="A"/>
 </xsl:template>

 <xsl:template match="b">
   <xsl:element name="B"/>
 </xsl:template>

 <xsl:template match="/">
   <xsl:element name="C"/>
 </xsl:template>

</xsl:stylesheet>
