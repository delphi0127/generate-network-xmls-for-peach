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

  <xsl:import href='agreement.common.xslt'/>
  <xsl:import href='html.fo.xslt'/>
  <xsl:import href='docbook.fo.xslt'/>

  <xsl:template match="/">
<fo:root>
  <fo:layout-master-set>
    <fo:simple-page-master  master-name="US-Letter"
      page-height="11in"   page-width="8.5in"
      margin-top="0.5in"   margin-bottom="0.5in"
      margin-left="0.5in"  margin-right="0.5in">
      <fo:region-body/>
    </fo:simple-page-master>
    <fo:simple-page-master  master-name="first"
      page-height="11in"   page-width="8.5in"
      margin-top="0.5in"   margin-bottom="0.5in"
      margin-left="0.5in"  margin-right="0.5in">
      <fo:region-body margin-top='0.5in' margin-bottom='0.5in'/>
      <fo:region-after extent='0.25in'/>
    </fo:simple-page-master>
    <fo:simple-page-master  master-name="main"
      page-height="11in"   page-width="8.5in"
      margin-top="0.5in"   margin-bottom="0.5in"
      margin-left="0.5in"  margin-right="0.5in">
      <fo:region-before extent='1in'/>
      <fo:region-body margin-top='0.5in' margin-bottom='0.5in'/>
      <fo:region-after extent='0.25in'/>
    </fo:simple-page-master>
 
    <fo:page-sequence-master master-name='contents'>
      <fo:repeatable-page-master-alternatives>
        <fo:conditional-page-master-reference
          master-reference='first'
          page-position='first'/>
        <fo:conditional-page-master-reference
          master-reference='main'
          page-position='rest' />
      </fo:repeatable-page-master-alternatives>
    </fo:page-sequence-master>
  </fo:layout-master-set>

  <fo:page-sequence master-reference='contents'>
 
    <fo:flow flow-name="xsl-region-body">
      <xsl:apply-templates/>              

      <fo:block space-before="20pt">
        The signatures of the authorized representatives of  <xsl:value-of select="$provider-abbrev"/> and <xsl:value-of select="$header/c:Client/@name"/> shall constitute acceptance
of this Statement of Work as set forth above.
      </fo:block>
      <fo:block space-before="20pt">
        <xsl:text>______________________________________________________________________</xsl:text>
      </fo:block>
      <fo:table>
        <fo:table-column column-width='300pt'/>
        <fo:table-column column-width='100pt'/>
        <fo:table-body>
          <fo:table-row>
            <fo:table-cell>
              <fo:block text-align="start">
                <xsl:value-of select="$header/c:Contractor/c:Contact[@desc='Primary']/c:Name"/>
              </fo:block>
            </fo:table-cell>
            <fo:table-cell text-align="end">
              <fo:block>
                <xsl:text>Date</xsl:text>
              </fo:block>
            </fo:table-cell>
          </fo:table-row>
        </fo:table-body>
      </fo:table>
      <fo:block><xsl:value-of select="$header/c:Contractor/c:Contact[@desc='Primary']/c:Title"/>
      </fo:block>
      <fo:block><xsl:value-of select="$provider-name"/></fo:block>
      <fo:block space-before="20pt">
        <xsl:text>______________________________________________________________________</xsl:text>
      </fo:block>
      <fo:table>
        <fo:table-column column-width='300pt'/>
        <fo:table-column column-width='100pt'/>
        <fo:table-body>
          <fo:table-row>
            <fo:table-cell>
              <fo:block text-align="start">
                <xsl:value-of select="$header/c:Client/c:Contact[@desc='Primary']/c:Name"/>
              </fo:block>
            </fo:table-cell>
            <fo:table-cell text-align="end">
              <fo:block>
                <xsl:text>Date</xsl:text>
              </fo:block>
            </fo:table-cell>
          </fo:table-row>
        </fo:table-body>
      </fo:table>
      <fo:block><xsl:value-of select="$header/c:Client/c:Contact[@desc='Primary']/c:Title"/>
      </fo:block>
      <fo:block><xsl:value-of select="$header/c:Client/@name"/></fo:block>
    </fo:flow>

  </fo:page-sequence>
</fo:root>
  </xsl:template>

  <xsl:template match="c:Agreement">
    <fo:block font-size="20pt" font-family="sans-serif"
        font-weight="bold" space-before="6pt" space-after="20pt">
<xsl:value-of select="$title"/>
    </fo:block>

	<xsl:apply-templates select="c:*"/>

  </xsl:template>

  <xsl:template match="c:Clause">
    <xsl:choose>
      <xsl:when test="child::node()">
        <xsl:if test="not(@id='preamble')">
          <xsl:variable name='content'>
            <xsl:apply-templates select="exslt:node-set($output-set)/*" mode='print-position'>
              <xsl:with-param name='id-to-find' select='@id'/>
            </xsl:apply-templates>
            <xsl:value-of select="ft:title"/>
          </xsl:variable>
    <xsl:call-template name="H3">
      <xsl:with-param name="content"><xsl:copy-of select="$content"/></xsl:with-param>
    </xsl:call-template>
        </xsl:if>
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name='boilerplate' select='fte:key("phrases", concat("contractual.", @id), $phrase-doc)'/>
        <xsl:if test="not(@id='preamble')">
          <xsl:variable name='content'>
            <xsl:apply-templates select="exslt:node-set($output-set)/*" mode='print-position'>
              <xsl:with-param name='id-to-find' select='@id'/>
            </xsl:apply-templates>
            <xsl:value-of select="$boilerplate/ft:title"/>
          </xsl:variable>
    <xsl:call-template name="H3">
      <xsl:with-param name="content"><xsl:copy-of select="$content"/></xsl:with-param>
    </xsl:call-template>
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
