#"Steve Muench" <Steve.Muench@oracle.com> offers help with nested grouping to "Alex Aguilar" <alex@pasofijo.com>

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>
  <!-- Used for distinct allocation categories -->
  <xsl:key name="cat" match="allocCategory" use="."/>
  <!-- Used for distinct asset classes for an alloc category -->
  <xsl:key name="ucls" match="assetClass"   use="concat(.,'::',../allocCategory)"/>
  <!-- Used to find (not-distinct) asset classes for an alloc cat -->
  <xsl:key name="cls" match="assetClass" use="../allocCategory"/>
  <!-- Used to find funds in a (allocCat,assetClass) combination -->
  <xsl:key name="fnd" match="Fund" use="concat(allocCategory,'::',assetClass)"/>
  <xsl:template match="/">
    <xsl:for-each 
      select="/FundList/Fund/allocCategory[generate-id(.)=
                                           generate-id(key('cat',.)[1])]">
      <xsl:variable name="curcat" select="string(.)"/>
      <xsl:value-of select="$curcat"/>
      <xsl:text>&#x0a;</xsl:text>
      <xsl:for-each 
        select="key('cls',$curcat)[generate-id(.)=
                                   generate-id(key('ucls',
                                   concat(.,'::',$curcat))[1])]">
        <xsl:variable name="curclass" select="string(.)"/>
        <xsl:text>  </xsl:text>
        <xsl:value-of select="$curclass"/>
        <xsl:text>&#x0a;</xsl:text>
        <xsl:for-each select="key('fnd',concat($curcat,'::',$curclass))">
          <xsl:text>    </xsl:text>
          <xsl:value-of select="fundName"/>
          <xsl:text>&#x0a;</xsl:text>
        </xsl:for-each>
      </xsl:for-each>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>"""

source_1 = """<?xml version="1.0" encoding="UTF-8"?>
<FundList>
	<Fund rowid="1">
		<fundName>Sarah's MoneyMarket Fund</fundName>
		<allocCategory>Cash</allocCategory>
		<assetClass>MoneyMarket</assetClass>
		<capitalization/>
		<id>12845</id>
		<percent>0</percent>
		<risk>4</risk>
	</Fund>
	<Fund rowid="2">
		<fundName>Bob's MoneyMarket Fund</fundName>
		<allocCategory>Cash</allocCategory>
		<assetClass>MoneyMarket</assetClass>
		<capitalization/>
		<id>11475</id>
		<percent>0</percent>
		<risk>4</risk>
	</Fund>
	<Fund rowid="3">
		<fundName>Will's Fund</fundName>
		<allocCategory>Domestic Equity</allocCategory>
		<assetClass>Growth</assetClass>
		<capitalization>Small Cap</capitalization>
		<id>12345</id>
		<percent>0</percent>
		<risk>4</risk>
	</Fund>
	<Fund rowid="4">
		<fundName>John's Fund</fundName>
		<allocCategory>Domestic Equity</allocCategory>
		<assetClass>Growth</assetClass>
		<capitalization>Small Cap</capitalization>
		<id>11445</id>
		<percent>0</percent>
		<risk>4</risk>
	</Fund>
	<Fund rowid="5">
		<fundName>Patrick's Fund</fundName>
		<allocCategory>Domestic Equity</allocCategory>
		<assetClass>Value</assetClass>
		<capitalization>Medium Cap</capitalization>
		<id>12378</id>
		<percent>0</percent>
		<risk>4</risk>
	</Fund>
	<Fund rowid="6">
		<fundName>Alex's Fund</fundName>
		<allocCategory>Domestic Equity</allocCategory>
		<assetClass>Aggressive Growth</assetClass>
		<capitalization>Medium Cap</capitalization>
		<id>17378</id>
		<percent>0</percent>
		<risk>5</risk>
	</Fund>
	<Fund rowid="7">
		<fundName>Pablo's Fund</fundName>
		<allocCategory>International Equity</allocCategory>
		<assetClass>Growth</assetClass>
		<capitalization>Small Cap</capitalization>
		<id>12345</id>
		<percent>0</percent>
		<risk>4</risk>
	</Fund>
	<Fund rowid="8">
		<fundName>Pierre's Fund</fundName>
		<allocCategory>International Equity</allocCategory>
		<assetClass>Growth</assetClass>
		<capitalization>Small Cap</capitalization>
		<id>11645</id>
		<percent>0</percent>
		<risk>4</risk>
	</Fund>
	<Fund rowid="9">
		<fundName>Bharat's Fund</fundName>
		<allocCategory>International Equity</allocCategory>
		<assetClass>Value</assetClass>
		<capitalization>Small Cap</capitalization>
		<id>12378</id>
		<percent>0</percent>
		<risk>5</risk>
	</Fund>
	<Fund rowid="10">
		<fundName>Onikaru's Fund</fundName>
		<allocCategory>International Equity</allocCategory>
		<assetClass>Value</assetClass>
		<capitalization>Large Cap</capitalization>
		<id>13474</id>
		<percent>0</percent>
		<risk>4</risk>
	</Fund>
	<Fund rowid="11">
		<fundName>Gunther's Fund</fundName>
		<allocCategory>International Equity</allocCategory>
		<assetClass>Aggressive Growth</assetClass>
		<capitalization>Medium Cap</capitalization>
		<id>17378</id>
		<percent>0</percent>
		<risk>5</risk>
	</Fund>
</FundList>"""

expected_1 = """Cash
  MoneyMarket
    Sarah's MoneyMarket Fund
    Bob's MoneyMarket Fund
Domestic Equity
  Growth
    Will's Fund
    John's Fund
  Value
    Patrick's Fund
  Aggressive Growth
    Alex's Fund
International Equity
  Growth
    Pablo's Fund
    Pierre's Fund
  Value
    Bharat's Fund
    Onikaru's Fund
  Aggressive Growth
    Gunther's Fund
"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
