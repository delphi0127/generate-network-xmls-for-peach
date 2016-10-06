# a pretty straightforward Muenchian grouping test

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" indent="yes"/>

  <xsl:key name="skills-by-mark" match="skill" use="@mark"/>
  <xsl:template match="skills">
    <table>
      <!-- process a set consisting of the first skill element for each mark -->
      <xsl:for-each select="skill[count(.|key('skills-by-mark',@mark)[1])=1]">
        <tr>
          <td><b><xsl:value-of select="concat(@mark,' skills:')"/></b></td>
          <td>
            <!-- process all skill elements having the current skill's mark -->
            <xsl:for-each select="key('skills-by-mark',@mark)">
              <xsl:value-of select="@name"/>
              <xsl:if test="position()!=last()"><br/></xsl:if>
            </xsl:for-each>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

</xsl:stylesheet>"""

source_1 = """<skills>
    <skill mark="excellent" name="excellentskill"/>
    <skill mark="excellent" name="excellent skill"/>
    <skill mark="good" name="goodskill"/>
    <skill mark="good" name="goodskill"/>
    <skill mark="basic" name="basicskill"/>
    <skill mark="basic" name="basicskill"/>
    <skill mark="excellent" name="excellentskill"/>
    <skill mark="good" name="goodskill"/>
    <skill mark="basic" name="basicskill"/>
</skills>"""

expected_1 = """<table>
  <tr>
    <td><b>excellent skills:</b></td>
    <td>excellentskill
      <br>excellent skill
      <br>excellentskill
    </td>
  </tr>
  <tr>
    <td><b>good skills:</b></td>
    <td>goodskill
      <br>goodskill
      <br>goodskill
    </td>
  </tr>
  <tr>
    <td><b>basic skills:</b></td>
    <td>basicskill
      <br>basicskill
      <br>basicskill
    </td>
  </tr>
</table>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='ordinary Muenchian grouping with keys')
    return
