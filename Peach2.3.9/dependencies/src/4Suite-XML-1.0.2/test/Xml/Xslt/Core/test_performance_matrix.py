#Grand test of many combinations of DOMs and other parameters that can affect performance.

import time, cStringIO
from Ft.Xml.Xslt.Processor import Processor
from Ft.Xml.Xslt import StylesheetReader, XsltException, Error
from Ft.Xml import pDomlette


def Test():
    top_level_ops = [
        SourceReading(),
        ]

    for op in top_level_ops:
        print "=" * len(op.title)
        print op.title
        if op.run():
            print "Relevant timing: ", op.lastTiming
            if op.comment:
                print "Comment: ", op.comment
    return


########################## Operations ##########################

class SourceReading:
    def __init__(self):
        self.title = "Check the performance of various methods of reading in source docs"
        self.lastTiming = 0.0
        self.lastResult = None
        self.ops = [DomFromSgmlopSax(), DomFromDefaultSax()]
        self.comment = ''
        self.failMsg = ''
        return

    def run(self):
        timings = []
        for key in g_source.keys():
            for op in self.ops:
                if op.run(g_source[key]):
                    print op.title
                    print "Source doc: ", key, "(", len(g_source[key]), "bytes)"
                    print "Relevant timing: ", op.lastTiming
                    timings.append(op.lastTiming)
                else:
                    print "FAILED"
                    print op.failMsg
        self.lastTiming = reduce(lambda x, y: x + y, timings, 0.0)
        return 1


class DomFromSgmlopSax:
    def __init__(self):
        self.title = "Read 4DOM from sgmlop using SAX"
        self.lastTiming = 0.0
        self.lastResult = None
        self.comment = ''
        self.failMsg = ''
        return

    def run(self, text):
        try:
            from xml.sax.saxexts import make_parser
            p = make_parser("xml.sax.drivers.drv_sgmlop")
            from xml.dom.ext.reader import Sax
            start = time.time()
            self.lastResult = Sax.FromXml(text, parser=p)
            end = time.time()
            self.lastTiming = end - start
            return 1
        except Exception, e:
            self.failMsg = str(e)
            return 0


class DomFromDefaultSax:
    def __init__(self):
        self.title = "Read 4DOM using the default SAX driver"
        self.lastTiming = 0.0
        self.lastResult = None
        self.comment = ''
        self.failMsg = ''
        return

    def run(self, text):
        try:
            from xml.dom.ext.reader import Sax
            start = time.time()
            self.lastResult = Sax.FromXml(text)
            end = time.time()
            self.lastTiming = end - start
            #self.comment = "Sax driver used: "
            return 1
        except Exception, e:
            self.failMsg = str(e)
            return 0


########################## Data ##########################


