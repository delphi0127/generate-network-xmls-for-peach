<?xml version="1.0"?>
<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:a="http://a" xmlns:func="http://exslt.org/functions" extension-element-prefixes="func">

  <func:function name="a:a-echo">
    <xsl:param name="a-param"/>
    <func:result>
      <xsl:value-of select="$a-param"/>
    </func:result>
  </func:function>

</xsl:transform>
