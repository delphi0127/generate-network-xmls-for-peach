<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  exclude-result-prefixes="f"
>

  <!-- max width to wrap to -->
  <xsl:param name="maxwidth" select="78"/>

  <!-- split lines at n characters without truncating words -->
  <!-- and preserve existing linefeeds -->
  <xsl:template name="wrap-multiline">
    <xsl:param name="text"/>
    <xsl:param name='width' select='$maxwidth'/>
    <xsl:choose>
      <xsl:when test="contains($text,'&#10;')">
        <xsl:call-template name="justify">
          <xsl:with-param name="width" select="$width"/>
          <xsl:with-param name="txt" select="substring-before($text,'&#10;')"/>
        </xsl:call-template>
        <xsl:text>&#10;</xsl:text>
        <xsl:call-template name="wrap-multiline">
          <xsl:with-param name="text" select="substring-after($text,'&#10;')"/>
          <xsl:with-param name='width' select='$width'/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$text">
        <xsl:call-template name="justify">
          <xsl:with-param name="width" select="$width"/>
          <xsl:with-param name="txt" select="$text"/>
        </xsl:call-template>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="justify">
    <xsl:param name="txt" />
    <xsl:param name="width" />
      <!-- Write a line out within the specified width.
           If the length of the line is less then the required width, just write it.
           If it is not.  split the line on white spaces.  Write out the text nodes until
           we get close to the width.  The add a line feed and recurse
           -->
      <xsl:choose>
        <xsl:when test='string-length($txt) &lt; $width'>
          <xsl:value-of select='$txt'/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name='write-chunk'>
            <xsl:with-param name='chunks'  select='f:split($txt," ")'/>
            <xsl:with-param name='current-chunk'  select='1'/>
            <xsl:with-param name='max-width' select='$width'/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
  </xsl:template>

  <xsl:template name='write-chunk'>
    <xsl:param name='chunks'/>
    <xsl:param name='current-chunk'/>
    <xsl:param name='max-width'/>
    <xsl:param name='written-width' select='0'/>
    <!--<xsl:message>
      Writing Chunks
      All Chunks:
      <xsl:for-each select='$chunks'>
        <xsl:value-of select='position()'/><xsl:text> = </xsl:text><xsl:value-of select='.'/>,
      </xsl:for-each>
      Current Chunk
      <xsl:value-of select='$current-chunk'/>
      Total Written:
      <xsl:value-of select='$written-width'/>
    </xsl:message>-->
    <xsl:choose>
      <xsl:when test='string-length($chunks[$current-chunk]) + $written-width &lt; $max-width + 10'>
        <xsl:value-of select='$chunks[$current-chunk]'/><xsl:text> </xsl:text>
        <!--<xsl:message>
          Writting:
          <xsl:value-of select='$chunks[$current-chunk]'/><xsl:text> </xsl:text>
          And calling next chunk
        </xsl:message>-->
        <xsl:if test='count($chunks) &gt; $current-chunk'>
          <xsl:call-template name='write-chunk'>
            <xsl:with-param name='current-chunk' select='$current-chunk + 1'/>
            <xsl:with-param name='chunks' select='$chunks'/>
            <xsl:with-param name='max-width' select='$max-width'/>
            <xsl:with-param name='written-width' select='$written-width + string-length($chunks[$current-chunk])'/>
          </xsl:call-template>
        </xsl:if>
      </xsl:when>
      <xsl:when test='$written-width &gt; ($max-width)-10'>
        <!-- WE got close enough -->
        <!--<xsl:message>
          Writting CR and starting over with current chunk:
        </xsl:message>-->
        <xsl:text>&#10;</xsl:text>
        <xsl:call-template name='write-chunk'>
          <xsl:with-param name='current-chunk' select='$current-chunk'/>
          <xsl:with-param name='chunks' select='$chunks'/>
          <xsl:with-param name='max-width' select='$max-width'/>
          <xsl:with-param name='written-width' select='0'/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:if test='$written-width != 0'>
          <!-- Something has already been written, LF and move on
               -->
          <xsl:text>&#10;</xsl:text>
        </xsl:if>
        <!--<xsl:message>
             Call unsplittable, and moving on to next chunk
           </xsl:message>-->
        <xsl:call-template name='write-unsplittable-chunk'>
          <xsl:with-param name='text'  select='$chunks[$current-chunk]'/>
          <xsl:with-param name='max-width' select='$width'/>
        </xsl:call-template>
        <xsl:call-template name='write-chunk'>
          <xsl:with-param name='current-chunk' select='$current-chunk+1'/>
          <xsl:with-param name='chunks' select='$chunks'/>
          <xsl:with-param name='max-width' select='$max-width'/>
          <xsl:with-param name='written-width' select='0'/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name='write-unsplittable-chunk'>
    <xsl:param name='text'/>
    <xsl:param name='max-width'/>
    <xsl:value-of select='substring($text,1,$max-width)'/>
    <xsl:text>&#10;</xsl:text>
    <xsl:if test='substring($text,$max-width+1)'>
      <xsl:call-template name='write-unsplittable-chunk'>
        <xsl:with-param name='text'  select='substring($text,$max-width+1)'/>
        <xsl:with-param name='max-width' select='$max-width'/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>


</xsl:stylesheet>
