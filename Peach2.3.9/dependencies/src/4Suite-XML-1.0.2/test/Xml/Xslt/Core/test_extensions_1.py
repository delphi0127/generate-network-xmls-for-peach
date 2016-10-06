import os, sys
from Ft.Xml.Xslt import XsltElement, AttributeInfo

from Xml.Xslt import test_harness

class SystemElement(XsltElement):

    legalAttrs = {
        'command' : AttributeInfo.StringAvt(required=1),
        }
    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self
        command = self._command.evaluate(context)
        os.system(command)
        return (context,)


ExtElements = {
    ('http://foo.org/namespaces/ext-xslt', 'system'): SystemElement
    }


sheet_str_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ext="http://foo.org/namespaces/ext-xslt"
  extension-element-prefixes="ext"
  version="1.0">

  <xsl:template match="execute-command">
    <docelem>
    <ext:system command="{@cmd}"/>
    </docelem>
  </xsl:template>

</xsl:stylesheet>
"""

if sys.platform[:3] != 'win':
    xml_source_1 = """<execute-command cmd="touch 'foo'"/>"""
    xml_source_2 = """<execute-command cmd="rm -f 'foo'"/>"""
else:
    xml_source_1 = """<execute-command cmd="echo '1' > foo"/>"""
    xml_source_2 = """<execute-command cmd="del foo"/>"""
    
expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<docelem/>
"""
expected_2 = expected_1


def Test(tester):

    tester.startGroup("Test 1")

    # make sure there is a clean slate
    if os.path.exists("foo"):
        os.unlink("foo")

    source = test_harness.FileInfo(string=xml_source_1)
    sty = test_harness.FileInfo(string=sheet_str_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          extensionModules=[__name__])
    tester.startTest("Test extension element result")
    tester.compare(1, os.path.exists("foo"))
    tester.testDone()
    tester.groupDone()


    tester.startGroup("Test 2")
    source = test_harness.FileInfo(string=xml_source_2)
    sty = test_harness.FileInfo(string=sheet_str_1)
    test_harness.XsltTest(tester, source, [sty], expected_2,
                          extensionModules=[__name__])
    tester.startTest("Test extension element result")
    tester.compare(0, os.path.exists("foo"))
    tester.testDone()
    tester.groupDone()

    # cleanup after ourselves
    if os.path.exists("foo"):
        os.unlink("foo")

    return
