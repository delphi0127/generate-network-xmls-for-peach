<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html"/>

  <xsl:template match="ext-module">
    <html>
      <head>
        <title><xsl:value-of select="./@name"/></title>
        <link rel="stylesheet" type="text/css" href="extensions.css"/>
      </head>
      <body>
        <h1>
          <xsl:text>Extension Module - </xsl:text>
          <xsl:value-of select="@name" />
        </h1>
      <xsl:apply-templates mode="summary"/>
        <xsl:apply-templates select="functions"/>
        <xsl:apply-templates select="elements"/>
      </body>
    </html>
  </xsl:template>
    

  <xsl:template match="description" mode="summary">
    <xsl:if test="normalize-space(.)">
      <pre><xsl:apply-templates/></pre>
    </xsl:if>
  </xsl:template>


  <xsl:template match="namespaces" mode="summary">
    <h2>Namespaces</h2>
    <p>
      <xsl:text>The namespace</xsl:text>
      <xsl:if test="count(namespace) &gt; 1">s</xsl:if>
      <xsl:text> for extensions defined in this document are:</xsl:text>
    </p>
    <table cellpadding="4">
      <tr>
        <th align="left">Prefix</th>
        <th align="center">Namespace</th>
      </tr>
      <xsl:for-each select="namespace">
        <xsl:sort select="@prefix"/>
        <tr align="left">
          <td>
            <samp><xsl:value-of select="@prefix"/></samp>
          </td>
          <td>
            <samp><xsl:value-of select="@namespace-uri"/></samp>
          </td>
        </tr>
      </xsl:for-each>
    </table>
    <p>
      <xsl:text>The prefix</xsl:text>
      <xsl:choose>
        <xsl:when test="count(namespace) &gt; 1">es are </xsl:when>
        <xsl:otherwise> is </xsl:otherwise>
      </xsl:choose>
      <xsl:text>given for this document only. Any other prefix can be
      used within a particular stylesheet.</xsl:text>
    </p>
  </xsl:template>

  <xsl:template match="functions | elements" mode="summary">
    <xsl:param name="category" select="concat(translate(substring(name(), 1, 1), 'fe', 'FE'), substring(name(), 2))"/>
    <hr width="100%"/>
    <h2><xsl:value-of select="$category"/></h2>
    <table cellpadding="4">
      <tr>
        <th align="left">
          <xsl:value-of select="substring($category, 1, string-length($category) - 1)"/>
        </th>
        <th align="center">Syntax</th>
      </tr>
      <xsl:apply-templates mode="summary">
        <xsl:sort select="@name"/>
      </xsl:apply-templates>
    </table>
  </xsl:template>


  <xsl:template match="function | element" mode="summary">
    <tr align="left">
      <td valign="top">
        <a href="#{generate-id(.)}">
          <xsl:value-of select="@name"/>
        </a>
      </td>
      <td class="syntax">
        <xsl:apply-templates select="." mode="syntax"/>
      </td>
    </tr>
  </xsl:template>


  <xsl:template match="function" mode="syntax">
    <var><xsl:value-of select="result"/></var>
    <xsl:text> </xsl:text>
    <b><xsl:value-of select="@name"/></b>
    <xsl:text>(</xsl:text>
    <xsl:for-each select="argument">
      <xsl:if test="position() > 1">, </xsl:if>
      <var>
        <xsl:choose>
          <xsl:when test="@type">
            <xsl:value-of select="@type"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="@name"/>
          </xsl:otherwise>
        </xsl:choose>
      </var>
      <xsl:if test="@required = 'no'">?</xsl:if>
    </xsl:for-each>
    <xsl:text>)</xsl:text>
  </xsl:template>


  <xsl:template match="element" mode="syntax">
    <xsl:text>&lt;</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:apply-templates select="attribute" mode="syntax">
      <!-- using "descending" to put 'yes' before 'no' -->
      <xsl:sort select="@required" order="descending"/>
      <xsl:sort select="@name"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="content" mode="syntax"/>
    <xsl:text> /&gt;</xsl:text>
    <br/>
  </xsl:template>


  <xsl:template match="attribute" mode="syntax">
    <br/>
    <xsl:text>&#160;&#160;</xsl:text>
    <xsl:choose>
      <xsl:when test="@required = 'yes'">
        <b><xsl:value-of select="@name"/></b>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@name"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text> = </xsl:text>
    <xsl:value-of select="@content"/>
  </xsl:template>


  <xsl:template match="content" mode="syntax">
    <br/>
    <xsl:text>&#160;&#160;&lt;!-- Content: </xsl:text>
    <xsl:call-template name="expand-text-formatting">
      <xsl:with-param name="text" select="string(.)"/>
    </xsl:call-template>
    <xsl:text> --&gt;</xsl:text>
    <br/>
  </xsl:template>


  <xsl:template match="namespaces"/>


  <xsl:template match="functions | elements">
    <xsl:param name="category" select="concat(translate(substring(name(), 1, 1), 'fe', 'FE'), substring(name(), 2))"/>
    <hr width="100%"/>
    <h2><xsl:value-of select="$category"/></h2>
    <xsl:apply-templates select="*">
      <xsl:sort select="@name"/>
      <xsl:with-param name="category" select="substring($category, 1, string-length($category) - 1)"/>
    </xsl:apply-templates>
  </xsl:template>


  <xsl:template match="function | element">
    <xsl:param name="category"/>
    <div class="detail">
      <a name="{generate-id(.)}"/>
      <h3>
        <xsl:value-of select="$category"/>
        <xsl:text> - </xsl:text>
        <xsl:value-of select="@name"/>
      </h3>
      <h4>
        <xsl:value-of select="$category"/>
        <xsl:text> Syntax</xsl:text>
      </h4>
      <div class="syntax">
        <xsl:apply-templates select="." mode="syntax"/>
      </div>
      <p>
        <xsl:apply-templates select="description"/>
      </p>
    </div>
  </xsl:template>


  <xsl:template name="expand-text-formatting">
    <xsl:param name="text"/>
    <xsl:choose>
      <xsl:when test="not(contains($text, '/'))">
        <!-- no formatting here -->
        <xsl:value-of select="$text"/>
      </xsl:when>
      <xsl:when test="not(contains(substring-after($text, '/'), '/'))">
        <!-- only one, no formatting here -->
        <xsl:value-of select="$text"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="substring-before($text, '/')"/>
        <xsl:variable name="after" select="substring-after($text, '/')"/>
        <var>
          <xsl:value-of select="substring-before($after, '/')"/>
        </var>
        <xsl:call-template name="expand-text-formatting">
          <xsl:with-param name="text" select="substring-after($after, '/')"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
