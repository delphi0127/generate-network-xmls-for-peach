<?xml version="1.0"?>
<!DOCTYPE rdf:RDF [
    <!ENTITY rdf 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
    <!ENTITY dc 'http://purl.org/dc/elements/1.1/'>
    <!ENTITY xbel 'http://rdfinference.org/schemata/xbel/'>
]>

<!--

  XBEL to RDF converter
  See http://pyxml.sourceforge.net/topics/xbel/

-->

<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="&rdf;"
  xmlns:dc="&dc;"
  xmlns:xbel="&xbel;"
  version="1.0"
>

  <xsl:output indent="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates/>
    </rdf:RDF>
  </xsl:template>
 
  <xsl:template match="title"/>
  <xsl:template match="desc"/>
  <xsl:template match="info"/>

  <xsl:template name="node-common">
      <xsl:if test='@id'>
        <xsl:attribute name='rdf:ID' namespace='&rdf;'/>
      </xsl:if>
      <xsl:if test='title'>
        <dc:title><xsl:value-of select='title'/></dc:title>
      </xsl:if>
      <xsl:if test='desc'>
        <dc:description><xsl:value-of select='desc'/></dc:description>
      </xsl:if>
  </xsl:template>

  <xsl:template match="xbel">
    <xbel:collection>
      <xsl:call-template name="node-common"/>
      <xsl:apply-templates/>
    </xbel:collection>
  </xsl:template>

  <xsl:template match="folder">
    <xbel:contains rdf:parseType='Resource'>
<!--
      <xbel:index><xsl:number count='*'/></xbel:index>
-->
      <xbel:index><xsl:value-of select='position()'/></xbel:index>
      <xbel:item>
        <xbel:folder>
          <xsl:call-template name="node-common"/>
          <xsl:apply-templates/>
        </xbel:folder>
      </xbel:item>
    </xbel:contains>
  </xsl:template>

  <xsl:template match="bookmark">
    <xbel:contains rdf:parseType='Resource'>
      <xbel:index><xsl:number count='*'/></xbel:index>
      <xbel:item>
        <xbel:bookmark>
          <xsl:call-template name="node-common"/>
          <xbel:visited><xsl:value-of select='@visited'/></xbel:visited>
          <xbel:modified><xsl:value-of select='@modified'/></xbel:modified>
          <xbel:link><xsl:value-of select='@href'/></xbel:link>
        </xbel:bookmark>
      </xbel:item>
    </xbel:contains>
  </xsl:template>

</xsl:stylesheet>

