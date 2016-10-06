#Glenn Gasmen's struggle with recursive modes

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  xmlns:ot='http://namespaces.opentechnology.org/talk'
  xmlns:dc='http://purl.org/metadata/dublin_core'
  extension-element-prefixes='ft'
  version="1.0"
>
  <xsl:output method="html" encoding="ISO-8859-1"/>
  <xsl:param name='user-mode' select='"full-story"'/>

  <xsl:template match="/">
  <HTML><HEAD><TITLE>Test Skin</TITLE></HEAD><BODY>
    <ft:apply-templates mode='{$user-mode}'/>
  </BODY></HTML>
  </xsl:template>

  <xsl:template match="ot:story" mode="front-page">

   <DIV ALIGN="CENTER">

    <DIV ALIGN="CENTER">
       <xsl:value-of select="dc:title"/>
    </DIV>

    <TABLE WIDTH="100%" BORDER="0">
      <TR>
        <TD ALIGN="LEFT" WIDTH="33%">
          <xsl:value-of select="dc:creator"/>
        </TD>
        <TD ALIGN="CENTER" WIDTH="33%">
          <xsl:value-of select="dc:datetime"/>
        </TD>
        <TD ALIGN="RIGHT" WIDTH="33%">
          <xsl:value-of select="ot:link"/>
        </TD>
      </TR>
    </TABLE>

    <DIV ALIGN="JUSTIFY">
        <xsl:apply-templates select="dc:description"/>
    </DIV>
   </DIV>

  </xsl:template>

  <xsl:template match="ot:story" mode="full-story">

    <DIV ALIGN="CENTER">
       <xsl:value-of select="dc:title"/>
    </DIV>

    <TABLE WIDTH="100%" BORDER="0">
      <TR>
        <TD ALIGN="LEFT" WIDTH="50%">
          <xsl:value-of select="dc:creator"/>
        </TD>
        <TD ALIGN="RIGHT" WIDTH="50%">
          <xsl:value-of select="dc:datetime"/>
        </TD>
      </TR>
    </TABLE>

    <DIV ALIGN="JUSTIFY">
       <xsl:apply-templates select="dc:content"/>
       <BR/><BR/>
    </DIV>

    <DIV ALIGN="JUSTIFY">
       <xsl:apply-templates select="dc:description"/>
       <BR/><BR/>
    </DIV>

  </xsl:template>

  <xsl:template match="ot:comment">
    <DIV ALIGN="JUSTIFY">
     <xsl:for-each select="dc:title"/>
    </DIV>
  </xsl:template>

</xsl:stylesheet>
"""


source_1 = """<result-set>
<!--
Notes:
* All elements in the valid dublic core meta-data 1.0  element set are
in the dc namespace.  All other metadata are in the ot namespace.
* for info on Dublin Core, see
http://purl.org/DC/documents/rec-dces-19990702.htm and
http://purl.org/dc/documents/rec/dcmes-qualifiers-20000711.htm
-->

<ot:story
  id='urn:uuid:this-is-bogus-uuid-1'
  xmlns:ot='http://namespaces.opentechnology.org/talk'
  xmlns:dc='http://purl.org/metadata/dublin_core'
  xmlns='http://docbook.org/docbook/xml/4.0/namespace'
>
  <dc:creator ot:id='urn:uuid:this-is-bogus-uuid-2' ot:name='Xavier
  Markus Langley'/>
  <dc:creator>Plagerized</dc:creator>
  <dc:subject>Test Data</dc:subject>
  <dc:datetime>2003-02-30 13:59:23-07:00</dc:datetime>
  <dc:title>Privacy, Part Two: Unwanted Gaze</dc:title>
  <dc:content>
This is an example content:
A growing number of lawyers and scholars, including Rosen, say they now
believe that fundamental changes in Net architecture are necessary to
protect constitutional values and restore the notion of the "inviolate
personality" to the private lives of Americans. These would include
copyright management systems to protect the right to read anonymously,
permitting individuals to pay with untraceable digital cash; prohibiting
the collection and disclosure of identifying information without the
reader's knowledge, or using digital certificates to create psudonymous
downloading.

To Rosen, author of Gaze, cyberspace is posing a greater menace to
privacy by the day. He details the l998 forced resignation of Harvard
Divinity School dean Ronald F. Thiemann, who downloaded pornography onto
his university-owned home computer. A Harvard technician installing a
computer with more memory at the dean's residence was transferring files
from the old computer to the new one and noticed thousands of
pornographic pictures. Although none of the pictures appeared to involve
minors, the technician told his supervisor. University administrators
asked the dean to step down.

