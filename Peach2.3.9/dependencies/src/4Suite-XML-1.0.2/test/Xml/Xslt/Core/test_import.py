from Ft.Xml.Xslt import Error

from Xml.Xslt import test_harness

#=======================================================================
# FIXME: These first 2 tests use addr_book1.xml as their source doc.
# That file contains an outdated xml-stylesheet PI pointing to
# addr_book1.xsl with the media type text/xml. If the media type is
# changed back to one that we support, then it may affect the import
# tree.
#=======================================================================

#-----------------------------------------------------------------------
# xsl:import has to come before all other top-level instructions.
#
sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:variable name='spam' select='"original"'/>
  <xsl:import href='Xml/Xslt/Core/addr_book3.xsl'/>

</xsl:stylesheet>
"""

#-----------------------------------------------------------------------
# A top-level variable defined in the importing stylesheet
# should override the definition in the importing stylesheet.
#
sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:import href='Xml/Xslt/Core/addr_book3.xsl'/>
  <xsl:variable name='spam' select='"original"'/>

</xsl:stylesheet>
"""

expected_2 = """<HTML>
  <HEAD>
    <META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>ADDRBOOK from imported: original</TABLE>
  </BODY>
</HTML>"""

#-----------------------------------------------------------------------
# A stylesheet cannot import itself directly.
#
STY_CIRC = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="self-import.xsl"/>

</xsl:stylesheet>"""

#-----------------------------------------------------------------------
# A stylesheet cannot import itself indirectly.
#
STY_CIRC_A = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="circ-B.xsl"/>

</xsl:stylesheet>"""

STY_CIRC_B = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="circ-A.xsl"/>

</xsl:stylesheet>"""

#-----------------------------------------------------------------------
# The same stylesheet can be imported twice.
# (the 2nd is at a lower precedence than the first)

STY_DUP_IMPORT = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="identity.xsl"/>
  <xsl:import href="identity.xsl"/>

</xsl:stylesheet>"""

#-----------------------------------------------------------------------
# The same stylesheet can be imported twice.
# (indirect example from the spec)
#
# B imports A: OK
# C imports A: OK
# D imports B: OK
# D imports C: OK because even though A is imported twice,
#              it doesn't import itself indirectly

STY_A = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- this is stylesheet A -->
  <xsl:output method="text"/>
  <xsl:template match="/">hello world</xsl:template>

</xsl:stylesheet>"""

STY_B = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- this is stylesheet B -->
  <xsl:include href="A.xsl"/>

</xsl:stylesheet>"""

STY_C = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- this is stylesheet C -->
  <xsl:include href="A.xsl"/>

</xsl:stylesheet>"""

STY_D = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- this is stylesheet D -->
  <xsl:include href="B.xsl"/>
  <xsl:include href="C.xsl"/>

</xsl:stylesheet>"""

STY_IDENTITY = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>"""

DUMMY_XML = """<?xml version="1.0" encoding="utf-8"?><dummy/>"""

def Test(tester):

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sty = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sty], None,
                          exceptionCode=Error.ILLEGAL_IMPORT,
                          title="xsl:import in wrong spot")

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sty = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sty], expected_2,
                          title="top-level variable overrides imported one")

    styfactory = test_harness.GetMappingFactory({
        'self-import.xsl' : STY_CIRC,
        'circ-A.xsl' : STY_CIRC_A,
        'circ-B.xsl' : STY_CIRC_B,
        'dup-import.xsl' : STY_DUP_IMPORT,
        'identity.xsl' : STY_IDENTITY,
        'A.xsl' : STY_A,
        'B.xsl' : STY_B,
        'C.xsl' : STY_C,
        'D.xsl' : STY_D,
        })

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri='self-import.xsl')
    test_harness.XsltTest(tester, source, [sty], None,
                          title='circular xsl:import (direct)',
                          exceptionCode=Error.CIRCULAR_INCLUDE,
                          stylesheetInputFactory=styfactory)

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri='circ-A.xsl')
    test_harness.XsltTest(tester, source, [sty], None,
                          title='circular xsl:import (indirect)',
                          exceptionCode=Error.CIRCULAR_INCLUDE,
                          stylesheetInputFactory=styfactory)

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri='dup-import.xsl')
    test_harness.XsltTest(tester, source, [sty], DUMMY_XML,
                          title='non-circular duplicate import (direct)',
                          stylesheetInputFactory=styfactory)

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri='D.xsl')
    test_harness.XsltTest(tester, source, [sty], 'hello world',
                          title='non-circular duplicate import (indirect)',
                          stylesheetInputFactory=styfactory)

    # appending the same stylesheet twice shouldn't be a problem;
    # it's equivalent to a non-circular duplicate import (direct)
    source = test_harness.FileInfo(string=DUMMY_XML)
    sty1 = test_harness.FileInfo(uri='identity.xsl')
    sty2 = test_harness.FileInfo(uri='identity.xsl')
    test_harness.XsltTest(tester, source, [sty1, sty2], DUMMY_XML,
                          title='duplicate stylesheet append via processor',
                          stylesheetInputFactory=styfactory)
    return
