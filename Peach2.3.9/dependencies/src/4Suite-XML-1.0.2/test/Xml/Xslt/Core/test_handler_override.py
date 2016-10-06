#Test the overidding of the processor handlers
#This will also test baseUri resolution for includes, imports and documents (some see test_baseUris for more testing)

from Xml.Xslt import test_harness

import urlparse, cStringIO
from Ft.Lib import Uri
from Ft.Xml import InputSource

doc1 = """<?xml version='1.0' encoding='UTF-8'?>
<root>DOC1</root>"""

doc2 = """<?xml version='1.0' encoding='UTF-8'?>
<root>DOC2</root>"""

style1 = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
  <xsl:template match='/root'>
    <xsl:text>STY1</xsl:text>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>"""

style2 = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
  <xsl:include href='STY1'/>
  <xsl:template match='/root'>
    <xsl:text>STY2</xsl:text>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>"""

style3 = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
  <xsl:import href='STY1'/>
  <xsl:template match='/root'>
    <xsl:text>STY3</xsl:text>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>"""

style4 = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
  <xsl:template match='/root'>
    <xsl:text>STY4</xsl:text>
    <xsl:value-of select='document("DOC2")/root'/>
  </xsl:template>
</xsl:stylesheet>"""

BASE_URI = "http://foo.com/"

URIS={BASE_URI + 'DOC1' : doc1,
      BASE_URI + 'DOC2' : doc2,
      BASE_URI + 'STY1' : style1,
      BASE_URI + 'STY2' : style2,
      BASE_URI + 'STY3' : style3,
      BASE_URI + 'STY4' : style4,
      }


class GenericInputSource(InputSource.InputSource):

    def _openStream(self, uri, ignoreErrors=False, hint=None):
        scheme = urlparse.urlparse(uri)[0]
        #if scheme in ['', 'http', 'ftp', 'file', 'gopher']:
        #    raise uri
        st = URIS[uri]
        return cStringIO.StringIO(st)

InputSourceFactory = InputSource.InputSourceFactory(GenericInputSource)


DOC1_STY1_EXPECTED="""<?xml version="1.0" encoding="UTF-8"?>
STY1DOC1"""

DOC1_STY2_EXPECTED="""<?xml version="1.0" encoding="UTF-8"?>
STY2DOC1"""

DOC1_STY3_EXPECTED="""<?xml version="1.0" encoding="UTF-8"?>
STY3DOC1"""

DOC1_STY4_EXPECTED="""<?xml version="1.0" encoding="UTF-8"?>
STY4DOC2"""


def Test(tester):
    source = test_harness.FileInfo(uri=BASE_URI+'DOC1')
    sty = test_harness.FileInfo(uri=BASE_URI+'STY1')
    test_harness.XsltTest(tester, source, [sty], DOC1_STY1_EXPECTED,
                          documentInputFactory=InputSourceFactory,
                          stylesheetInputFactory=InputSourceFactory,
                          title='Simple URI')


    source = test_harness.FileInfo(uri=BASE_URI+'DOC1')
    sty = test_harness.FileInfo(uri=BASE_URI+'STY2')
    test_harness.XsltTest(tester, source, [sty], DOC1_STY2_EXPECTED,
                          documentInputFactory=InputSourceFactory,
                          stylesheetInputFactory=InputSourceFactory,
                          title='Relative URI included')


    source = test_harness.FileInfo(uri=BASE_URI+'DOC1')
    sty = test_harness.FileInfo(uri=BASE_URI+'STY3')
    test_harness.XsltTest(tester, source, [sty], DOC1_STY3_EXPECTED,
                          documentInputFactory=InputSourceFactory,
                          stylesheetInputFactory=InputSourceFactory,
                          title='Relative URI imported')


    source = test_harness.FileInfo(uri=BASE_URI+'DOC1')
    sty = test_harness.FileInfo(uri=BASE_URI+'STY4')
    test_harness.XsltTest(tester, source, [sty], DOC1_STY4_EXPECTED,
                          documentInputFactory=InputSourceFactory,
                          stylesheetInputFactory=InputSourceFactory,
                          title='Relative URI document')
    return
