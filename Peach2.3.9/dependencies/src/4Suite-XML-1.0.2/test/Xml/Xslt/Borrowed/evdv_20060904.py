#Bug reported by Eric van der Vlist on IRC
from Xml.Xslt import test_harness

TRANSFORM_1 = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="Invoice">
    <result>
      <xsl:value-of select="sum(dyn:map(InvoiceRow/RowAmount, 'string(.)'))"/>
    </result>
  </xsl:template>

</xsl:transform>
"""


SOURCE_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
   <TotalAmount>10000</TotalAmount>
   <InvoiceRow>  
     <RowAmount>3000</RowAmount>
   </InvoiceRow>
   <InvoiceRow>  
     <RowAmount>7000</RowAmount>
   </InvoiceRow>
</Invoice>
"""


EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result>10000</result>'


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=TRANSFORM_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED,
                          title='Simple dynamic map test')
    return

