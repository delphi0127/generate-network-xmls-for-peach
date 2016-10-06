#Example from Michael Kay's to Sanjay on 9 Dec 1999, with minor corrections to produce well-formed XML

from Xml.Xslt import test_harness

sheet_1 = """<xsl:transform
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 version="1.0"
>
<xsl:template match="/">
    <top>
    <xsl:apply-templates select="/FORMS/CONTAINERS"/>
    </top>
</xsl:template>
<xsl:template match="/FORMS/CONTAINERS"> 
    <xsl:for-each select="CONTAINER"> 

        <xsl:copy-of select="//*[name(.)=current()/PRE_HTML]" /> 
        <xsl:value-of select="TITLE"/>
        <xsl:comment>Do some more things here</xsl:comment>

        <xsl:copy-of select="//*[name(.)=current()/POST_HTML]" /> 

    </xsl:for-each> 
</xsl:template> 
</xsl:transform>"""

source_1 = """<FORMS>
    <CONTAINERS>
        <CONTAINER>
            <PRE_HTML>DEPT_PREHTML</PRE_HTML>
            <TITLE>Departments</TITLE>
            <POST_HTML>DEPT_POSTHTML</POST_HTML>
        </CONTAINER>

        <CONTAINER>
            <PRE_HTML>EMP_PREHTML</PRE_HTML>
            <TITLE>Employees</TITLE>
            <POST_HTML>EMP_POSTHTML</POST_HTML>
        </CONTAINER>
    </CONTAINERS>

    <DEPT_PREHTML>
        <!-- Well-formed HTML. -->
        <DIV id="Layer1" style="position: absolute">
            <IMG src="/images/edu.gif" width="917"
                 height="104"/>
        </DIV>
    </DEPT_PREHTML>

    <DEPT_POSTHTML>
        <P>DEPT_POSTHTML: Some more well-formed HTML. </P>
    </DEPT_POSTHTML>

    <EMP_PREHTML>
        <P>EMP_PREHTML: Some more well-formed HTML. </P>
    </EMP_PREHTML>

    <EMP_POSTHTML>
        <P>EMP_POSTHTML: Some more well-formed HTML. </P>
    </EMP_POSTHTML>
</FORMS>"""


saxon_expected = """<?xml version="1.0"?>
<top><DEPT_PREHTML>
        <!-- Well-formed HTML. -->
        <DIV id="Layer1" style="position: absolute">
            <IMG src="/images/edu.gif" width="917" height="104"></IMG>
        </DIV>
    </DEPT_PREHTML>Departments<!--Do some more things here--><DEPT_POSTHTML>

        <P>DEPT_POSTHTML: Some more well-formed HTML. </P>
    </DEPT_POSTHTML><EMP_PREHTML>
        <P>EMP_PREHTML: Some more well-formed HTML. </P>
    </EMP_PREHTML>Employees<!--Do some more things here--><EMP_POSTHTML>
        <P>EMP_POSTHTML: Some more well-formed HTML. </P>
    </EMP_POSTHTML></top>"""


#Note that XML processors are not required to pass on comments
expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<top><DEPT_PREHTML>
        <!-- Well-formed HTML. -->
        <DIV style='position: absolute' id='Layer1'>
            <IMG height='104' width='917' src='/images/edu.gif'/>
        </DIV>
    </DEPT_PREHTML>Departments<!--Do some more things here--><DEPT_POSTHTML>
        <P>DEPT_POSTHTML: Some more well-formed HTML. </P>
    </DEPT_POSTHTML><EMP_PREHTML>
        <P>EMP_PREHTML: Some more well-formed HTML. </P>
    </EMP_PREHTML>Employees<!--Do some more things here--><EMP_POSTHTML>
        <P>EMP_POSTHTML: Some more well-formed HTML. </P>
    </EMP_POSTHTML></top>"""
    #Note that XML processors are not required to pass on comments


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
