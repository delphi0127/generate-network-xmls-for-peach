
import time

from Ft.Xml.Xslt import StylesheetCompilier

ADDRBOOK="""<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
	<TR>
	<xsl:apply-templates select='NAME'/>
	</TR>
  </xsl:template>

  <xsl:template match="NAME">
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
"""

ADDRBOOK_XML_1="""<?xml version = "1.0"?>
<!DOCTYPE ADDRBOOK SYSTEM "addr_book.dtd">
<ADDRBOOK xmlns:xlink="http://www.w3.org/XML/XLink/0.9">"""
ADDRBOOK_XML_ENTRY="""
	<ENTRY ID="vz">
		<NAME>Vasia Zhugenev</NAME>
		<ADDRESS>2000 Disaster Plaza</ADDRESS>
		<PHONENUM DESC="Work">000-987-6543</PHONENUM>
		<PHONENUM DESC="Cell">000-000-0000</PHONENUM>
		<EMAIL>vxz@magog.ru</EMAIL>
	</ENTRY>"""
ADDRBOOK_XML_2="""
</ADDRBOOK>
"""

ERASTOTHENES_SOURCE="""<dummy/>"""
ERASTOTHENES_FILE="borrowed/erastothenes.xslt"


def test():

    #Test generating a file and running it
    #Test a simple addrbook

    #Build a ADDRBOOK xml file
    print "Address Book"
    src = ADDRBOOK_XML_1 + (ADDRBOOK_XML_ENTRY*5000) + ADDRBOOK_XML_2
    s = time.time()
    StylesheetCompilier.CompileString(ADDRBOOK,outFileName='addrbook')
    e = time.time()
    t = e - s
    print "Compile Time: %f" % (t)

    import addrbook
    st = addrbook.Stylesheet()
    s = time.time()
    st.executeString(src)
    e = time.time()
    cTime = e - s
    print "Compile Time: %f" % (cTime)

    from Ft.Xml.Xslt import Processor
    p = Processor.Processor()
    p.appendStylesheetString(ADDRBOOK)
    s = time.time()
    p.runString(src)
    e = time.time()
    pTime = e - s
    print "Processor Time: %f" % (pTime)
    print "Difference %f" % (pTime - cTime)
    print "Increase %f" % (100.0*(pTime - cTime)/pTime)


def test2():

    #Run a larger document (RDF API document)
    print "RDF API"
    srcUri = "/usr/doc/4Suite-0.10.1/docs/xml/4RDF.api"
    styUri = "/usr/local/lib/xslt/api.xslt"
    s = time.time()
    StylesheetCompilier.CompileUri(styUri,outFileName='api',baseUri='/usr/local/lib/xslt/')
    e = time.time()
    t = e - s
    print "Compile Time: %f" % (t)
    




    #Run The Sieve of Erastothenes
    StylesheetCompilier.CompileUri(ERASTOTHENES_FILE,outFileName='erastonthenes')



    



if __name__ == '__main__':
    #test()
    test2()