Harvard justified its decision by claiming that Divinity School rules
prohibited personal use of university computers in any way that clashed
with its educational mission. But the dean was using his computer at
home, not work. And no student or colleague suggested he had improperly
behaved in any way as head of the Divinity School. His work was never
questioned. It's ludicrous to suggest that the school would have fired
him if he'd been downloading sports scores or bidding for furniture on
eBay. But although he'd committed no crime and performed well in his
job, he was forced out in disgrace, while his intimate communications
were discussed in public.


Should free citizens in a democratic society have to spend money for
"nyms" to preserve the privacy they ought to be -- and once were --
accorded in law? How many millions of computer users will even know of
this new technology, or have the money to use it?  Rosen's implication
is that even if software caused the problem, then software will clean
up.

His assurances seem a bit "gee-whiz." But to ignore them cynically on
that basis, or to trust them completely, ignores the history of
technology. What people can create, others can and will undo. Technology
that can be used will be used. In an otherwise powerful book, he also
glosses over powerful incentives for eliminating privacy in cyberspace.
First, the megacorporations dominating media, business and government
will continue to aggressively explore ways of tracking potential
customers as Net use grows. Secondly, law enforcement agencies like the
FBI have been fighting for decades for the right to deploy tracking
programs like "Carnivore" (see part one) and are hardly likely to back
off.

  </dc:content>
  <dc:description>
     This is an example of a description:
     Can pseudonymous downloading, "snoop-proof" e-mail, digital pseuds called
     "nyms," PDA-like machines, allegedly untraceable digi-cash and other
     changes in software and the architecture of cyberspace, restore some
     privacy and restore the idea of the "Inviolate Personality?" Part Two
     in a series based on Jeffrey Rosen's new book, "The Unwanted Gaze: The
     Destruction of Privacy in America."
  </dc:description>
</ot:story>

<ot:story
  id='urn:uuid:this-is-bogus-uuid-1'
  xmlns:ot='http://namespaces.opentechnology.org/talk'
  xmlns:dc='http://purl.org/metadata/dublin_core'
>
  <dc:creator ot:id='urn:uuid:this-is-bogus-uuid-2' ot:name='Xavier
  Markus Langley'/>
   <dc:subject>4Suite</dc:subject>
  <dc:subject>Release</dc:subject>
  <dc:subject>XSLT</dc:subject>
  <dc:subject>DOM</dc:subject>
  <dc:subject>XPath</dc:subject>
  <dc:subject>RDF</dc:subject>
  <dc:subject>Object Databases</dc:subject>
  <dc:datetime>2003-11-19 13:59:23-07:00</dc:datetime>
  <dc:title>4Suite 5.3.8 Released</dc:title>
  <!--
Note that 4Suite is also marked as a keyword in the content.  This is
fine.  The final keywords are a union of all the dc:subject children of
ot:story and dc:content.
  -->
  <dc:content><ot:source>Fourthought, Inc.</ot:source> today announced
  the latest version of their XML middleware suite,
  <dc:subject>4Suite</dc:subject>.  This latest version adds support for
  the latest <dc:subject>XSLT</dc:subject> 2.3 Recommendation and
  <dc:subject>DOM</dc:subject> Level 7.
  </dc:content>
  <dc:description>
     Can pseudonymous downloading, "snoop-proof" e-mail, digital pseuds
     called "nyms," PDA-like machines, allegedly untraceable digi-cash
     and other changes in software and the architecture of cyberspace,
     restore some privacy and restore the idea of the "Inviolate
     Personality?" Part Two in a series based on Jeffrey Rosen's new
     book, "The Unwanted Gaze: The Destruction of Privacy in America."
  </dc:description>
</ot:story>