g_sheets = {
    "addr-book-1":
    """<?xml version="1.0"?>
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
        <xsl:apply-templates select='NAME | PHONENUM'/>
        </TR>
  </xsl:template>

  <xsl:template match="NAME">
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>""",

    "schematron-1.3":
    """<?xml version="1.0" ?>
<!--
    Preprocessor for the Schematron XML Schema Language.
        http://www.ascc.net/xml/resource/schematron/schematron.html
    Copyright (C) 1999 Rick Jelliffe and Academia Sinica Computing Centre
    Permission to use granted under GPL or MPL.
-->

<!-- Skeleton: namespace enabled version -->

<xsl:stylesheet
   version="1.0"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:axsl="http://www.w3.org/1999/XSL/TransformAlias"
   xmlns:sch="http://www.ascc.net/xml/schematron">
   <!-- Note that this namespace is not version specific.
        This program implements schematron 1.2 with some
        of the extensions for schematron 1.3: namespaces, keys
   -->

<xsl:namespace-alias stylesheet-prefix="axsl" result-prefix="xsl"/>

<!-- Category: top-level-element -->
<xsl:output
   method="xml"
   omit-xml-declaration="no"
   standalone="yes"
   indent="yes" />

<xsl:template match="sch:schema">
   <axsl:stylesheet version="1.0">
      <xsl:for-each select="sch:ns">
         <xsl:attribute name="{concat(@prefix,':dummy-for-xmlns')}"
                        namespace="{@uri}"/>
      </xsl:for-each>
      <xsl:call-template name="process-prolog"/>
      <xsl:apply-templates mode="do-keys" />
      <axsl:template match='/'>
         <xsl:call-template name="process-root">
            <xsl:with-param name="fpi" select="@fpi" />
            <xsl:with-param name="title" select="sch:title" />
            <xsl:with-param name="contents">
               <xsl:apply-templates mode="do-all-patterns" />
            </xsl:with-param>
         </xsl:call-template>
      </axsl:template>
      <xsl:apply-templates />
      <axsl:template match="text()" priority="-1">
         <!-- strip characters -->
      </axsl:template>
   </axsl:stylesheet>
</xsl:template>

<xsl:template match="sch:pattern" mode="do-all-patterns" >
   <xsl:call-template name="process-pattern">
      <xsl:with-param name="name" select="@name" />
      <xsl:with-param name="id"   select="@id" />
      <xsl:with-param name="see"  select="@see" />
      <xsl:with-param name="fpi"  select="@fpi" />
   </xsl:call-template>
   <axsl:apply-templates mode='M{count(preceding-sibling::*)}' />
</xsl:template>

<xsl:template match="sch:pattern">
   <xsl:apply-templates />
   <axsl:template match="text()" priority="-1"
                  mode="M{count(preceding-sibling::*)}">
      <!-- strip characters -->
   </axsl:template>
</xsl:template>

<xsl:template match="sch:rule">
   <axsl:template match='{@context}'
                  priority='{4000 - count(preceding-sibling::*)}'
                  mode='M{count(../preceding-sibling::*)}'>
      <xsl:apply-templates />
    <axsl:apply-templates mode='M{count(../preceding-sibling::*)}'/>
   </axsl:template>
</xsl:template>

<xsl:template match="sch:name" mode="text">
   <axsl:text xml:space="preserve"> </axsl:text>
   <xsl:choose>
      <xsl:when test='@path' >
         <xsl:call-template name="process-name">
            <xsl:with-param name="name" select="'name({@path})'" />
         </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
         <xsl:call-template name="process-name">
            <xsl:with-param name="name" select="'name(.)'" />
         </xsl:call-template>
      </xsl:otherwise>
   </xsl:choose>
   <axsl:text xml:space="preserve"> </axsl:text>
</xsl:template>

<xsl:template match="sch:assert">
   <axsl:choose>
      <axsl:when test='{@test}'/>
      <axsl:otherwise>
         <xsl:call-template name="process-assert">
            <xsl:with-param name="pattern"
                            select="ancestor::sch:pattern/@name" />
            <xsl:with-param name="role"
                            select="@role" />
         </xsl:call-template>
      </axsl:otherwise>
   </axsl:choose>
</xsl:template>


<xsl:template match="sch:report">
   <axsl:if test='{@test}'>
      <xsl:call-template name="process-report">
         <xsl:with-param name="pattern"
                         select="ancestor::sch:pattern/@name" />
         <xsl:with-param name="role" select="@role" />
      </xsl:call-template>
   </axsl:if>
</xsl:template>

<xsl:template match="sch:rule/sch:key" mode="do-keys">
    <axsl:key match="{../@context}" name="{@name}" use="{@path}" />
</xsl:template>

<xsl:template match="text()" priority="-1" mode="do-keys" >
   <!-- strip characters -->
</xsl:template>

<xsl:template match="text()" priority="-1" mode="do-all-patterns">
   <!-- strip characters -->
</xsl:template>

<xsl:template match="text()" priority="-1">
   <!-- strip characters -->
</xsl:template>

<xsl:template match="text()" mode="text">
   <xsl:value-of select="normalize-space(.)" />
</xsl:template>

<!-- ============================================================== -->

<!-- report schema errors -->

<xsl:template match="sch:title|sch:ns|sch:key">
   <xsl:if test="count(*)">
      <xsl:message>
         <xsl:text>Warning: </xsl:text>
         <xsl:value-of select="name(.)" />
         <xsl:text> must not contain any child elements</xsl:text>
      </xsl:message>
   </xsl:if>
</xsl:template>

<xsl:template match="*">
   <xsl:message>
      <xsl:text>Warning: unrecognized element </xsl:text>
      <xsl:value-of select="name(.)" />
   </xsl:message>
</xsl:template>

<xsl:template match="*" mode="text">
   <xsl:message>
      <xsl:text>Warning: unrecognized element </xsl:text>
      <xsl:value-of select="name(.)" />
   </xsl:message>
</xsl:template>


<!-- ============================================================== -->

<!-- Default templates -->

<xsl:template name="process-prolog" />
<!-- no params -->

<xsl:template name="process-root">
   <xsl:param name="contents" />
   <xsl:copy-of select="$contents" />
<!-- additional params: fpi, title -->
</xsl:template>

<xsl:template name="process-pattern" />
<!-- params: name, id, see, fpi -->

<xsl:template name="process-name">
   <xsl:param name="name" />
   <axsl:value-of select="{$name}" />
</xsl:template>

<xsl:template name="process-assert">
   <xsl:param name="pattern" />
   <xsl:param name="role" />
   <xsl:call-template name="process-message">
      <xsl:with-param name="pattern" select="$pattern" />
      <xsl:with-param name="role" select="$role" />
   </xsl:call-template>
</xsl:template>

<xsl:template name="process-report">
   <xsl:param name="pattern" />
   <xsl:param name="role" />
   <xsl:call-template name="process-message">
      <xsl:with-param name="pattern" select="$pattern" />
      <xsl:with-param name="role" select="$role" />
   </xsl:call-template>
</xsl:template>

<xsl:template name="process-message">
<!-- params: pattern, role -->
   <xsl:apply-templates mode="text" />
</xsl:template>


</xsl:stylesheet>
    """,
    }


