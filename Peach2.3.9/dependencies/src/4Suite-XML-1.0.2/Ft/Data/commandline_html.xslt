<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  exclude-result-prefixes="f"
>
  <!--
    Stylesheet to generate 4Suite command-line application docs
  -->

  <xsl:output method="html"/>

  <xsl:template match="application">
    <html>
      <head>
    	<title>Command-line Application <xsl:value-of select="@name"/></title>
        <link rel="stylesheet" type="text/css" href="commandline.css"/>
      </head>
      <body>
        <xsl:call-template name='do-application'/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match='command' name='do-application'>
    <a name='{generate-id(.)}'>
      <h1>
        <xsl:choose>
          <xsl:when test='name(.) = "application"'>
            <xsl:text>Commandline Application - </xsl:text>
            <xsl:value-of select="@name" />
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>Command - </xsl:text>
            <xsl:for-each select='ancestor-or-self::*'>
              <xsl:if test='name(.) = "command" or name(.) = "application"'>
                <xsl:value-of select='@name'/>
                <xsl:text> </xsl:text>
              </xsl:if>
            </xsl:for-each>
          </xsl:otherwise>
        </xsl:choose>
      </h1>
    </a>
    <h4>
      <xsl:value-of select="description"/>
    </h4>
    <blockquote>
      <xsl:value-of select="verbose-description"/>
    </blockquote>

    <H2>Usage</H2>
    <TABLE>
      <TR VALIGN='top'>
        <TD>
          <pre>
            <xsl:choose>
              <xsl:when test='name(.) = "application"'>
                <xsl:value-of select="@name" />
              </xsl:when>
              <xsl:otherwise>
                <xsl:for-each select='ancestor-or-self::*'>
                  <xsl:if test='name(.) = "command" or name(.) = "application"'>
                    <xsl:value-of select='@name'/>
                    <xsl:text> </xsl:text>
                  </xsl:if>
                </xsl:for-each>
              </xsl:otherwise>
            </xsl:choose>
          </pre>
        </TD>
        <TD>
          <xsl:variable name='usage'>
            <xsl:for-each select='options/* | arguments/*'>
              <xsl:apply-templates  select='.' mode='usage'/>
              <xsl:if test='position() != last()'>
                <xsl:text> </xsl:text>
              </xsl:if>
            </xsl:for-each>
          </xsl:variable>
          <pre>
            <xsl:value-of select="f:wrap($usage,60)"/>
          </pre>
        </TD>
      </TR>
    </TABLE>
    <xsl:apply-templates select="options" mode="detail"/>
    <xsl:choose>
      <xsl:when test="subcommands">
        <xsl:apply-templates select='subcommands' mode='overview'/>
        <xsl:for-each select='subcommands/command'>
          <HR/>
          <xsl:apply-templates select='.'/>
        </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="arguments"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match='option' mode='usage'>
    <xsl:text>[--</xsl:text>
    <xsl:value-of select='@long-name'/>
    <xsl:if test='argument'>
      <xsl:choose>
        <xsl:when test='argument/value'>
          <xsl:text>=[</xsl:text>
          <xsl:for-each select='argument/value'>
            <xsl:value-of select='@name'/>
            <xsl:if test='position() != last()'>
              <xsl:text>|</xsl:text>
            </xsl:if>
          </xsl:for-each>
          <xsl:text>]</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select='concat("=&lt;",argument/@name,"&gt;")'/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:text>]</xsl:text>
  </xsl:template>


  <xsl:template match='exclusive-options' mode='usage'>
    <xsl:variable name='temp'>
      <xsl:for-each select='option'>
        <xsl:apply-templates select='.' mode='usage'/>
        <xsl:if test='position() != last()'>
          <xsl:text> | </xsl:text>
        </xsl:if>
      </xsl:for-each>
    </xsl:variable>
    <xsl:value-of select='concat("[",string($temp),"]")'/>
  </xsl:template>

  <xsl:template match='argument' mode='usage'>
    <xsl:if test='@required != "yes"'>
      <xsl:text>[</xsl:text>
    </xsl:if>
    <xsl:value-of select='@name'/>
    <xsl:if test='@required != "yes"'>
      <xsl:text>]</xsl:text>
    </xsl:if>
    <xsl:if test='@multiple = "yes"'>
      <xsl:text>...</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match='*' mode='usage'>
    UNSUPPORTED USAGE<xsl:value-of select='name()'/>
  </xsl:template>


  <xsl:template match='options' mode='detail'>
    <h2>Options</h2>
    <TABLE cellpadding="4">
      <tr>
        <th align="left">Name</th>
        <th align="center">Description</th>
      </tr>
      <xsl:apply-templates select='*' mode='detail'/>
    </TABLE>
  </xsl:template>

  <xsl:template match='option' mode='detail'>
    <TR VALIGN='TOP'>
      <TD>
        <xsl:if test='@short-name'>
          <xsl:text>-</xsl:text>
          <xsl:value-of select ='@short-name'/>
          <xsl:text>, </xsl:text>
        </xsl:if>
        <xsl:text>--</xsl:text>
        <xsl:value-of select='@long-name'/>
        <xsl:if test='argument'>
          <xsl:choose>
            <xsl:when test='argument/value'>
              <xsl:text>=[</xsl:text>
              <xsl:for-each select='argument/value'>
                <xsl:value-of select='@name'/>
                <xsl:if test='position() != last()'>
                  <xsl:text>|</xsl:text>
                </xsl:if>
              </xsl:for-each>
              <xsl:text>]</xsl:text>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select='concat("=&lt;",argument/@name,"&gt;")'/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>
      </TD>
      <TD>
        <xsl:value-of select='description'/>
        <xsl:if test='argument/value'>
          <BR/><B>Allowed Values:</B>
          <TABLE>
            <xsl:for-each select='argument/value'>
              <TR>
                <TD><xsl:value-of select='@name'/></TD>
                <TD><xsl:value-of select='description'/></TD>
              </TR>
            </xsl:for-each>
          </TABLE>
        </xsl:if>
      </TD>
    </TR>
  </xsl:template>

  <xsl:template match='exclusive-options' mode='detail'>
    <xsl:apply-templates select='option' mode='detail'/>
  </xsl:template>

  <xsl:template match='subcommands' mode='overview'>
    <H2>Sub Commands</H2>
    <TABLE cellpadding="4">
      <tr>
        <th align="left">Command</th>
        <th align="center">Description</th>
      </tr>
      <xsl:apply-templates select='command' mode='overview'>
        <xsl:sort select='@name'/>
      </xsl:apply-templates>
    </TABLE>
  </xsl:template>

  <xsl:template match='command' mode='overview'>
    <TR>
      <TD>
        <a href='#{generate-id(.)}'>
          <xsl:for-each select='ancestor-or-self::*'>
            <xsl:if test='name(.) = "command" or name(.) = "application"'>
              <xsl:value-of select='@name'/>
              <xsl:text> </xsl:text>
            </xsl:if>
          </xsl:for-each>
        </a>
      </TD>
      <TD>
        <xsl:value-of select='description'/>
      </TD>
    </TR>
  </xsl:template>

  <xsl:template match='arguments'>
    <H2>Arguments</H2>
    <TABLE cellpadding="4">
      <tr>
        <th align="left">Name</th>
        <th align="center">Description</th>
      </tr>
      <xsl:apply-templates select='argument'/>
    </TABLE>
  </xsl:template>

  <xsl:template match='argument'>
    <TR>
      <TD><xsl:value-of select='@name'/></TD>
      <TD><xsl:value-of select='description'/></TD>
    </TR>
  </xsl:template>

</xsl:stylesheet>

