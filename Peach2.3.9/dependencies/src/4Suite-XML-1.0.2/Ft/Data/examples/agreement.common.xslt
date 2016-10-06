<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://namespaces.fourthought.com/common"
  xmlns:c="http://namespaces.fourthought.com/contractual"
  xmlns:fte="http://xmlns.4suite.org/ext"
  xmlns:exslt="http://exslt.org/common"
  xmlns:doc="http://docbook.org/docbook/xml/4.0/namespace"
  xmlns:fo="http://www.w3.org/1999/XSL/Format"
  version="1.0"
>

  <!--
  <xsl:param name='title' select='"Agreement For Consulting Services"'/>
  <xsl:param name='contractor' select='"Fourthought, Inc."'/>
  <xsl:param name='contractor-abbrev' select='"Fourthought"'/>
  <xsl:param name='contractor-addr' select='"4735 East Walnut Street, Boulder, Colorado 80301"'/>
  <xsl:variable name='phrase-doc' select='document("phrases.xml")'/>
  <xsl:variable name='header' select='/c:Agreement/c:Header'/>
-->


  <xsl:key name='phrases' match='ft:group/ft:phrase' use='concat(../@name, ".", @name)'/>

  <xsl:param name='title' select='"Agreement For Consulting Services"'/>

  <xsl:variable name='phrase-doc' select='document("phrases.xml")'/>
  <xsl:variable name='header' select='/c:Agreement/c:Header'/>

  <!-- used for numbering the clauses -->
  <xsl:variable name='output-set'>
    <xsl:for-each select="/c:Agreement/c:Clause[not(@id='preamble')]">
      <output-clause>
        <xsl:attribute name='id' namespace=''><xsl:value-of select="@id"/></xsl:attribute>
      </output-clause>
    </xsl:for-each>
  </xsl:variable>

  <xsl:param name='client-name' select='$header/c:Client/@name'/>

  <xsl:param name='provider-name' select='$header/c:Contractors/@name'/>

  <xsl:param name='client-abbrev' select='$header/c:Client/@abbrev'/>

  <xsl:param name='provider-abbrev' select='$header/c:Contractors/@abbrev'/>

  <xsl:template match="c:ClientName">
    <xsl:value-of select="$header/c:Client/@name"/>
  </xsl:template>

  <xsl:template match="c:ClientAbbrev">
    <xsl:value-of select="$header/c:Client/@abbrev"/>
  </xsl:template>

  <xsl:template match="c:ClientAddress">
    <xsl:value-of select="$header/c:Client/c:Address"/>
  </xsl:template>

  <xsl:template match="c:ClientEntity">
    <xsl:value-of select="$header/c:Client/c:Entity"/>
  </xsl:template>

  <xsl:template match="c:Contractor">
    <xsl:value-of select="$header/c:Contractor/@name"/>
  </xsl:template>

  <xsl:template match="c:ContractorAbbrev">
    <xsl:value-of select="$header/c:Contractor/@abbrev"/>
  </xsl:template>

  <xsl:template match="c:ContractorAddress">
    <xsl:value-of select="$header/c:Contractor/c:Address"/>
  </xsl:template>

  <xsl:template match="c:ContractorEntity">
    <xsl:value-of select="$header/c:Contractor/c:Entity"/>
  </xsl:template>

  <xsl:template match="c:AgreementDate">
    <xsl:value-of select="$header/@initDate"/>
  </xsl:template>

</xsl:stylesheet>
