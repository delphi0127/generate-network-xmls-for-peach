# -*- coding: ISO-8859-1 -*-
"""
> Sounds as if it's a lingering bug.  So any help you or Carey Evans could
> provide in hunting it down would be much appreciated.
>
> Do you have a stripped-down stylesheet that exhibits the problem?  Could
> you also quickly note the exact character sequences you're expecting
> instead of the problem characters?  We'll track it down if we can.

Here's an example.  The input file is ISO-8859-1 encoded, since that's
what my editing environment is:

[snip xml_source_1]

And a simple stylesheet transforms it into XHTML:

[snip sheet_str_1]

If I run xt over this, then the "é" turns into the sequence 0xc3 0xa9,
which is the UTF-8 encoding for "LATIN SMALL LETTER E WITH ACUTE".

If I use 4xslt instead, the individual octets in the UTF-8 encoding
are inserted as &#...; entities instead (wrapped for email):

[snip expected_1]

(Shouldn't that have `<?xml version="1.0"?>' at the top, BTW?)

I would expect to see either what xt produces or "&#233;".
"&#195;&#169;" is two characters, "LATIN CAPITAL LETTER A WITH TILDE"
followed by "COPYRIGHT SIGN", whatever the encoding of the file.

I'd _like_ to be able to make 4XSLT produce ISO-8859-1 encoded output,
but that's another story.

    Carey Evans  http://home.clear.net.nz/pages/c.evans/

"""

from Ft.Xml.Xslt.Processor import Processor
from Ft.Xml.Xslt import OutputParameters

sheet_1 = """<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml"/>

<xsl:template match="/">
<html><head><title>Test</title></head>
<body>
<p><xsl:value-of select="text"/></p>
</body></html>
</xsl:template>

</xsl:stylesheet>"""

sheet_2 = """<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="UTF-8"/>

<xsl:template match="/">
<html><head><title>Test</title></head>
<body>
<p><xsl:value-of select="text"/></p>
</body></html>
</xsl:template>

</xsl:stylesheet>"""

sheet_3 = """<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="ISO-8859-1"/>

<xsl:template match="/">
<html><head><title>Test</title></head>
<body>
<p><xsl:value-of select="text"/></p>
</body></html>
</xsl:template>

</xsl:stylesheet>"""

sheet_4 = """<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
<html><head><title>Test</title></head>
<body>
<p><xsl:value-of select="text"/></p>
</body></html>
</xsl:template>

</xsl:stylesheet>"""

source_1 = """<?xml version="1.0" encoding="ISO-8859-1"?>
<text xml:lang="fr">C'est une révolte?</text>"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<html><head><title>Test</title></head><body><p>C'est une r\303\251volte?</p></body></html>"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<html><head><title>Test</title></head><body><p>C'est une r\303\251volte?</p></body></html>"""

expected_3 = """<?xml version='1.0' encoding='ISO-8859-1'?>
<html><head><title>Test</title></head><body><p>C'est une r\351volte?</p></body></html>"""

expected_4 = """<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <title>Test</title>
  </head>
  <body>
    <p>C'est une r&eacute;volte?</p>
  </body>
</html>"""
#'

from Xml.Xslt import test_harness


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='Default encoding')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='UTF-8 encoding')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='ISO-8859-1 encoding')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_4)
    test_harness.XsltTest(tester, source, [sheet], expected_4,
                          title='Default output method and encoding')
    return
