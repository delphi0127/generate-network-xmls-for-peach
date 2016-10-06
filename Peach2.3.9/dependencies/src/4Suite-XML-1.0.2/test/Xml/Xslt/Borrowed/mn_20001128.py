#Miloslav Nic <nicmila@idoox.com> has a cool element/attribute stats tool

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
version =
"1.0" > 
   <xsl:output method="text"/>

   <xsl:key name="elements" match="*" use="name()"/>
   <xsl:key name="attributes" match="@*"
use="concat(name(parent::*),':::',name())"/>
<xsl:key name="allSameAttributes" match="@*" use="name(parent::*)"/>

   <xsl:template match = "*" > 
     <xsl:if test="generate-id() = generate-id(key('elements',name()))">
       <xsl:text>&#xA;</xsl:text>
       <xsl:value-of select="name()"/>
       <xsl:apply-templates select="key('allSameAttributes',name())">
         <xsl:sort select='name()'/>
       </xsl:apply-templates>
     </xsl:if>
     <xsl:apply-templates/>
   </xsl:template> 

   <xsl:template match="@*">
     <xsl:if test="position()=1">
       <xsl:text> [ </xsl:text>
     </xsl:if>

     <xsl:if test="generate-id() =
generate-id(key('attributes',concat(name(parent::*),':::',name())))">
       <xsl:value-of select="name()"/>
       <xsl:text> </xsl:text>
     </xsl:if>

     <xsl:if test="position()=last()">
       <xsl:text> ] </xsl:text>
     </xsl:if>
   </xsl:template>

   <xsl:template match="text()"/>
 </xsl:stylesheet>"""


sheet_2 = """<xsl:stylesheet xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
 version =
 "1.0" > 
    <xsl:output method="text"/>

    <xsl:key name="elements" match="*" use="name()"/>
    <xsl:key name="attributes" match="@*"
 use="concat(name(parent::*),':::',name())"/>
    <xsl:key name="allSameAttributes" match="@*" use="name(parent::*)"/>

    <xsl:template match="/">
      <xsl:apply-templates select="//*">
        <xsl:sort select="name()"/>
      </xsl:apply-templates>
    </xsl:template>

    <xsl:template match = "*" >
      <xsl:if test="generate-id() = generate-id(key('elements',name()))">
        <xsl:text>&#xA;</xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:apply-templates select="key('allSameAttributes',name())">
          <xsl:sort select="name()"/>
        </xsl:apply-templates>
      </xsl:if>
    </xsl:template> 

    <xsl:template match="@*">
      <xsl:if test="generate-id() =
 generate-id(key('attributes',concat(name(parent::*),':::',name())))">
        <xsl:text>&#xA;     </xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:text>: </xsl:text>
        <xsl:apply-templates
 select="key('attributes',concat(name(parent::*),':::',name()))"
 mode="values">
          <xsl:sort/>
        </xsl:apply-templates>
      </xsl:if>
    </xsl:template>

    <xsl:template match="@*" mode="values">
      <xsl:variable name="sameValues" 
        select="key('attributes',concat(name(parent::*),':::',name()))[.
 = current()]" />

        <xsl:if test="generate-id() = generate-id($sameValues)">
          <xsl:value-of select="."/>
          <xsl:text>(</xsl:text>
          <xsl:value-of select="count($sameValues)"/>
          <xsl:text>) </xsl:text>
        </xsl:if>

    </xsl:template>

    <xsl:template match="text()"/>
  </xsl:stylesheet>"""


source_2 = """<AAA> 
            <XXX/>
           <BBB bb = "1" ccc="OOOOO"> 
                <CCC uuu="234">c11 </CCC> 
                <CCC ccc="ZZZ">c12 </CCC> 
                <CCC ccc="XXX">c13 </CCC> 
            </BBB> 
           <BBB bb = "2" > 
                <CCC>c21 </CCC> 
                <CCC ccc="AAA">c22 </CCC> 
                <CCC ccc="XXX">c23 </CCC> 
            </BBB> 
           <BBB bb = "2" > 
                <CCC>c31</CCC> 
                <CCC>c32</CCC> 
                <CCC sss="WWWW">c33</CCC>
            </BBB> 
 </AAA>"""


expected_1 = """
slideshow
title
metadata
speaker
jobTitle
organization
presentationDate
presentationLocation
occasion
slideset
slide [ id  ] 
item
speakerNote
emphasis [ role  ] 
heading
bulletlist
preformatted
graphic [ file height width  ] 
link [ href  ] 
para"""


expected_2 = """
bulletlist
emphasis
     role: note(3) 
graphic
     file: sample.svg(1) 
     height: 800(1) 
     width: 800(1) 
heading
item
jobTitle
link
     href: http://dmoz.org/Computers/Data_Formats/Graphics/Vector/SVG/(1) http://www.sun.com/xml/developers/svg-slidetoolkit/(1) http://www.w3.org/Graphics/SVG(1) 
metadata
occasion
organization
para
preformatted
presentationDate
presentationLocation
slide
     id: I.1(1) II.1(1) II.2(1) II.3(1) III.1(1) III.2(1) 
slideset
slideshow
speaker
speakerNote
title"""


expected_3 = """
AAA
BBB
     bb: 1(1) 2(2) 
     ccc: OOOOO(1) 
CCC
     ccc: AAA(1) XXX(2) ZZZ(1) 
     sss: WWWW(1) 
     uuu: 234(1) 
XXX"""


def Test(tester):
    source = test_harness.FileInfo(uri="Xml/Xslt/Borrowed/slides4svg.xml")
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')


    source = test_harness.FileInfo(uri="Xml/Xslt/Borrowed/slides4svg.xml")
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')


    source = test_harness.FileInfo(string=source_2)
    sty = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 3')
    return