</result-set>
"""

expected_1 = """<HTML xmlns:ot="http://namespaces.opentechnology.org/talk" xmlns:dc="http://purl.org/metadata/dublin_core">\n  <HEAD>\n    <meta content="text/html; charset=ISO-8859-1" http-equiv="Content-Type">\n    <TITLE>Test Skin</TITLE>\n  </HEAD>\n  <BODY>\n\n\n\n    <DIV ALIGN="CENTER">Privacy, Part Two: Unwanted Gaze</DIV>\n    <TABLE WIDTH="100%" BORDER="0">\n      <TR>\n        <TD WIDTH="50%" ALIGN="LEFT"></TD>\n        <TD WIDTH="50%" ALIGN="RIGHT">2003-02-30 13:59:23-07:00</TD>\n      </TR>\n    </TABLE>\n    <DIV ALIGN="JUSTIFY">\nThis is an example content:\nA growing number of lawyers and scholars, including Rosen, say they now\nbelieve that fundamental changes in Net architecture are necessary to\nprotect constitutional values and restore the notion of the "inviolate\npersonality" to the private lives of Americans. These would include\ncopyright management systems to protect the right to read anonymously,\npermitting individuals to pay with untraceable digital cash; prohibiting\nthe collection and disclosure of identifying information without the\nreader's knowledge, or using digital certificates to create psudonymous\ndownloading.\n\nTo Rosen, author of Gaze, cyberspace is posing a greater menace to\nprivacy by the day. He details the l998 forced resignation of Harvard\nDivinity School dean Ronald F. Thiemann, who downloaded pornography onto\nhis university-owned home computer. A Harvard technician installing a\ncomputer with more memory at the dean's residence was transferring files\nfrom the old computer to the new one and noticed thousands of\npornographic pictures. Although none of the pictures appeared to involve\nminors, the technician told his supervisor. University administrators\nasked the dean to step down.\n\nHarvard justified its decision by claiming that Divinity School rules\nprohibited personal use of university computers in any way that clashed\nwith its educational mission. But the dean was using his computer at\nhome, not work. And no student or colleague suggested he had improperly\nbehaved in any way as head of the Divinity School. His work was never\nquestioned. It's ludicrous to suggest that the school would have fired\nhim if he'd been downloading sports scores or bidding for furniture on\neBay. But although he'd committed no crime and performed well in his\njob, he was forced out in disgrace, while his intimate communications\nwere discussed in public.\n\n\nShould free citizens in a democratic society have to spend money for\n"nyms" to preserve the privacy they ought to be -- and once were --\naccorded in law? How many millions of computer users will even know of\nthis new technology, or have the money to use it?  Rosen's implication\nis that even if software caused the problem, then software will clean\nup.\n\nHis assurances seem a bit "gee-whiz." But to ignore them cynically on\nthat basis, or to trust them completely, ignores the history of\ntechnology. What people can create, others can and will undo. Technology\nthat can be used will be used. In an otherwise powerful book, he also\nglosses over powerful incentives for eliminating privacy in cyberspace.\nFirst, the megacorporations dominating media, business and government\nwill continue to aggressively explore ways of tracking potential\ncustomers as Net use grows. Secondly, law enforcement agencies like the\nFBI have been fighting for decades for the right to deploy tracking\nprograms like "Carnivore" (see part one) and are hardly likely to back\noff.\n\n  \n<BR>\n      <BR>\n    </DIV>\n    <DIV ALIGN="JUSTIFY">\n     This is an example of a description:\n     Can pseudonymous downloading, "snoop-proof" e-mail, digital pseuds called\n     "nyms," PDA-like machines, allegedly untraceable digi-cash and other\n     changes in software and the architecture of cyberspace, restore some\n     privacy and restore the idea of the "Inviolate Personality?" Part Two\n     in a series based on Jeffrey Rosen's new book, "The Unwanted Gaze: The\n     Destruction of Privacy in America."\n  \n      <BR>\n      <BR>\n    </DIV>\n\n\n    <DIV ALIGN="CENTER">4Suite 5.3.8 Released</DIV>\n    <TABLE WIDTH="100%" BORDER="0">\n      <TR>\n        <TD WIDTH="50%" ALIGN="LEFT"></TD>\n        <TD WIDTH="50%" ALIGN="RIGHT">2003-11-19 13:59:23-07:00</TD>\n      </TR>\n    </TABLE>\n    <DIV ALIGN="JUSTIFY">Fourthought, Inc. today announced\n  the latest version of their XML middleware suite,\n  4Suite.  This latest version adds support for\n  the latest XSLT 2.3 Recommendation and\n  DOM Level 7.\n  \n      <BR>\n      <BR>\n    </DIV>\n    <DIV ALIGN="JUSTIFY">\n     Can pseudonymous downloading, "snoop-proof" e-mail, digital pseuds\n     called "nyms," PDA-like machines, allegedly untraceable digi-cash\n     and other changes in software and the architecture of cyberspace,\n     restore some privacy and restore the idea of the "Inviolate\n     Personality?" Part Two in a series based on Jeffrey Rosen's new\n     book, "The Unwanted Gaze: The Destruction of Privacy in America."\n  \n      <BR>\n      <BR>\n    </DIV>\n\n\n  </BODY>\n</HTML>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return

