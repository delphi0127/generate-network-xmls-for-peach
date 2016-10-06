<?xml version="1.0"?>
<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:b="http://b" xmlns:func="http://exslt.org/functions" extension-element-prefixes="func">

  <func:function name="b:b-echo">
    <xsl:param name="b-param"/>
    <func:result>
      <xsl:value-of select="$b-param"/>
    </func:result>
  </func:function>

</xsl:transform>
