<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:doc="http://docbook.org/docbook/xml/4.0/namespace"
  xmlns:ft="http://xmlns.fourthought.com/common"
  xmlns:contact="http://xmlns.fourthought.com/contact"
  xmlns:vCard='http://4suite.org/nexus/rdfs/vcard#'
  xmlns:dc='http://purl.org/dc/elements/1.1/'
  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  xmlns:ftr='http://xmlns.fourthought.com/event.rdfs#'
  version="1.0"
>

  <xsl:import href='docbook_html1.xslt'/>

  <xsl:output method="html" encoding="ISO-8859-1"/>

  <xsl:param name="anonymous-id"/>
  <xsl:param name="anonymous-contact" select='"info@fourthought.com"'/>

  <xsl:variable name='heading-color' select='"#330066"'/>
  <xsl:variable name='bg-color' select='"#FFFFFF"'/>

  <xsl:key name="proj" match="ft:Project" use="@emp"/>

  <xsl:template match="ft:ProjectProfile"/>

  <xsl:template match="ft:Resume" mode="HEADING">
    <xsl:choose>
      <xsl:when test='$anonymous-id'>
      <title>
        <xsl:text>Anonymous resume.  Please contact </xsl:text>
        <xsl:value-of select='$anonymous-contact'/>
        <xsl:text> for more information.  The resume ID is </xsl:text>
        <xsl:value-of select='$anonymous-id'/>
        </title>
      </xsl:when>
      <xsl:otherwise>
      <title>
        <xsl:value-of select='contact:Contact/contact:Name'/>'s Curriculum Vita</title>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="ft:Resume">
    <!-- we expect to be adding bgcolor to BODY element -->
    <xsl:attribute name="bgcolor">
      <xsl:value-of select="$bg-color"/>
    </xsl:attribute>
    <DIV class="resumehead">
      <xsl:apply-templates select='contact:Contact'/>
      <HR WIDTH="100%"/>
    </DIV>
    <DIV class="resumebody">
      <xsl:if test='ft:Qualification'>
        <H2>Qualifications</H2>
        <UL>
          <xsl:apply-templates select='ft:Qualification'/>
        </UL>
      </xsl:if>
      <H2>Work Experience</H2>
      <xsl:apply-templates select='ft:Employment'/>
      <xsl:if test='ft:Industry'>
        <H2>Industrial experience</H2>
        <UL>
          <xsl:for-each select='ft:Industry'>
            <LI><xsl:apply-templates/></LI>
          </xsl:for-each>
        </UL>
      </xsl:if>
      <xsl:if test='rdf:RDF'>
        <H2>Publications and Presentations</H2>
        <xsl:apply-templates select='rdf:RDF'/>
      </xsl:if>
      <H2>Skills</H2>
      <xsl:apply-templates select='ft:Skills'/>
      <xsl:if test='ft:Affiliation'>
        <H2>Professional Affiliation</H2>
        <xsl:for-each select='ft:Affiliation'>
          <xsl:apply-templates/>
          <BR/>
        </xsl:for-each>
      </xsl:if>
      <xsl:if test='ft:Education'>
        <H2>Education</H2>
        <UL>
          <xsl:apply-templates select='ft:Education'/>
        </UL>
      </xsl:if>
    </DIV>
  </xsl:template>

  <xsl:template match="contact:Contact">
    <DIV class="contact" align="center">
      <xsl:choose>
      <xsl:when test='$anonymous-id'>
        <xsl:text>Anonymous resume.  Please contact </xsl:text>
        <xsl:value-of select='$anonymous-contact'/>
        <xsl:text> for more information.  The resume ID is </xsl:text>
        <xsl:value-of select='$anonymous-id'/>
      </xsl:when>
      <xsl:otherwise>
        <B>
          <xsl:value-of select='contact:Name'/>
        </B>
        <BR/>
        <A HREF='mailto:{contact:E-mail}'><xsl:value-of select='contact:E-mail'/></A>
        <PRE>
          <xsl:value-of select='contact:Address'/>
          <BR/>
          <xsl:value-of select='contact:Phone'/>
        </PRE>
        </xsl:otherwise>
      </xsl:choose>
    </DIV>
  </xsl:template>

  <xsl:template match="ft:Qualification">
    <LI class="qualification"><xsl:apply-templates/></LI>
  </xsl:template>

  <xsl:template match="ft:Employment">
    <DIV class="employment">
      <B>
        <xsl:choose>
          <xsl:when test='ft:Company/@href'>
            <A HREF='{ft:Company/@href}'><xsl:value-of select='ft:Company'/></A>
          </xsl:when>
          <xsl:otherwise><xsl:value-of select='ft:Company'/></xsl:otherwise>
        </xsl:choose>
      </B>
      <xsl:text>, </xsl:text>
      <xsl:value-of select='ft:Location'/>
      <BR/>
      <xsl:if test="ft:Title">
        <xsl:value-of select='ft:Title'/>
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:value-of select='ft:Period'/>
      <BR/>
      <BLOCKQUOTE class="role"><xsl:apply-templates select='ft:Role'/></BLOCKQUOTE>
      <xsl:if test='@id'>
        <P class="projectsdiv">
          <xsl:text>Projects included:</xsl:text>
        </P>
        <UL class="projects">
          <xsl:for-each select="key('proj', @id)">
            <LI><xsl:apply-templates/></LI>
          </xsl:for-each>
        </UL>
      </xsl:if>
    </DIV>
  </xsl:template>

  <xsl:template match="ftr:Publication">
    <DIV class="publication">
      <P>
        <SPAN class="pubtitle">
          <A HREF='{@about}'>
            <xsl:value-of select='dc:title'/>
          </A>
        </SPAN>
        <xsl:if test="dc:publisher">
          <xsl:text>, </xsl:text>
          <I><xsl:value-of select='dc:publisher/vCard:FN'/></I>
          <xsl:if test="dc:date">
            <xsl:text>, </xsl:text>
            <xsl:value-of select='dc:date'/>
          </xsl:if>
        </xsl:if>
      </P>
      <xsl:if test="dc:description">
        <BLOCKQUOTE class="pubdesc">
          <xsl:value-of select="dc:description"/>
        </BLOCKQUOTE>
      </xsl:if>
    </DIV>
  </xsl:template>

  <xsl:template match="ftr:Presentation">
    <DIV class="publication">
      <A HREF='{@about}'>
        <xsl:value-of select='dc:title'/>
      </A>
      <xsl:if test="dc:publisher">
        <xsl:text> (</xsl:text>
        <I><xsl:value-of select='dc:publisher/vCard:FN'/></I>
        <xsl:text>)</xsl:text>
      </xsl:if>
      <xsl:if test="dc:date">
        <xsl:text> </xsl:text>
        <xsl:value-of select='dc:date'/>
      </xsl:if>
      <BR/>
    </DIV>
  </xsl:template>

  <xsl:template match="ft:Education">
    <LI>
      <xsl:value-of select='ft:Date'/>
      <xsl:text>: </xsl:text>
      <xsl:if test="ft:Degree">
        <B>
          <xsl:value-of select='ft:Degree'/>
        </B>
        <xsl:text> -- </xsl:text>
      </xsl:if>
      <B>
        <xsl:value-of select='ft:Institution'/>
      </B>
      <xsl:text>, </xsl:text>
      <xsl:value-of select='ft:Location'/>
      <xsl:if test="ft:Notes">
        <BR/>
        <xsl:copy-of select='ft:Notes/*'/>
      </xsl:if>
    </LI>
  </xsl:template>

</xsl:stylesheet>
