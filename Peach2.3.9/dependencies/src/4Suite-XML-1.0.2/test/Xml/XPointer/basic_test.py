import os, string
from xml.dom import Node
from Ft.Lib import Uri, UriException

def Test(tester):
    base_uri = Uri.OsPathToUri(__file__, attemptAbsolute=True)
    tester.startTest('Creating test environment')
    from Ft.Xml import XPointer
    from Ft.Xml import Domlette
    r = Domlette.NonvalidatingReader
    doc_uri = Uri.Absolutize('addrbook.xml', base_uri)
    doc = r.parseUri(doc_uri)
    ADDRBOOK = doc.documentElement
    elementType = lambda n, nt=Node.ELEMENT_NODE: n.nodeType == nt
    ENTRIES = filter(elementType, ADDRBOOK.childNodes)
    PA = ENTRIES[0]
    children = filter(elementType, PA.childNodes)
    PA_NAME = children[0]
    PA_ADDR = children[1]
    PA_WORK = children[2]
    PA_FAX = children[3]
    PA_PAGER = children[4]
    PA_EMAIL = children[5]
    EN = ENTRIES[1]
    children = filter(elementType, EN.childNodes)
    EN_NAME = children[0]
    EN_ADDR = children[1]
    EN_WORK = children[2]
    EN_FAX = children[3]
    EN_PAGER = children[4]
    EN_EMAIL = children[5]

    VZ = ENTRIES[2]


    tester.testDone()

    # Just one; it can be too confusing to compare much else
    # because the documents are different
    uri = Uri.Absolutize('addrbook.xml#element(/1)', base_uri)
    tester.startTest('SelectUri(%s)' % uri)
    result = XPointer.SelectUri(uri)
    tester.compare(1, len(result))
    tester.compare(ADDRBOOK.nodeName, result[0].nodeName)
    tester.testDone()

    tester.startTest('SelectNode()')
    frag = 'element(pa/2)'
    result = XPointer.SelectNode(doc, frag)
    tester.compare([PA_ADDR], result, 'frag=%s' % frag)

    frag = 'xpointer(//ENTRY[@ID="en"]/EMAIL)'
    result = XPointer.SelectNode(doc, frag)
    tester.compare([EN_EMAIL], result, 'frag=%s' % frag)
    tester.testDone()

    if tester.offline:
        # No further testing
        return

    tester.startTest('Testing remote lookup')
    nss = {'xsl':'http://www.w3.org/1999/XSL/Transform'}
    uri = "http://www.w3.org/Style/XSL/stylesheets/public2html.xsl#xpointer(//xsl:template[@match='/'])"
    try:
        result = XPointer.SelectUri(uri, nss=nss)
    except UriException, error:
        if error.errorCode != UriException.RESOURCE_ERROR:
            raise
        tester.warning("No internet connection available")
    else:
        tester.compare(1, len(result), 'Wrong number of subresources')
        compared = result[0].localName
        tester.compare('template', compared, 'Wrong localName')
        compared = result[0].attributes[(None, 'match')].value
        tester.compare('/', compared, 'Wrong attribute')
    tester.testDone()
    return
