import os

from Ft.Lib import Uri
from Ft.Xml import READ_EXTERNAL_DTD

from Xml.Xslt import test_harness

base = os.getcwd()
if base[-1] != os.sep:
    base += os.sep
base = Uri.OsPathToUri(base)

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="html">
  <xsl:copy-of select="."/>
</xsl:template>
<xsl:template match="*">
  <xsl:apply-templates select="*"/>
</xsl:template>
</xsl:stylesheet>
"""

source_1 = "<foo>Embedded <html><a href='link'>go</a>.</html></foo>"


expected_1 = """<html><a href='link'>go</a>.</html>"""


sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
  <xsl:copy-of select="document('Xml/Xslt/Core/svgeg.svg')"/>
</xsl:template>

</xsl:stylesheet>
"""

source_2 = "<dummy/>"

# Updated to reflect default attributes from DTD
expected_2_dtd = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" height="10cm" width="10cm" contentStyleType="text/css" preserveAspectRatio="xMidYMid meet" zoomAndPan="magnify" viewBox="0 0 800 800" contentScriptType="text/ecmascript">
  <desc content="structured text">SVG Sample for SunWorld Article</desc>

  <style xml:space="preserve" type="text/css">
    .Lagos { fill: white; stroke: green; stroke-width: 30 }
    .ViaAppia { fill: none; stroke: black; stroke-width: 10 }
    .OrthoLogos { font-size: 32; font-family: helvetica }
  </style>

  <ellipse style="fill: brown; stroke: yellow; stroke-width: 10" rx="250" transform="translate(500 200)" ry="100"/>

  <polygon points="350,75 379,161 469,161 397,215 423,301 350,250 277,                    301 303,215 231,161 321,161" transform="translate(100 200) rotate(45)" class="Lagos"/>

  <text y="400" x="400" class="OrthoLogos">TO KALON</text>

  <path d="M500,600 C500,500 650,500 650,600                             S800,700 800,600" class="ViaAppia"/>
</svg>"""

expected_2 = """<?xml version="1.0" encoding="UTF-8"?>
<svg height="10cm" width="10cm" viewBox="0 0 800 800">
  <desc>SVG Sample for SunWorld Article</desc>

  <style type="text/css">
    .Lagos { fill: white; stroke: green; stroke-width: 30 }
    .ViaAppia { fill: none; stroke: black; stroke-width: 10 }
    .OrthoLogos { font-size: 32; font-family: helvetica }
  </style>

  <ellipse style="fill: brown; stroke: yellow; stroke-width: 10" rx="250" transform="translate(500 200)" ry="100"/>

  <polygon points="350,75 379,161 469,161 397,215 423,301 350,250 277,                    301 303,215 231,161 321,161" transform="translate(100 200) rotate(45)" class="Lagos"/>

  <text y="400" x="400" class="OrthoLogos">TO KALON</text>

  <path d="M500,600 C500,500 650,500 650,600                             S800,700 800,600" class="ViaAppia"/>
</svg>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='copy element and contents')

    title_2 = 'copy external document w/ext. DTD'
    if READ_EXTERNAL_DTD and tester.offline:
        tester.startTest('copy external document w/ext. DTD')
        tester.warning('skipped; reading external DTD requires Internet connection')
        tester.testDone()
    else:
        source = test_harness.FileInfo(string=source_2)
        sheet = test_harness.FileInfo(string=sheet_2, baseUri=base)
        if READ_EXTERNAL_DTD:
            expected = expected_2_dtd
        else:
            expected = expected_2
        test_harness.XsltTest(tester, source, [sheet], expected,
                              title=title_2)
    return
