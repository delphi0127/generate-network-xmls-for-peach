#Olivier Cayrol <olivier.cayrol@logilab.fr> reports (https://sourceforge.net/tracker/index.php?func=detail&aid=452113&group_id=6473&atid=106473) bug with spacing and nbsps

from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html"
            version="4.0" 
            encoding="ISO-8859-1" 
            indent="yes" 
            doctype-public="-//W3C//DTD HTML 4.0//EN"/>

<xsl:template match="/">
  <html>
    <head/>
    <body>
      <p>&#160;</p>
      <p> &#160;</p>
      <p>&#160; </p>
      <p> &#160;*</p>
      <p>*&#160; </p>
      <p>*&#160;*</p>
      <p>*</p>
      <table width="100%" border="1">
       <tr>
        <td bgcolor="blue">&#160;</td>
        <td bgcolor="blue"> &#160;</td>
        <td bgcolor="blue">&#160; </td>
        <td bgcolor="blue"> &#160;*</td>
        <td bgcolor="blue">*&#160; </td>
        <td bgcolor="blue">*&#160;*</td>
        <td bgcolor="blue">*</td>
       </tr>
      </table>
    </body>
  </html>
</xsl:template>
</xsl:stylesheet>
"""

source_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<root/>
"""


expected_1 = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0//EN">\n<html>\n  <head>\n    <meta http-equiv=\'Content-Type\' content=\'text/html; charset=ISO-8859-1\'>\n  </head>\n  <body>\n    <p>&nbsp;</p>\n    <p> &nbsp;</p>\n    <p>&nbsp; </p>\n    <p> &nbsp;*</p>\n    <p>*&nbsp; </p>\n    <p>*&nbsp;*</p>\n    <p>*</p>\n    <table width=\'100%\' border=\'1\'>\n      <tr>\n        <td bgcolor=\'blue\'>&nbsp;</td>\n        <td bgcolor=\'blue\'> &nbsp;</td>\n        <td bgcolor=\'blue\'>&nbsp; </td>\n        <td bgcolor=\'blue\'> &nbsp;*</td>\n        <td bgcolor=\'blue\'>*&nbsp; </td>\n        <td bgcolor=\'blue\'>*&nbsp;*</td>\n        <td bgcolor=\'blue\'>*</td>\n      </tr>\n    </table>\n  </body>\n</html>'


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='Spacing and nbsps (Olivier Cayroll)')
    return
