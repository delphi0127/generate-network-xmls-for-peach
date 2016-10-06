<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">

  <!-- URI of source doc (absolute, with scheme) -->
  <xsl:param name="src-uri" select="'file:///genid.xsl'"/>

  <!-- URI of stylesheet doc (absolute, with scheme) -->
  <xsl:param name="sty-uri" select="'file:///genid.xsl'"/>

  <xsl:variable name="src-scheme" select="substring-before($src-uri,':')"/>
  <xsl:variable name="sty-scheme" select="substring-before($sty-uri,':')"/>
  <xsl:variable name="src-file">
    <xsl:call-template name="get-tail">
      <xsl:with-param name="path" select="$src-uri"/>
    </xsl:call-template>
  </xsl:variable>
  <xsl:variable name="sty-file">
    <xsl:call-template name="get-tail">
      <xsl:with-param name="path" select="$sty-uri"/>
    </xsl:call-template>
  </xsl:variable>
  <xsl:variable name="src-authority" select="substring-before(substring-after($src-uri,'://'),'/')"/>
  <xsl:variable name="sty-authority" select="substring-before(substring-after($sty-uri,'://'),'/')"/>
  <xsl:variable name="src-path" select="substring-after($src-uri, concat($src-scheme,'://',$src-authority))"/>
  <xsl:variable name="sty-path" select="substring-after($sty-uri, concat($sty-scheme,'://',$sty-authority))"/>
  <xsl:variable name="src-base-path" select="substring($src-path, string-length($src-path) - string-length($src-file))"/>
  <xsl:variable name="sty-base-path" select="substring($sty-path, string-length($sty-path) - string-length($sty-file))"/>
  <xsl:variable name="src-relative-uri-ref" select="$src-file"/>
  <xsl:variable name="src-absolute-uri-ref" select="$src-uri"/>
  <xsl:variable name="src-localhost-uri-ref" select="concat('file://localhost',$src-path)"/>
  <xsl:variable name="sty-relative-uri-ref" select="$sty-file"/>
  <xsl:variable name="sty-absolute-uri-ref" select="$sty-uri"/>
  <xsl:variable name="sty-localhost-uri-ref" select="concat('file://localhost',$sty-path)"/>

  <xsl:variable name="src-is-sty" select="$src-uri = $sty-uri"/>
  <xsl:variable name="ok-to-test-src-localhost" select="$src-scheme='file' and $src-authority=''"/>
  <xsl:variable name="ok-to-test-sty-localhost" select="$sty-scheme='file' and $sty-authority=''"/>

  <xsl:output method="xml" encoding="us-ascii" indent="yes"/>

  <xsl:template match="/">

    <xsl:variable name="src-locpath-root" select="/"/>
    <xsl:variable name="src-thisdoc-root" select="document('',$src-locpath-root)"/>
    <xsl:variable name="src-relative-root" select="document($src-relative-uri-ref,$src-locpath-root)"/>
    <xsl:variable name="src-absolute-root" select="document($src-absolute-uri-ref)"/>
    <xsl:variable name="src-localhost-root" select="document($src-localhost-uri-ref)"/>

    <xsl:variable name="sty-thisdoc-root" select="document('')"/>
    <xsl:variable name="sty-relative-root" select="document($sty-relative-uri-ref)"/>
    <xsl:variable name="sty-absolute-root" select="document($sty-absolute-uri-ref)"/>
    <xsl:variable name="sty-localhost-root" select="document($sty-localhost-uri-ref)"/>

    <xsl:variable name="src-locpath-root-id" select="generate-id($src-locpath-root)"/>
    <xsl:variable name="src-thisdoc-root-id" select="generate-id($src-thisdoc-root)"/>
    <xsl:variable name="src-relative-root-id" select="generate-id($src-relative-root)"/>
    <xsl:variable name="src-absolute-root-id" select="generate-id($src-absolute-root)"/>
    <xsl:variable name="src-localhost-root-id" select="generate-id($src-localhost-root)"/>

    <xsl:variable name="sty-thisdoc-root-id" select="generate-id($sty-thisdoc-root)"/>
    <xsl:variable name="sty-relative-root-id" select="generate-id($sty-relative-root)"/>
    <xsl:variable name="sty-absolute-root-id" select="generate-id($sty-absolute-root)"/>
    <xsl:variable name="sty-localhost-root-id" select="generate-id($sty-localhost-root)"/>

    <results>
      <group>
        <title>source doc IDs</title>
        <test>ID of root node of source via XPath location path / is non-empty string</test>
        <result><xsl:value-of select="boolean($src-locpath-root-id)"/></result>
        <test>ID of root node of source via same-document URI reference relative to XPath location path / does not differ</test>
        <result><xsl:value-of select="$src-thisdoc-root-id=$src-locpath-root-id"/></result>
        <test>ID of root node of source via relative URI ref does not differ</test>
        <result><xsl:value-of select="$src-relative-root-id=$src-locpath-root-id"/></result>
        <test>ID of root node of source via absolute URI ref does not differ</test>
        <result><xsl:value-of select="$src-absolute-root-id=$src-locpath-root-id"/></result>
        <test>all of the above IDs are identical</test>
        <result><xsl:value-of select="$src-locpath-root-id=$src-thisdoc-root-id=$src-relative-root-id=$src-absolute-root-id"/></result>
        <xsl:if test="$ok-to-test-src-localhost">
          <test>ID of root node of source via file://localhost/ absolute URI ref does not differ</test>
          <result><xsl:value-of select="$src-locpath-root-id=$src-absolute-root-id"/></result>
        </xsl:if>
      </group>
      <group>
        <title>stylesheet IDs</title>
        <test>ID of root node of stylesheet via same-document URI reference is non-empty string</test>
        <result><xsl:value-of select="boolean($sty-thisdoc-root-id)"/></result>
        <xsl:choose>
          <xsl:when test="$src-is-sty">
            <test>above ID is same as ID of root node of source via XPath location path /</test>
            <result><xsl:value-of select="$sty-thisdoc-root-id=$src-locpath-root-id"/></result>
          </xsl:when>
          <xsl:otherwise>
            <test>above ID differs from ID of root node of source via XPath location path /</test>
            <result><xsl:value-of select="$sty-thisdoc-root-id!=$src-locpath-root-id"/></result>
          </xsl:otherwise>
        </xsl:choose>
        <test>ID of root node of stylesheet via relative URI ref does not differ</test>
        <result><xsl:value-of select="$sty-relative-root-id=$sty-thisdoc-root-id"/></result>
        <test>ID of root node of stylesheet via absolute URI ref does not differ</test>
        <result><xsl:value-of select="$sty-absolute-root-id=$sty-thisdoc-root-id"/></result>
        <test>all of the above IDs are identical</test>
        <result><xsl:value-of select="$sty-thisdoc-root-id=$sty-relative-root-id=$sty-absolute-root-id"/></result>
        <xsl:if test="$ok-to-test-sty-localhost">
          <test>ID of root node of stylesheet via file://localhost/ absolute URI ref does not differ</test>
          <result><xsl:value-of select="$sty-thisdoc-root-id=$sty-absolute-root-id"/></result>
        </xsl:if>
      </group>
      <group>
        <title>factors affecting results above</title>
        <test>generate-id() on empty node-set returns empty string</test>
        <result><xsl:value-of select="not(generate-id(/..))"/></result>
        <test>generate-id() on same node returns same results</test>
        <result><xsl:value-of select="$src-locpath-root-id=generate-id($src-locpath-root) and $sty-thisdoc-root-id=generate-id($sty-thisdoc-root)"/></result>
        <test>generate-id() on different nodes returns different results</test>
        <result><xsl:value-of select="$src-locpath-root-id!=generate-id($src-locpath-root/*)"/></result>
        <test>URIs given as src-uri and sty-uri are resolvable</test>
        <result><xsl:value-of select="$src-absolute-root and $sty-absolute-root"/></result>
        <test>given same URI reference, document() returns same node</test>
        <result><xsl:value-of select="$src-relative-root=document($src-relative-uri-ref,$src-locpath-root) and $src-absolute-root=document($src-absolute-uri-ref)"/></result>
        <test>given equivalent relative and absolute URI references, document() returns same node</test>
        <result><xsl:value-of select="$src-relative-root-id=$src-absolute-root-id"/></result>
        <test>URI given as src-uri parameter is recognized as URI of source doc fed to processor</test>
        <result><xsl:value-of select="$src-locpath-root-id=$src-absolute-root-id"/></result>
        <test>URI given as sty-uri parameter is recognized as URI of stylesheet fed to processor</test>
        <result><xsl:value-of select="$sty-thisdoc-root-id=$sty-absolute-root-id"/></result>
        <xsl:choose>
          <xsl:when test="$ok-to-test-src-localhost">
            <test>URI resolver treats file:/// and file://localhost/ same as per RFC 1738</test>
            <result><xsl:value-of select="$src-absolute-root-id=$src-localhost-root-id"/></result>
          </xsl:when>
          <xsl:when test="$ok-to-test-sty-localhost">
            <test>URI resolver treats file:/// and file://localhost/ same as per RFC 1738</test>
            <result><xsl:value-of select="$sty-absolute-root-id=$sty-localhost-root-id"/></result>
          </xsl:when>
        </xsl:choose>
      </group>
    </results>

  </xsl:template>

  <xsl:template name="get-tail">
    <xsl:param name="path"/>
    <xsl:choose>
      <xsl:when test="contains($path,'/')">
        <xsl:call-template name="get-tail">
          <xsl:with-param name="path" select="substring-after($path,'/')"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$path"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
