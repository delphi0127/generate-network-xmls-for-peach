#Olivier Cayrol reports xsl:import bug
#http://sourceforge.net/bugs/?func=detailbug&bug_id=128172&group_id=6473

from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:import href="Xml/Xslt/Borrowed/pool-comm.xsl"/>

  <xsl:output method="html" 
              version="4.0" 
              encoding="ISO-8859-1" 
              indent="yes" 
              doctype-public="-//W3C//DTD HTML 4.0//EN"/>

  <xsl:template match="/">
<html>
 <head>
  <title>Cars Pool Management</title>
  <meta http-equiv="content-type" content="text/html"/>
 </head>

 <body bgcolor="#FFFFFF">
  <h1>Cars Pool Management</h1>
  <table border="1" cellpadding="3">
   <tr>
    <td>State</td>
    <td>Brand</td>
    <td>Type</td>
    <td>Registration Number</td>
   </tr>

    <xsl:apply-templates select="pool/car"/>

  </table>
 </body>
</html>
  </xsl:template>

  <xsl:template match="car">
<tr>
 <td>
    <xsl:call-template name="state-value"/>
 </td>
 <td>
    <xsl:value-of select="brand"/>
 </td>
 <td>
    <xsl:value-of select="type"/>
 </td>
 <td>
    <xsl:value-of select="number"/>
 </td>
</tr>
  </xsl:template>

</xsl:stylesheet>
"""

source_1 = """\
<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>

<!DOCTYPE pool>

<pool>
  <car state="1">
    <brand>Ferrari</brand>
    <type>F40</type>
    <number>459 CBO 75</number>
  </car>
  <car state="2">
    <brand>Porsche</brand>
    <type>911</type>
    <number>347 CQQ 75</number>
  </car>
</pool>
"""

expected_1 = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0//EN">
<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=ISO-8859-1'>
    <title>Cars Pool Management</title>
    <meta content='text/html' http-equiv='content-type'>
  </head>
  <body bgcolor='#FFFFFF'>
    <h1>Cars Pool Management</h1>
    <table cellpadding='3' border='1'>
      <tr>
        <td>State</td>
        <td>Brand</td>
        <td>Type</td>
        <td>Registration Number</td>
      </tr>
      <tr>
        <td><b>Free</b></td>
        <td>Ferrari</td>
        <td>F40</td>
        <td>459 CBO 75</td>
      </tr>
      <tr>
        <td>
        Used
      </td>
        <td>Porsche</td>
        <td>911</td>
        <td>347 CQQ 75</td>
      </tr>
    </table>
  </body>
</html>"""

#"

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