g_source = {
    "addr-book-1":
    """<?xml version="1.0"?>
<?xml-stylesheet type="text/xml" href="addr_book1.xsl"?>
<!DOCTYPE ADDRBOOK SYSTEM "addr_book.dtd">
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
</ADDRBOOK>
""",

    "old-svg-1":
    """<?xml version="1.0" standalone="yes"?>
<!-- Generated by dotneato version 1.6 (Wed Mar 29 15:22:48 EST 2000)
     For: (nobody) Nobody
     Title: G
     Pages: 1
-->
<svg width="1799pt" height="789pt">
<ellipse  cx="136" cy="783" rx="133" ry="10" style="fill:none;stroke:black" />
<text x="6" y="785" style="font-family:Times;font-size:6.29" >http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#GetEndorsingBoarderRequest</text>
<ellipse  cx="571" cy="752" rx="57" ry="10" style="fill:none;stroke:black" />
<text x="518" y="754" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/message</text>
<g  style="fill:none;stroke:black"><path d="M234 776C320 770 441 762 513 756"/></g>
<polygon  style="fill:black" points="511,758 517,756 511,755 511,758 "/>
<text x="340" y="760" style="font-family:Times;font-size:6.86" >rdf::type</text>
<text x="528" y="816" style="font-family:Times;font-size:6.29" > \'\'GetEndorsingBoarderRequest\'\'</text>
<g  style="fill:none;stroke:black"><path d="M234 790C324 796 451 806 521 811"/></g>
<polygon  style="fill:black" points="519,812 525,811 519,809 519,812 "/>
<text x="299" y="791" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/name</text>
<ellipse  cx="571" cy="783" rx="106" ry="10" style="fill:none;stroke:black" />
<text x="468" y="785" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid3]</text>
<g  style="fill:none;stroke:black"><path d="M270 783C331 783 401 783 459 783"/></g>
<polygon  style="fill:black" points="458,784 464,783 458,782 458,784 "/>
<text x="301" y="781" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/part</text>
<text x="962" y="780" style="font-family:Times;font-size:6.29" > \'\'body\'\'</text>
<g  style="fill:none;stroke:black"><path d="M677 782C773 781 905 779 954 778"/></g>
<polygon  style="fill:black" points="953,779 958,778 953,776 953,779 "/>
<text x="733" y="777" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/name</text>
<text x="933" y="811" style="font-family:Times;font-size:6.29" > \'\'esxsd:GetEndorsingBoarder\'\'</text>
<g  style="fill:none;stroke:black"><path d="M660 789C742 794 861 802 926 806"/></g>
<polygon  style="fill:black" points="925,807 930,806 925,804 925,807 "/>
<text x="730" y="790" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/element</text>
<ellipse  cx="136" cy="695" rx="136" ry="10" style="fill:none;stroke:black" />
<text x="4" y="696" style="font-family:Times;font-size:6.29" >http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#GetEndorsingBoarderResponse</text>
<g  style="fill:none;stroke:black"><path d="M268 697C332 699 400 702 423 705 435 707 422 735 433 739 453 744 482 748 508 750"/></g>
<polygon  style="fill:black" points="508,751 514,751 508,749 508,751 "/>
<text x="340" y="696" style="font-family:Times;font-size:6.86" >rdf::type</text>
<text x="526" y="668" style="font-family:Times;font-size:6.29" > \'\'GetEndorsingBoarderResponse\'\'</text>
<g  style="fill:none;stroke:black"><path d="M225 687C245 685 267 684 282 683 347 678 454 672 517 669"/></g>
<polygon  style="fill:black" points="517,670 523,668 517,668 517,670 "/>
<text x="299" y="672" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/name</text>
<ellipse  cx="571" cy="722" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="467" y="723" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid10]</text>
<g  style="fill:none;stroke:black"><path d="M188 704C219 710 257 715 282 717 329 720 398 721 457 722"/></g>
<polygon  style="fill:black" points="456,723 462,722 456,720 456,723 "/>
<text x="301" y="715" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/part</text>
<text x="962" y="712" style="font-family:Times;font-size:6.29" > \'\'body\'\'</text>
<g  style="fill:none;stroke:black"><path d="M675 719C771 716 905 712 954 711"/></g>
<polygon  style="fill:black" points="953,712 958,711 953,710 953,712 "/>
<text x="733" y="711" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/name</text>
<text x="921" y="743" style="font-family:Times;font-size:6.29" > \'\'esxsd:GetEndorsingBoarderResponse\'\'</text>
<g  style="fill:none;stroke:black"><path d="M667 726C744 730 850 736 914 739"/></g>
<polygon  style="fill:black" points="913,740 918,739 913,737 913,740 "/>
<text x="730" y="726" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/element</text>
<ellipse  cx="571" cy="123" rx="135" ry="10" style="fill:none;stroke:black" />
<text x="440" y="125" style="font-family:Times;font-size:6.29" >http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#GetEndorsingBoarderPortType</text>
<ellipse  cx="974" cy="107" rx="58" ry="10" style="fill:none;stroke:black" />
<text x="920" y="109" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/portType</text>
<g  style="fill:none;stroke:black"><path d="M692 118C764 115 853 112 912 110"/></g>
<polygon  style="fill:black" points="911,111 917,110 911,108 911,111 "/>
<text x="775" y="110" style="font-family:Times;font-size:6.86" >rdf::type</text>
<text x="930" y="140" style="font-family:Times;font-size:6.29" > \'\'GetEndorsingBoarderPortType\'\'</text>
<g  style="fill:none;stroke:black"><path d="M692 127C769 130 863 134 921 137"/></g>
<polygon  style="fill:black" points="921,138 926,137 921,135 921,138 "/>
<text x="733" y="126" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/name</text>
<ellipse  cx="974" cy="169" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="171" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid17]</text>
<g  style="fill:none;stroke:black"><path d="M624 133C655 138 694 143 719 146 763 152 831 158 885 162"/></g>
<polygon  style="fill:black" points="885,163 890,162 885,160 885,163 "/>
<text x="728" y="144" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<ellipse  cx="974" cy="250" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="252" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid21]</text>
<g  style="fill:none;stroke:black"><path d="M602 133C660 152 791 194 865 217 885 223 913 232 936 239"/></g>
<polygon  style="fill:black" points="936,240 941,241 936,237 936,240 "/>
<text x="728" y="169" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<ellipse  cx="974" cy="46" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="47" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid24]</text>
<g  style="fill:none;stroke:black"><path d="M598 113C631 101 685 82 719 75 765 66 835 59 890 53"/></g>
<polygon  style="fill:black" points="890,55 895,53 890,52 890,55 "/>
<text x="728" y="55" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<ellipse  cx="974" cy="77" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="78" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid27]</text>
<g  style="fill:none;stroke:black"><path d="M630 114C668 107 713 101 719 100 764 95 833 89 887 84"/></g>
<polygon  style="fill:black" points="887,86 893,83 887,83 887,86 "/>
<text x="728" y="85" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<text x="1324" y="109" style="font-family:Times;font-size:6.29" > \'\'GetEndorsingBoarder\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1056 162C1066 161 1075 158 1082 156 1093 152 1082 126 1093 124 1153 114 1259 109 1316 108"/></g>
<polygon  style="fill:black" points="1315,109 1321,108 1315,106 1315,109 "/>
<text x="1112" y="110" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/name</text>
<ellipse  cx="1357" cy="294" rx="53" ry="10" style="fill:none;stroke:black" />
<text x="1308" y="296" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/input</text>
<g  style="fill:none;stroke:black"><path d="M1043 258C1119 267 1239 281 1307 289"/></g>
<polygon  style="fill:black" points="1305,290 1311,289 1305,287 1305,290 "/>
<text x="1153" y="262" style="font-family:Times;font-size:6.86" >rdf::type</text>
<ellipse  cx="1357" cy="253" rx="90" ry="10" style="fill:none;stroke:black" />
<text x="1271" y="254" style="font-family:Times;font-size:6.29" >http://uche.ogbuji.net/articles/wsdlrdf/GetEndorsingBoarderRequest</text>
<g  style="fill:none;stroke:black"><path d="M1082 251C1139 252 1207 252 1261 252"/></g>
<polygon  style="fill:black" points="1261,253 1267,252 1261,250 1261,253 "/>
<text x="1108" y="249" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/message</text>
<ellipse  cx="1357" cy="149" rx="54" ry="10" style="fill:none;stroke:black" />
<text x="1307" y="151" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/output</text>
<g  style="fill:none;stroke:black"><path d="M1065 51C1072 53 1077 55 1082 59 1103 75 1069 128 1093 136 1121 145 1227 148 1296 149"/></g>
<polygon  style="fill:black" points="1296,150 1302,149 1296,147 1296,150 "/>
<text x="1153" y="134" style="font-family:Times;font-size:6.86" >rdf::type</text>
<ellipse  cx="1357" cy="46" rx="92" ry="10" style="fill:none;stroke:black" />
<text x="1269" y="47" style="font-family:Times;font-size:6.29" >http://uche.ogbuji.net/articles/wsdlrdf/GetEndorsingBoarderResponse</text>
<g  style="fill:none;stroke:black"><path d="M1082 46C1138 46 1205 46 1259 46"/></g>
<polygon  style="fill:black" points="1259,47 1264,46 1259,44 1259,47 "/>
<text x="1108" y="43" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/message</text>
<ellipse  cx="1357" cy="222" rx="52" ry="10" style="fill:none;stroke:black" />
<text x="1309" y="224" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/fault</text>
<g  style="fill:none;stroke:black"><path d="M1070 81C1074 83 1079 86 1082 90 1096 106 1075 201 1093 210 1107 217 1227 220 1300 221"/></g>
<polygon  style="fill:black" points="1299,222 1304,221 1299,220 1299,222 "/>
<text x="1153" y="208" style="font-family:Times;font-size:6.86" >rdf::type</text>
<ellipse  cx="1357" cy="77" rx="86" ry="10" style="fill:none;stroke:black" />
<text x="1275" y="78" style="font-family:Times;font-size:6.29" >http://uche.ogbuji.net/articles/wsdlrdf/GetEndorsingBoarderFault</text>
<g  style="fill:none;stroke:black"><path d="M1082 77C1140 77 1210 77 1265 77"/></g>
<polygon  style="fill:black" points="1264,78 1270,77 1264,75 1264,78 "/>
<text x="1108" y="74" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/message</text>
<ellipse  cx="571" cy="400" rx="137" ry="10" style="fill:none;stroke:black" />
<text x="437" y="402" style="font-family:Times;font-size:6.29" >http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#EndorsementSearchSoapBinding</text>
<ellipse  cx="974" cy="543" rx="56" ry="10" style="fill:none;stroke:black" />
<text x="922" y="544" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/binding</text>
<g  style="fill:none;stroke:black"><path d="M583 411C619 437 672 437 709 464 721 472 706 501 719 506 765 525 817 522 865 529 881 531 902 534 922 536"/></g>
<polygon  style="fill:black" points="920,537 926,537 920,535 920,537 "/>
<text x="775" y="504" style="font-family:Times;font-size:6.86" >rdf::type</text>
<text x="928" y="340" style="font-family:Times;font-size:6.29" > \'\'EndorsementSearchSoapBinding\'\'</text>
<g  style="fill:none;stroke:black"><path d="M610 391C643 382 690 371 719 366 773 358 861 349 919 344"/></g>
<polygon  style="fill:black" points="918,345 924,343 918,342 918,345 "/>
<text x="733" y="348" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/name</text>
<text x="926" y="371" style="font-family:Times;font-size:6.29" > \'\'es:GetEndorsingBoarderPortType\'\'</text>
<g  style="fill:none;stroke:black"><path d="M667 393C746 387 854 379 919 373"/></g>
<polygon  style="fill:black" points="917,375 923,373 917,372 917,375 "/>
<text x="735" y="376" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/type</text>
<ellipse  cx="974" cy="431" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="433" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid33]</text>
<g  style="fill:none;stroke:black"><path d="M667 408C733 413 819 419 883 424"/></g>
<polygon  style="fill:black" points="883,425 889,425 883,423 883,425 "/>
<text x="723" y="409" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/binding</text>
<ellipse  cx="974" cy="472" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="474" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid38]</text>
<g  style="fill:none;stroke:black"><path d="M610 410C643 419 689 429 719 435 769 444 849 455 906 463"/></g>
<polygon  style="fill:black" points="906,464 912,464 906,461 906,464 "/>
<text x="728" y="432" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<ellipse  cx="974" cy="512" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="513" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid42]</text>
<g  style="fill:none;stroke:black"><path d="M590 411C620 427 681 457 719 468 768 481 848 495 905 503"/></g>
<polygon  style="fill:black" points="905,504 910,503 905,501 905,504 "/>
<text x="728" y="465" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<ellipse  cx="974" cy="400" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="402" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid45]</text>
<g  style="fill:none;stroke:black"><path d="M709 400C758 400 813 400 861 400"/></g>
<polygon  style="fill:black" points="859,401 865,400 859,399 859,401 "/>
<text x="728" y="398" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<ellipse  cx="974" cy="200" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="202" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid52]</text>
<g  style="fill:none;stroke:black"><path d="M587 390C616 370 681 329 719 308 767 281 815 255 865 233 883 226 910 218 933 211"/></g>
<polygon  style="fill:black" points="933,213 938,210 932,210 933,213 "/>
<text x="728" y="236" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<ellipse  cx="974" cy="308" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="870" y="309" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid59]</text>
<g  style="fill:none;stroke:black"><path d="M591 390C622 375 682 347 719 338 763 329 833 320 887 315"/></g>
<polygon  style="fill:black" points="887,317 893,314 887,314 887,317 "/>
<text x="728" y="317" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/operation</text>
<text x="1340" y="421" style="font-family:Times;font-size:6.29" > \'\'document\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1077 428C1164 425 1281 422 1332 420"/></g>
<polygon  style="fill:black" points="1331,421 1336,420 1331,419 1331,421 "/>
<text x="1105" y="421" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/style</text>
<text x="1305" y="452" style="font-family:Times;font-size:6.29" > \'\'http://schemas.xmlsoap.org/soap/http\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1058 437C1070 439 1083 439 1093 440 1148 443 1237 447 1296 448"/></g>
<polygon  style="fill:black" points="1296,449 1301,448 1296,447 1296,449 "/>
<text x="1100" y="437" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/transport</text>
<text x="1324" y="483" style="font-family:Times;font-size:6.29" > \'\'GetEndorsingBoarder\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1079 475C1157 477 1260 479 1316 480"/></g>
<polygon  style="fill:black" points="1315,481 1321,480 1315,479 1315,481 "/>
<text x="1152" y="473" style="font-family:Times;font-size:6.86" >rdf::about</text>
<ellipse  cx="1357" cy="512" rx="65" ry="10" style="fill:none;stroke:black" />
<text x="1296" y="514" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/soap/operation</text>
<g  style="fill:none;stroke:black"><path d="M1082 512C1148 512 1229 512 1286 512"/></g>
<polygon  style="fill:black" points="1285,513 1291,512 1285,511 1285,513 "/>
<text x="1153" y="510" style="font-family:Times;font-size:6.86" >rdf::type</text>
<text x="1285" y="545" style="font-family:Times;font-size:6.29" > \'\'http://www.snowboard-info.com/EndorsementSearch\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1043 520C1061 521 1079 523 1093 524 1142 528 1219 533 1276 537"/></g>
<polygon  style="fill:black" points="1276,539 1281,538 1276,536 1276,539 "/>
<text x="1096" y="522" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/soapAction</text>
<g  style="fill:none;stroke:black"><path d="M1039 392C1062 389 1082 387 1082 387 1086 386 1089 382 1093 381 1141 369 1192 365 1238 346 1247 343 1240 323 1248 319 1264 312 1289 306 1311 302"/></g>
<polygon  style="fill:black" points="1310,304 1316,301 1310,301 1310,304 "/>
<text x="1153" y="344" style="font-family:Times;font-size:6.86" >rdf::type</text>
<ellipse  cx="1357" cy="389" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="1253" y="391" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid46]</text>
<g  style="fill:none;stroke:black"><path d="M1077 397C1131 396 1195 394 1248 392"/></g>
<polygon  style="fill:black" points="1248,393 1253,392 1248,391 1248,393 "/>
<text x="1105" y="391" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/body</text>
<text x="1703" y="385" style="font-family:Times;font-size:6.29" > \'\'literal\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1464 387C1547 386 1653 385 1695 384"/></g>
<polygon  style="fill:black" points="1694,385 1699,384 1694,382 1694,385 "/>
<text x="1490" y="383" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/use</text>
<text x="1634" y="416" style="font-family:Times;font-size:6.29" > \'\'http://schemas.snowboard-info.com/EndorsementSearch.xsd\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1432 396C1448 398 1464 399 1476 400 1516 403 1577 407 1626 409"/></g>
<polygon  style="fill:black" points="1625,411 1630,410 1625,408 1625,411 "/>
<text x="1479" y="397" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/namespace</text>
<g  style="fill:none;stroke:black"><path d="M1039 192C1062 189 1082 186 1082 186 1086 186 1089 182 1093 182 1151 174 1247 162 1305 156"/></g>
<polygon  style="fill:black" points="1305,157 1311,155 1305,154 1305,157 "/>
<text x="1153" y="162" style="font-family:Times;font-size:6.86" >rdf::type</text>
<ellipse  cx="1357" cy="191" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="1253" y="193" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid53]</text>
<g  style="fill:none;stroke:black"><path d="M1079 198C1131 197 1194 195 1247 194"/></g>
<polygon  style="fill:black" points="1246,195 1252,194 1246,192 1246,195 "/>
<text x="1105" y="192" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/body</text>
<text x="1703" y="177" style="font-family:Times;font-size:6.29" > \'\'literal\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1456 187C1539 184 1651 178 1695 176"/></g>
<polygon  style="fill:black" points="1694,177 1699,176 1694,174 1694,177 "/>
<text x="1490" y="178" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/use</text>
<text x="1634" y="208" style="font-family:Times;font-size:6.29" > \'\'http://schemas.snowboard-info.com/EndorsementSearch.xsd\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1445 197C1456 198 1467 198 1476 198 1516 201 1577 202 1626 204"/></g>
<polygon  style="fill:black" points="1625,205 1630,204 1625,202 1625,205 "/>
<text x="1479" y="196" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/namespace</text>
<g  style="fill:none;stroke:black"><path d="M1082 309C1136 308 1197 304 1238 293 1257 289 1232 246 1248 236 1261 228 1281 225 1300 223"/></g>
<polygon  style="fill:black" points="1299,225 1304,222 1299,222 1299,225 "/>
<text x="1153" y="291" style="font-family:Times;font-size:6.86" >rdf::type</text>
<ellipse  cx="1357" cy="336" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="1253" y="338" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid60]</text>
<g  style="fill:none;stroke:black"><path d="M1043 316C1058 317 1072 320 1082 321 1087 322 1089 330 1093 330 1133 332 1193 334 1245 335"/></g>
<polygon  style="fill:black" points="1244,336 1249,335 1244,333 1244,336 "/>
<text x="1105" y="328" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/body</text>
<text x="1703" y="318" style="font-family:Times;font-size:6.29" > \'\'literal\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1451 331C1534 326 1650 320 1695 317"/></g>
<polygon  style="fill:black" points="1694,318 1699,317 1694,315 1694,318 "/>
<text x="1490" y="320" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/use</text>
<text x="1634" y="349" style="font-family:Times;font-size:6.29" > \'\'http://schemas.snowboard-info.com/EndorsementSearch.xsd\'\'</text>
<g  style="fill:none;stroke:black"><path d="M1460 339C1512 341 1575 343 1626 344"/></g>
<polygon  style="fill:black" points="1625,345 1630,344 1625,342 1625,345 "/>
<text x="1479" y="338" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/namespace</text>
<ellipse  cx="136" cy="557" rx="130" ry="10" style="fill:none;stroke:black" />
<text x="9" y="559" style="font-family:Times;font-size:6.29" >http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#EndorsementSearchService</text>
<ellipse  cx="571" cy="481" rx="55" ry="10" style="fill:none;stroke:black" />
<text x="520" y="483" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/service</text>
<g  style="fill:none;stroke:black"><path d="M164 547C197 536 249 519 282 512 332 501 383 500 433 495 456 492 490 489 518 487"/></g>
<polygon  style="fill:black" points="516,488 522,486 516,485 516,488 "/>
<text x="340" y="493" style="font-family:Times;font-size:6.86" >rdf::type</text>
<text x="531" y="513" style="font-family:Times;font-size:6.29" > \'\'EndorsementSearchService\'\'</text>
<g  style="fill:none;stroke:black"><path d="M197 548C234 543 276 537 282 536 348 529 459 520 522 516"/></g>
<polygon  style="fill:black" points="522,517 528,515 522,515 522,517 "/>
<text x="299" y="521" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/name</text>
<text x="508" y="544" style="font-family:Times;font-size:6.29" > \'\'snowboarding-info.com Endorsement Service\'\'</text>
<g  style="fill:none;stroke:black"><path d="M256 553C335 551 435 547 501 545"/></g>
<polygon  style="fill:black" points="499,546 505,545 499,543 499,546 "/>
<text x="286" y="545" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/documentation</text>
<ellipse  cx="571" cy="604" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="467" y="606" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid69]</text>
<g  style="fill:none;stroke:black"><path d="M187 567C218 572 257 579 282 581 333 588 413 593 476 598"/></g>
<polygon  style="fill:black" points="476,599 482,599 476,597 476,599 "/>
<text x="301" y="579" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/port</text>
<ellipse  cx="571" cy="573" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="467" y="575" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid73]</text>
<g  style="fill:none;stroke:black"><path d="M244 563C258 564 271 564 282 565 329 567 400 569 460 571"/></g>
<polygon  style="fill:black" points="460,572 466,571 460,569 460,572 "/>
<text x="301" y="563" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/port</text>
<ellipse  cx="571" cy="635" rx="108" ry="10" style="fill:none;stroke:black" />
<text x="467" y="637" style="font-family:Times;font-size:6.29" >[http://uche.ogbuji.net/articles/wsdlrdf/endorsingsnowboarderservice.rdf#genid76]</text>
<g  style="fill:none;stroke:black"><path d="M162 568C194 580 249 599 282 606 332 616 383 616 433 622 448 623 470 625 490 627"/></g>
<polygon  style="fill:black" points="489,628 495,628 489,626 489,628 "/>
<text x="301" y="603" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/port</text>
<text x="936" y="606" style="font-family:Times;font-size:6.29" > \'\'GetEndorsingBoarderPort\'\'</text>
<g  style="fill:none;stroke:black"><path d="M679 604C761 604 867 604 928 604"/></g>
<polygon  style="fill:black" points="927,606 933,604 927,603 927,606 "/>
<text x="773" y="602" style="font-family:Times;font-size:6.86" >rdf::about</text>
<g  style="fill:none;stroke:black"><path d="M655 567C734 561 850 552 918 547"/></g>
<polygon  style="fill:black" points="916,549 922,547 916,546 916,549 "/>
<text x="775" y="549" style="font-family:Times;font-size:6.86" >rdf::type</text>
<text x="928" y="575" style="font-family:Times;font-size:6.29" > \'\'EndorsementSearchSoapBinding\'\'</text>
<g  style="fill:none;stroke:black"><path d="M679 573C757 573 857 573 918 573"/></g>
<polygon  style="fill:black" points="918,575 924,573 918,572 918,575 "/>
<text x="769" y="571" style="font-family:Times;font-size:6.86" >rdf::resource</text>
<ellipse  cx="974" cy="635" rx="62" ry="10" style="fill:none;stroke:black" />
<text x="916" y="637" style="font-family:Times;font-size:6.29" >http://schemas.xmlsoap.org/wsdl/soap/address</text>
<g  style="fill:none;stroke:black"><path d="M679 635C751 635 843 635 905 635"/></g>
<polygon  style="fill:black" points="905,636 911,635 905,634 905,636 "/>
<text x="775" y="633" style="font-family:Times;font-size:6.86" >rdf::type</text>
<text x="902" y="668" style="font-family:Times;font-size:6.29" > \'\'http://www.snowboard-info.com/EndorsementSearch\'\'</text>
<g  style="fill:none;stroke:black"><path d="M655 642C726 647 826 655 894 660"/></g>
<polygon  style="fill:black" points="893,661 898,660 893,658 893,661 "/>
<text x="722" y="644" style="font-family:Times;font-size:6.86" >http://schemas.xmlsoap.org/wsdl/soap/location</text>
</svg>
""",
}


if __name__ == '__main__':
    Test()

