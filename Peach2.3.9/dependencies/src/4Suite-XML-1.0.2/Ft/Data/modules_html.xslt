<?xml version="1.0" encoding="ISO-8859-1" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method='html' encoding='iso-8859-1'/>

  <xsl:param name="top-documentation-link">../index.html</xsl:param>

  <xsl:key name="classes" match="class" use="@name"/>

  <!-- Main ==============================================================-->

  <xsl:template match="module">
    <html>
      <head>
        <title>
          <xsl:text>4Suite API Documentation: </xsl:text>
          <xsl:value-of select="@name"/>
        </title>
        <link rel="stylesheet" type="text/css" href="modules.css"/>
      </head>
      <body>
        <div class="universal-header">
          <span class="universal-header-prefix">&#160;&#160;&#160;</span>
          <xsl:text>&#160;</xsl:text>
          <span class="universal-header-prefix">&#160;&#160;</span>
          <xsl:text>&#160;</xsl:text>
          <span class="universal-header-prefix">&#160;</span>
          <xsl:text>&#160;</xsl:text>
          <a href="{$top-documentation-link}">4Suite<sup>&#8482;</sup> API Documentation</a>
        </div>
        <h1>
          <span class="glyph-arrow">&#9658;</span>
          <xsl:text> Module </xsl:text>
          <span class="this-name">
            <xsl:call-template name='link-python-path'>
              <xsl:with-param name='path' select='@name'/>
            </xsl:call-template>
          </span>
        </h1>

        <xsl:apply-templates select="abstract"/>
        <xsl:apply-templates select="description"/>

        <xsl:variable name="members"
                      select="(classes|functions|globals)[*/@public = 'yes']"/>
        <xsl:if test="$members">
          <div class="summary-section">
            <table cellpadding="0" cellspacing="0">
              <tbody>
                <tr>
                  <xsl:apply-templates select="$members" mode="summary"/>
                </tr>
              </tbody>
            </table>
          </div>
        </xsl:if>

        <xsl:apply-templates select="modules"/>
        <xsl:apply-templates select="classes"/>
        <xsl:apply-templates select="functions"/>
        <xsl:apply-templates select="globals"/>

        <div class="universal-footer">
          <xsl:text>Last modified on </xsl:text>
          <xsl:value-of select="modification-date"/>
        </div>
      </body>
    </html>
  </xsl:template>

  <!-- Module Summary ====================================================-->

  <xsl:template match="classes | functions | globals" mode="summary">
    <!-- add separator cells between groups -->
    <xsl:if test="position() != 1">
      <td valign="middle" width="7"/>
      <td valign="middle" width="1" bgcolor="#C5C5C5"/>
      <td valign="middle" width="7"/>
    </xsl:if>

    <td valign="top">
      <div class="summary-header">
        <xsl:choose>
          <xsl:when test="name() = 'classes'">Classes:</xsl:when>
          <xsl:when test="name() = 'functions'">Functions:</xsl:when>
          <xsl:when test="name() = 'globals'">Globals:</xsl:when>
        </xsl:choose>
      </div>
      <div class="summary-list">
        <xsl:for-each select="*[@public = 'yes']">
          <span class="{name()}-name">
            <a href="#{@name}"><xsl:value-of select="@name"/></a>
          </span>
          <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
      </div>
    </td>
  </xsl:template>

  <!-- Modules ===========================================================-->

  <xsl:template match="modules">
    <xsl:variable name="public" select="module-reference[@public = 'yes']"/>
    <xsl:if test="$public">
      <div class="section">
        <h2>Modules</h2>
        <table class="modules">
          <tbody>
            <xsl:apply-templates select="$public" mode="module"/>
          </tbody>
        </table>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="module-reference" mode="module">
    <tr>
      <td valign="top" class="moduledef">
        <div class="module-name">
          <a name="{@name}"/>
          <xsl:choose>
            <xsl:when test="@documented = 'no'">
              <span class='undocumented'>
                <xsl:value-of select="@name"/>
              </span>
            </xsl:when>
            <xsl:otherwise>
              <a>
                <xsl:attribute name="href">
                  <xsl:call-template name='translate-href'>
                    <xsl:with-param name="href" select="@realname"/>
                  </xsl:call-template>
                </xsl:attribute>
                <xsl:value-of select="@name"/>
              </a>
            </xsl:otherwise>
          </xsl:choose>
        </div>
      </td>
      <td valign="bottom" class="moduledesc">
        <xsl:apply-templates select='abstract'/>
      </td>
    </tr>
  </xsl:template>

  <!-- Classes ===========================================================-->

  <xsl:template match="classes">
    <xsl:variable name="public" select="class[@public = 'yes']"/>
    <xsl:if test="$public">
      <div class="section">
        <h2>Classes</h2>
        <dl class="classes">
          <xsl:apply-templates select="$public"/>
        </dl>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template name="class-reference">
    <xsl:param name="refnode" select="."/>
    <xsl:param name="fullname" select="true()"/>
    <xsl:variable name="class" select="$refnode/@class"/>
    <xsl:variable name="module" select="$refnode/@module"/>

    <xsl:choose>
      <xsl:when test="$refnode/@documented = 'no' or
                      key('classes', $class)/@public = 'no'">
        <span class='undocumented'>
          <xsl:if test="@module">
            <xsl:value-of select="concat($module, '.')"/>
          </xsl:if>
          <xsl:value-of select="$class"/>
        </span>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name='href'>
          <xsl:call-template name='translate-href'>
            <xsl:with-param name='href' select='$module'/>
          </xsl:call-template>
        </xsl:variable>
        <a href='{$href}#{$class}'>
          <xsl:if test="$fullname and $module != /module/@name">
            <xsl:value-of select="concat($module, '.')"/>
          </xsl:if>
          <xsl:value-of select="$class"/>
        </a>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="class">
    <dt class="classdef">
      <a name="{@name}"/>
      <xsl:text>class </xsl:text>
      <span class="class-name">
        <xsl:value-of select="@name"/>
      </span>
      <xsl:apply-templates select="bases"/>
    </dt>
    <dd class="classdesc">
      <xsl:apply-templates select="abstract"/>
      <xsl:apply-templates select="description"/>
      <xsl:apply-templates select="methods"/>
      <xsl:apply-templates select="inherited-methods"/>
      <xsl:apply-templates select="members"/>
      <xsl:apply-templates select="inherited-members"/>
    </dd>
  </xsl:template>

  <xsl:template match="bases">
    <span class="bases">
      <xsl:text>(</xsl:text>
      <xsl:apply-templates select="*"/>
      <xsl:text>)</xsl:text>
    </span>
  </xsl:template>

  <xsl:template match="base">
    <xsl:if test='position() &gt; 1'>, </xsl:if>
    <span class="class-name">
      <xsl:call-template name="class-reference"/>
    </span>
  </xsl:template>

  <xsl:template match='methods'>
    <h3>Methods</h3>
    <dl class="methods">
      <xsl:apply-templates select="*"/>
    </dl>
  </xsl:template>

  <xsl:template match='method | class-method | static-method'>
    <dt class="methoddef">
      <a name="{@id}">
        <span class="method-name">
          <xsl:value-of select='@name'/>
        </span>
      </a>
      <xsl:if test='@realname'> = </xsl:if>
      <xsl:choose>
        <xsl:when test='@realid'>
          <a href='#{@realid}'>
            <xsl:value-of select='@realname'/>
          </a>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select='@realname'/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select='arguments'/>
    </dt>
    <dd class="methoddesc">
      <xsl:apply-templates select="abstract"/>
      <xsl:apply-templates select="description"/>
    </dd>
    <xsl:if test="overrides">
      <dd class="overrides">
        <b>Overrides: </b>
        <span class="inherited-name">
          <xsl:choose>
            <xsl:when test="overrides/@documented = 'yes'">
              <a>
                <xsl:attribute name="href">
                  <xsl:call-template name='translate-href'>
                    <xsl:with-param name='href' select='overrides/@module'/>
                  </xsl:call-template>
                  <xsl:text>#</xsl:text>
                  <xsl:value-of select="overrides/@class"/>
                  <xsl:text>-</xsl:text>
                  <xsl:value-of select="@name"/>
                </xsl:attribute>
                <xsl:value-of select="@name"/>
              </a>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="@name"/>
            </xsl:otherwise>
          </xsl:choose>
        </span>
        <xsl:text> from class </xsl:text>
        <span class="class-name">
          <xsl:call-template name="class-reference">
            <xsl:with-param name="refnode" select="overrides"/>
            <xsl:with-param name="fullname" select="false()"/>
          </xsl:call-template>
        </span>
      </dd>
    </xsl:if>
  </xsl:template>

  <xsl:template match="inherited-methods">
    <xsl:variable name="class" select="key('classes', @class)"/>
    <xsl:variable name="documented" select="@documented = 'yes'"/>
    <xsl:variable name='linkbase'>
      <xsl:call-template name='translate-href'>
        <xsl:with-param name='href' select='@module'/>
      </xsl:call-template>
      <xsl:text>#</xsl:text>
      <xsl:value-of select="@class"/>
    </xsl:variable>

    <h3>
      <xsl:text>Methods inherited from class </xsl:text>
      <xsl:call-template name="class-reference"/>
    </h3>
    <xsl:choose>
      <!-- if the class is in this module and not public -->
      <xsl:when test="$class/@public = 'no'">
        <xsl:variable name="methods" select="$class/methods/method"/>
        <dl class="methods">
          <xsl:for-each select="member-reference">
            <xsl:apply-templates select="$methods[@name = current()/@name]"/>
          </xsl:for-each>
        </dl>
      </xsl:when>
      <xsl:otherwise>
        <div class="inherited">
          <xsl:for-each select="member-reference">
            <xsl:if test="position() &gt; 1">, </xsl:if>
            <span class="inherited-name">
              <xsl:choose>
                <xsl:when test="$documented">
                  <a href='{$linkbase}-{@name}'>
                    <xsl:value-of select="@name"/>
                  </a>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="@name"/>
                </xsl:otherwise>
              </xsl:choose>
            </span>
          </xsl:for-each>
        </div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match='members'>
    <h3>Members</h3>
    <dl class="members">
      <xsl:apply-templates select="*"/>
    </dl>
  </xsl:template>

  <xsl:template match='member'>
    <dt class="memberdef">
      <a name="{@name}">
        <span class="member-name">
          <xsl:value-of select="@name"/>
        </span>
      </a>
      <xsl:text> = </xsl:text>
      <xsl:value-of select='value'/>
    </dt>
    <xsl:if test="abstract | description">
      <dd class="memberdesc">
        <xsl:apply-templates select='abstract'/>
        <xsl:apply-templates select='description'/>
      </dd>
    </xsl:if>
  </xsl:template>

  <xsl:template match="inherited-members">
    <xsl:variable name="class" select="key('classes', @class)"/>
    <xsl:variable name="documented" select="@documented = 'yes'"/>
    <xsl:variable name='linkbase'>
      <xsl:call-template name='translate-href'>
        <xsl:with-param name='href' select='@module'/>
      </xsl:call-template>
      <xsl:text>#</xsl:text>
      <xsl:value-of select="@class"/>
    </xsl:variable>

    <h3>
      <xsl:text>Members inherited from class </xsl:text>
      <xsl:call-template name="class-reference"/>
    </h3>
    <xsl:choose>
      <!-- if the class is in this module and not public -->
      <xsl:when test="$class/@public = 'no'">
        <xsl:variable name="members" select="$class/members/member"/>
        <dl class="members">
          <xsl:for-each select="member-reference">
            <xsl:apply-templates select="$members[@name = current()/@name]"/>
          </xsl:for-each>
        </dl>
      </xsl:when>
      <xsl:otherwise>
        <div class="inherited">
          <xsl:for-each select="member-reference">
            <xsl:if test="position() &gt; 1">, </xsl:if>
            <span class="inherited-name">
              <xsl:choose>
                <xsl:when test="$documented">
                  <a href='{$linkbase}-{@name}'>
                    <xsl:value-of select="@name"/>
                  </a>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="@name"/>
                </xsl:otherwise>
              </xsl:choose>
            </span>
          </xsl:for-each>
        </div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Functions =========================================================-->

  <xsl:template match="functions">
    <xsl:variable name="public" select="*[@public = 'yes']"/>
    <xsl:if test="$public">
      <div class="section">
        <h2>Functions</h2>
        <dl class="functions">
          <xsl:apply-templates select="$public"/>
        </dl>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="function">
    <dt class="functiondef">
      <a name="{@id}">
        <span class="function-name">
          <xsl:value-of select='@name'/>
        </span>
      </a>
      <xsl:if test='@realname'> = </xsl:if>
      <xsl:choose>
        <xsl:when test='@realid'>
          <a href='#{@realid}'>
            <xsl:value-of select='@realname'/>
          </a>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select='@realname'/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select='arguments'/>
    </dt>
    <dd class="functiondesc">
      <xsl:apply-templates select="abstract"/>
      <xsl:apply-templates select="description"/>
    </dd>
  </xsl:template>


  <!-- Function Arguments ================================================-->

  <xsl:template match='arguments'>
    <xsl:text>(</xsl:text>
    <xsl:apply-templates select='*' mode='argument'/>
    <xsl:text>)</xsl:text>
  </xsl:template>

  <xsl:template match='arg' mode='argument'>
    <xsl:if test='position() &gt; 1'>, </xsl:if>
    <span class="argument-name">
      <xsl:value-of select='@name'/>
    </span>
    <xsl:if test='@default'>
      <span class='argument-default'>
        <xsl:text>=</xsl:text>
        <xsl:value-of select='@default'/>
      </span>
    </xsl:if>
  </xsl:template>

  <xsl:template match='sequence' mode='argument'>
    <xsl:if test='position() &gt; 1'>, </xsl:if>
    <xsl:text>(</xsl:text>
    <xsl:apply-templates select='*' mode='argument'/>
    <xsl:if test='count(*) = 1'>
      <!-- add the trailing comma for tuples of length one -->
      <xsl:text>,</xsl:text>
    </xsl:if>
    <xsl:text>)</xsl:text>
  </xsl:template>

  <xsl:template match='var-args' mode='argument'>
    <xsl:if test='position() &gt; 1'>, </xsl:if>
    <span class="argument-name">
      <xsl:text>*</xsl:text>
      <xsl:value-of select='@name'/>
    </span>
  </xsl:template>

  <xsl:template match='var-keywords' mode='argument'>
    <xsl:if test='position() &gt; 1'>, </xsl:if>
    <span class="argument-name">
      <xsl:text>**</xsl:text>
      <xsl:value-of select='@name'/>
    </span>
  </xsl:template>

  <xsl:template match='unknown' mode='argument'>
    <span class="argument-name">
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!-- Globals ===========================================================-->

  <xsl:template match="globals">
    <xsl:variable name='public' select="*[@public = 'yes']"/>
    <xsl:if test="$public">
      <div class="section">
        <h2>Globals</h2>
        <dl class="globals">
          <xsl:apply-templates select='$public'/>
        </dl>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="global">
    <dt class="globaldef">
      <a name="{@name}">
        <span class="global-name">
          <xsl:value-of select="@name"/>
        </span>
      </a>
      <xsl:text> = </xsl:text>
      <xsl:value-of select='value'/>
    </dt>
    <dd class="globaldesc">
      <xsl:apply-templates select='abstract'/>
      <xsl:apply-templates select='description'/>
    </dd>
  </xsl:template>

  <!-- Descriptions ======================================================-->

  <xsl:template match="abstract[normalize-space()]">
    <div class="abstract">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="description[normalize-space()]">
    <pre class="description">
      <xsl:apply-templates/>
    </pre>
  </xsl:template>

  <!-- Helper functions to allow overriding of link creation -->
  <xsl:template name='translate-href'>
    <xsl:param name='href'/>
    <xsl:if test="$href">
      <xsl:value-of select='concat($href,".html")'/>
    </xsl:if>
  </xsl:template>


  <!-- Funcion to split a Python dotted path into separate links -->
  <xsl:template name='link-python-path'>
    <xsl:param name='path'/>
    <xsl:param name='parent-path'/>

    <xsl:choose>
      <xsl:when test="contains($path, '.')">
        <xsl:variable name="module" select="substring-before($path, '.')"/>
        <xsl:variable name="fullpath">
          <xsl:if test='$parent-path'>
            <xsl:value-of select="concat($parent-path, '.')"/>
          </xsl:if>
          <xsl:value-of select='$module'/>
        </xsl:variable>

        <a title="{$fullpath}">
          <xsl:attribute name="href">
            <xsl:call-template name='translate-href'>
              <xsl:with-param name='href' select='$fullpath'/>
            </xsl:call-template>
          </xsl:attribute>
          <xsl:value-of select="$module"/>
        </a>
        <xsl:text>.</xsl:text>

        <xsl:call-template name='link-python-path'>
          <xsl:with-param name="path" select="substring-after($path, '.')"/>
          <xsl:with-param name="parent-path" select="$fullpath"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <!-- no link needed as this is the module we're displaying -->
        <xsl:value-of select="$path"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
