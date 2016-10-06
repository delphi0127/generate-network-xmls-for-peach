<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://namespaces.fourthought.com/common"
  xmlns:c="http://namespaces.fourthought.com/contractual"
  xmlns:fte="http://xmlns.4suite.org/ext"
  xmlns:exslt="http://exslt.org/common"
  xmlns:doc="http://docbook.org/docbook/xml/4.0/namespace"
  version="1.0"
>

  <xsl:import href='agreement.common.xslt'/>
  <xsl:import href='docbook_html1.xslt'/>

  <xsl:output method="html" encoding="ISO-8859-1"/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE><xsl:value-of select="$title"/></TITLE>
    </HEAD>
    <BODY>
    <xsl:apply-templates/>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="c:Agreement">
	<H1><U><DIV ALIGN="CENTER"><xsl:value-of select="$title"/></DIV></U></H1>

	<xsl:apply-templates select="c:*"/>

	<P>
The signatures of the authorized representatives of <xsl:value-of select="$contractor"/> and
<xsl:value-of select="$header/c:Client/@name"/> shall constitute acceptance
of the terms and conditions contained in this Agreement as set forth above.
    </P>
<BR/>
<BR/>
<BR/>
<BR/>
______________________________________________________________________
<P><xsl:value-of select="$header/c:Consultants/c:Contact[@desc='Primary']/c:Name"/></P>
<P><xsl:value-of select="$header/c:Consultants/c:Contact[@desc='Primary']/c:Title"/></P>
<P><xsl:value-of select="$contractor"/></P>

<BR/>
<BR/>
______________________________________________________________________
<P><xsl:value-of select="$header/c:Client/c:Contact[@desc='Primary']/c:Name"/></P>
<P><xsl:value-of select="$header/c:Client/c:Contact[@desc='Primary']/c:Title"/></P>
<P><xsl:value-of select="$header/c:Client/@name"/> (<xsl:value-of select="$header/c:Client/@abbrev"/>)</P>
  </xsl:template>

  <xsl:template match="c:Clause">
    <xsl:choose>
      <xsl:when test="child::node()">
        <xsl:if test="not(@id='preamble')">
          <H3>
            <xsl:apply-templates select="exslt:node-set($output-set)/*" mode='print-position'>
              <xsl:with-param name='id-to-find' select='@id'/>
            </xsl:apply-templates>
            <xsl:value-of select="ft:title"/>
          </H3>
        </xsl:if>
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name='boilerplate' select='fte:key("phrases", concat("contractual.", @id), $phrase-doc)'/>
        <xsl:if test="not(@id='preamble')">
          <H3>
            <xsl:apply-templates select="exslt:node-set($output-set)/*" mode='print-position'>
              <xsl:with-param name='id-to-find' select='@id'/>
            </xsl:apply-templates>
            <xsl:value-of select="$boilerplate/ft:title"/>
          </H3>
        </xsl:if>
        <xsl:apply-templates select='$boilerplate'/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="c:Xref">
    <xsl:variable name='refend' select='fte:key("phrases", concat("contractual.", @id), $phrase-doc)'/>
    <xsl:if test='not($refend)'>
      <xsl:message>DANGLING CROSS-REFERENCE IN <xsl:value-of select="@id"/></xsl:message>
      <xsl:text>DANGLING CROSS-REFERENCE</xsl:text>
    </xsl:if>
    <xsl:text>"</xsl:text>
    <xsl:apply-templates select="exslt:node-set($output-set)/*" mode='print-position'>
      <xsl:with-param name='id-to-find' select='@id'/>
    </xsl:apply-templates>
    <xsl:value-of select="$refend/ft:title"/>
    <xsl:text>"</xsl:text>
  </xsl:template>

  <xsl:template match="*" mode="print-position">
    <xsl:param name='id-to-find' select='@id'/>
    <xsl:if test='@id=$id-to-find'>
      <xsl:value-of select="position()"/><xsl:text>. </xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="ft:title|c:Header" priority='-0.25'>
    <!-- do nothing -->
  </xsl:template>

</xsl:stylesheet>
