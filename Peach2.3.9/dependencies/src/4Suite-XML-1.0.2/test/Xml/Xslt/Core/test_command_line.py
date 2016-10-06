import os, sys, tempfile

from Ft.Lib.CommandLine import CommandLineTestUtil
from Ft.Xml.Lib import TreeCompare

source_1 = """<?xml version = "1.0"?>
<ADDRBOOK>
    <ENTRY ID="pa">
        <NAME>Pieter Aaron</NAME>
        <ADDRESS>404 Error Way</ADDRESS>
        <PHONENUM DESC="Work">404-555-1234</PHONENUM>
        <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
        <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
        <EMAIL>pieter.aaron@inter.net</EMAIL>
    </ENTRY>
    <ENTRY ID="en">
        <NAME>Emeka Ndubuisi</NAME>
        <ADDRESS>42 Spam Blvd</ADDRESS>
        <PHONENUM DESC="Work">767-555-7676</PHONENUM>
        <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
        <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
        <EMAIL>endubuisi@spamtron.com</EMAIL>
    </ENTRY>
    <ENTRY ID="vz">
        <NAME>Vasia Zhugenev</NAME>
        <ADDRESS>2000 Disaster Plaza</ADDRESS>
        <PHONENUM DESC="Work">000-987-6543</PHONENUM>
        <PHONENUM DESC="Cell">000-000-0000</PHONENUM>
        <EMAIL>vxz@magog.ru</EMAIL>
    </ENTRY>
</ADDRBOOK>"""

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:strip-space elements='*'/>

  <xsl:param name='title' select='"Untitled"'/>
  
  <xsl:template match="/">
    <HTML>
      <HEAD>
        <TITLE><xsl:value-of select='$title'/></TITLE>
      </HEAD>
      <BODY>
        <TABLE><xsl:apply-templates/></TABLE>
      </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
    <xsl:element name='TR'>
      <xsl:apply-templates select='NAME'/>
    </xsl:element>
    <xsl:if test='not(position()=last())'><HR/></xsl:if>
  </xsl:template>

  <xsl:template match="NAME">
    <xsl:element name='TD'>
      <xsl:attribute name='ALIGN'>CENTER</xsl:attribute>
      <B><xsl:apply-templates/></B>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
"""

expected_1 = """<HTML>
  <HEAD>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <TITLE>Untitled</TITLE>
  </HEAD>
  <BODY>
    <TABLE>
      <TR>
        <TD ALIGN="CENTER"><B>Pieter Aaron</B></TD>
      </TR>
      <HR>
      <TR>
        <TD ALIGN="CENTER"><B>Emeka Ndubuisi</B></TD>
      </TR>
      <HR>
      <TR>
        <TD ALIGN="CENTER"><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""

expected_2 = """<HTML>
  <HEAD>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <TITLE>Untitled</TITLE>
  </HEAD>
  <BODY>
    <TABLE>
      <TR>
        <TD ALIGN="CENTER"><B>Pieter Aaron</B></TD>
      </TR>
      <HR>
      <TR>
        <TD ALIGN="CENTER"><B>Emeka Ndubuisi</B></TD>
      </TR>
      <HR>
      <TR>
        <TD ALIGN="CENTER"><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""

expected_3 = """<HTML>
  <HEAD>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <TABLE>
      <TR>
        <TD ALIGN="CENTER"><B>Pieter Aaron</B></TD>
      </TR>
      <HR>
      <TR>
        <TD ALIGN="CENTER"><B>Emeka Ndubuisi</B></TD>
      </TR>
      <HR>
      <TR>
        <TD ALIGN="CENTER"><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""


def Test(tester):
    xml_file = tempfile.mktemp()
    xslt_file = tempfile.mktemp()
    output_file = tempfile.mktemp()
    
    f = open(xml_file, 'w')
    f.write(source_1)
    f.close()
    f = open(xslt_file, 'w')
    f.write(sheet_1)
    f.close()


    tr1 = CommandLineTestUtil.TestRun('Simple Transform',
                                      {},
                                      [xml_file, xslt_file],
                                      expectedOut=expected_1,
                                      compareFunc=TreeCompare.TreeCompare)
    tr2 = CommandLineTestUtil.TestRun('Transform to output file',
                                      {'outfile' : output_file},
                                      [xml_file, xslt_file],
                                      outFile=output_file,
                                      expectedOut=expected_2,
                                      compareFunc=TreeCompare.TreeCompare)
    tr3 = CommandLineTestUtil.TestRun('Transform with parameters',
                                      {'define' : 'title=Address Book'},
                                      [xml_file, xslt_file],
                                      expectedOut=expected_3,
                                      compareFunc=TreeCompare.TreeCompare)
    t = CommandLineTestUtil.Test('4xslt',[tr1,tr2,tr3])
    t.test(tester)

    os.unlink(xml_file)
    os.unlink(xslt_file)
    return
