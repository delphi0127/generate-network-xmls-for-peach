
'''Contributed by Carey Evans'''

import sys

from Ft.Xml.Xslt import Processor

"""outenc.py

Test whether 4DOM and 4XSLT produce correct output given different
input strings, using different output encodings.  The general testing
procedure goes:

    Read document into DOM from string <A>.

    Extract text into Unicode string <B>.

    Write DOM to another string <X> using specified output encoding.

    Read <X> into a DOM, and extract text into Unicode string <Y>.

    Check whether <B> == <Y>.

An exception at any stage is also an error.  Any Unicode character can
be encoded in any output encoding, e.g. LATIN CAPITAL LETTER C WITH
CARON as &#268;.

"""

# All the following strings are in UTF-8;
# I'm not trying to test the parser.

input_88591 = '0x0041 is A, 0x00C0 is \303\200.'
input_88592 = '0x0041 is A, 0x010C is \304\214.'
input_both = '0x0041 is A, 0x00C0 is \303\200, 0x010C is \304\214.'

inputs = [('ISO-8859-1', input_88591),
#          ('ISO-8859-2', input_88592),
#          ('Unicode', input_both)
          ]

#out_encodings = ['UTF-8', 'ISO-8859-1', 'ISO-8859-2']
out_encodings = ['UTF-8', 'ISO-8859-1']

xslt_input_fmt = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE text [ <!ELEMENT text (#PCDATA)> ]>
<text>%s</text>'''
xslt_identity = '''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="xml" indent="no" encoding="%s"/>
<xsl:template match="/">
 <text><xsl:value-of select="text"/></text>
</xsl:template>
</xsl:stylesheet>'''
#'

def get_text(doc):
    doc.normalize()
    elem = doc.documentElement
    child = elem.firstChild
    text = child.nodeValue
    return text

def process(doc, out_enc):
    proc = Processor.Processor()
    stylesheet = xslt_identity % (out_enc,)
    proc.appendStylesheetString(stylesheet)
    return proc.runNode(doc)

def results(input, out_enc):
    indoc = None
    outdoc = None

    indoc = Sax2.FromXml(input)
    intext = get_text(indoc)

    outstring = process(indoc, out_enc)

    outdoc = Sax2.FromXml(outstring)
    outtext = get_text(outdoc)


    return intext, outtext

def test(tester, inp, out_enc):
    tester.startTest(inp[0]+" to "+out_enc)
    input = inp[1]
    try:
        intext, outtext = results(xslt_input_fmt % (input,), out_enc)
    except Exception, e:
        tester.testError("Exception %s"%e)
        return

    tester.compare(input, intext)
    tester.compare(input, outtext)
    tester.testDone()

try:
    from xml.dom.ext.reader import Sax2
    import xml.unicode.iso8859
    from xml.sax import saxexts
except ImportError:
    Sax2 = None
    pass

def Test(tester):
    tester.startTest('Checking Unicode support')

    skipped = 0
    if sys.version[0] == '2':
        tester.message("Test skipped (version >= 2.0)")
        skipped = 1
    if Sax2 is None:
        tester.message("Test skipped (Rquires PyXML)")
        skipped = 1

    tester.testDone()

    if not skipped:
        parser = saxexts.XMLParserFactory.make_parser()
        if parser.__class__.__name__ != "SAX_expat":
            tester.message("Using", parser.__class__, "parser, results are unpredictable.\n")
        for out_enc in out_encodings:
            for inp in inputs:
                test(tester,inp, out_enc)
    return
