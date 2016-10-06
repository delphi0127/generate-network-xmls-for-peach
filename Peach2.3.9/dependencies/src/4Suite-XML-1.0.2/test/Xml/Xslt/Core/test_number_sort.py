#Based on the XSLT spec: http://docs.local/REC-xslt-19991116.html#sorting and
#http://docs.local/REC-xslt-19991116.html#number

from Xml.Xslt import test_harness

source_1="""<?xml version="1.0" encoding="utf-8"?>
<employees>
  <employee>
    <name>
      <id>1024</id>
      <given>James</given>
      <family>Clark</family>
    </name>
  </employee>
  <employee>
    <name>
      <id>1099</id>
      <given>Uche</given>
      <family>Ogbuji</family>
    </name>
  </employee>
  <employee>
    <name>
      <id>1040</id>
      <given>Mike</given>
      <family>Olson</family>
    </name>
  </employee>
  <employee>
    <name>
      <id>1075</id>
      <given>Mike</given>
      <family>Doe</family>
    </name>
  </employee>
  <employee>
    <name>
      <id>1050</id>
      <given>James</given>
      <family>Doe</family>
    </name>
  </employee>
</employees>"""

source_2="""<?xml version="1.0" encoding="utf-8"?>
<taxonomy>
  <!-- Uche reads too much National Geographic -->
  <kingdom name="Animalia">
    <phylum name="Chordata">
      <class name="Mammalia">
        <order name="Primates">
          <family name="Hominidae">
            <genus name="Homo">
              <species name="Sapiens"/>
            </genus>
            <genus name="Pan">
              <species name="Troglodytes"/>
            </genus>
            <genus name="Pan">
              <species name="Paniscus">
                <comment>Quite familiar to GNOME CORBA users</comment>
              </species>
            </genus>
            <genus name="Gorilla">
              <species name="Gorilla"/>
            </genus>
          </family>
        </order>
        <order name="Carnivora">
          <family name="Felidae">
            <genus name="Felis">
              <species name="Catus"/>
            </genus>
            <genus name="Panthera">
              <species name="Pardus"/>
            </genus>
            <genus name="Panthera">
              <species name="Tigris"/>
            </genus>
            <genus name="Panthera">
              <species name="Leo"/>
            </genus>
          </family>
          <family name="Canidae">
            <genus name="Canis">
              <species name="Familiaris"/>
            </genus>
            <genus name="Canis">
              <species name="Lupus"/>
            </genus>
            <genus name="Vulpes">
              <species name="Vulpes"/>
            </genus>
          </family>
        </order>
      </class>
    </phylum>
  </kingdom>
  <kingdom name="Plantae">
    <division name="Magnoliophyta">
      <comment>Flowering plants</comment>
      <!-- Cronquist System -->
      <class name="Magnoliopsida">
        <comment>Dicots</comment>
        <order name="Rutaceae">
          <family name="Citrus">
            <genus name="Citrus">
              <species name="Aurantiifolia"/>
            </genus>
            <genus name="Citrus">
              <species name="Limon"/>
            </genus>
            <genus name="Citrus">
              <species name="Sinensis"/>
            </genus>
          </family>
        </order>
      </class>
    </division>
  </kingdom>
  <kingdom name="Protista">
  </kingdom>
  <!-- Prokaryotes -->
  <kingdom name="Archaea">
  </kingdom>
  <kingdom name="Eubacteria">
  </kingdom>
</taxonomy>"""

source_3 = """<?xml version="1.0" encoding="utf-8"?>
<book>
  <div1>
    <head>Chapter 1</head>
    <para>Chapter 1 content.</para>
    <div2>
      <head>Section 1.1</head>
      <para>Section 1.1 content.</para>
    </div2>
    <div2>
      <head>Section 1.2</head>
      <para>Section 1.2 content.</para>
    </div2>
  </div1>
  <div1>
    <head>Chapter 2</head>
    <para>Chapter 2 content.</para>
    <div2>
      <head>Section 2.1</head>
      <para>Section 2.1 content.</para>
    </div2>
    <div2>
      <head>Section 2.2</head>
      <para>Section 2.2 content.</para>
    </div2>
  </div1>
</book>
"""

sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="text()"/>

  <xsl:template match="employees">
    <ul>
      <xsl:apply-templates select="employee">
        <xsl:sort select="name/family"/>
        <xsl:sort select="name/given"/>
      </xsl:apply-templates>
    </ul>
  </xsl:template>

  <xsl:template match="employee">
    <li>
      <xsl:number value="position()" format="1. "/>
      <xsl:value-of select="name/given"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="name/family"/>
    </li>
  </xsl:template>

</xsl:stylesheet>"""

expected_1 = """<?xml version="1.0" encoding="UTF-8"?>
<ul><li>1. James Clark</li><li>2. James Doe</li><li>3. Mike Doe</li><li>4. Uche Ogbuji</li><li>5. Mike Olson</li></ul>"""

sheet_2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="text()"/>

  <xsl:template match="employees">
    <ul>
      <xsl:apply-templates select="employee">
        <xsl:sort select="name/family" order="descending"/>
        <xsl:sort select="name/given" order="ascending"/>
      </xsl:apply-templates>
    </ul>
  </xsl:template>

  <xsl:template match="employee">
    <li>
      <xsl:value-of select="name/given"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="name/family"/>
    </li>
  </xsl:template>

</xsl:stylesheet>"""

expected_2 = """<?xml version="1.0" encoding="UTF-8"?>
<ul><li>Mike Olson</li><li>Uche Ogbuji</li><li>James Doe</li><li>Mike Doe</li><li>James Clark</li></ul>"""

sheet_3 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="text()"/>

  <xsl:template match="employees">
    <ul>
      <xsl:apply-templates select="employee">
        <xsl:sort select="name/family"/>
        <xsl:sort select="name/given" case-order="lower-first"/>
      </xsl:apply-templates>
    </ul>
  </xsl:template>

  <xsl:template match="employee">
    <li>
      <xsl:value-of select="name/given"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="name/family"/>
    </li>
  </xsl:template>

</xsl:stylesheet>"""

expected_3 = """<?xml version="1.0" encoding="UTF-8"?>
<ul><li>James Clark</li><li>James Doe</li><li>Mike Doe</li><li>Uche Ogbuji</li><li>Mike Olson</li></ul>"""

sheet_4 = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="text()"/>

  <xsl:template match="employees">
    <ul>
      <xsl:apply-templates select="employee">
        <xsl:sort select="name/id" data-type="number"/>
      </xsl:apply-templates>
    </ul>
  </xsl:template>

  <xsl:template match="employee">
    <li>
      <xsl:value-of select="name/given"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="name/family"/>
    </li>
  </xsl:template>

</xsl:stylesheet>"""

expected_4 = """<?xml version="1.0" encoding="UTF-8"?>
<ul><li>James Clark</li><li>Mike Olson</li><li>James Doe</li><li>Mike Doe</li><li>Uche Ogbuji</li></ul>"""

sheet_5 = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text"/>

  <xsl:template match="/">
    <!-- Some number formatting tests -->
    <xsl:text>Format 1715 using "A": </xsl:text><xsl:number value="1715" format="A"/><xsl:text>&#10;</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="*">
    <xsl:number format="==>I.A.1.a.i. " level="multiple" count="*[not(name()='comment')]"/>
    <xsl:value-of select="concat(name(), ': ' , @name, '&#10;')"/>
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="comment"/>

</xsl:stylesheet>"""

expected_5 = """\
Format 1715 using "A": BMY
==>I. taxonomy:\x20
==>I.A. kingdom: Animalia
==>I.A.1. phylum: Chordata
==>I.A.1.a. class: Mammalia
==>I.A.1.a.i. order: Primates
==>I.A.1.a.i.i. family: Hominidae
==>I.A.1.a.i.i.i. genus: Homo
==>I.A.1.a.i.i.i.i. species: Sapiens
==>I.A.1.a.i.i.ii. genus: Pan
==>I.A.1.a.i.i.ii.i. species: Troglodytes
==>I.A.1.a.i.i.iii. genus: Pan
==>I.A.1.a.i.i.iii.i. species: Paniscus
==>I.A.1.a.i.i.iv. genus: Gorilla
==>I.A.1.a.i.i.iv.i. species: Gorilla
==>I.A.1.a.ii. order: Carnivora
==>I.A.1.a.ii.i. family: Felidae
==>I.A.1.a.ii.i.i. genus: Felis
==>I.A.1.a.ii.i.i.i. species: Catus
==>I.A.1.a.ii.i.ii. genus: Panthera
==>I.A.1.a.ii.i.ii.i. species: Pardus
==>I.A.1.a.ii.i.iii. genus: Panthera
==>I.A.1.a.ii.i.iii.i. species: Tigris
==>I.A.1.a.ii.i.iv. genus: Panthera
==>I.A.1.a.ii.i.iv.i. species: Leo
==>I.A.1.a.ii.ii. family: Canidae
==>I.A.1.a.ii.ii.i. genus: Canis
==>I.A.1.a.ii.ii.i.i. species: Familiaris
==>I.A.1.a.ii.ii.ii. genus: Canis
==>I.A.1.a.ii.ii.ii.i. species: Lupus
==>I.A.1.a.ii.ii.iii. genus: Vulpes
==>I.A.1.a.ii.ii.iii.i. species: Vulpes
==>I.B. kingdom: Plantae
==>I.B.1. division: Magnoliophyta
==>I.B.1.a. class: Magnoliopsida
==>I.B.1.a.i. order: Rutaceae
==>I.B.1.a.i.i. family: Citrus
==>I.B.1.a.i.i.i. genus: Citrus
==>I.B.1.a.i.i.i.i. species: Aurantiifolia
==>I.B.1.a.i.i.ii. genus: Citrus
==>I.B.1.a.i.i.ii.i. species: Limon
==>I.B.1.a.i.i.iii. genus: Citrus
==>I.B.1.a.i.i.iii.i. species: Sinensis
==>I.C. kingdom: Protista
==>I.D. kingdom: Archaea
==>I.E. kingdom: Eubacteria
"""

sheet_6 = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text"/>

  <xsl:template match="*">
    <xsl:number format="==>I,A$1*a!i:: " level="multiple" count="*"/>
    <xsl:value-of select="concat(name(), ': ' , @name, '&#10;')"/>
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="comment"/>

</xsl:stylesheet>"""

expected_6 = """\
==>I:: taxonomy:\x20
==>I,A:: kingdom: Animalia
==>I,A$1:: phylum: Chordata
==>I,A$1*a:: class: Mammalia
==>I,A$1*a!i:: order: Primates
==>I,A$1*a!i!i:: family: Hominidae
==>I,A$1*a!i!i!i:: genus: Homo
==>I,A$1*a!i!i!i!i:: species: Sapiens
==>I,A$1*a!i!i!ii:: genus: Pan
==>I,A$1*a!i!i!ii!i:: species: Troglodytes
==>I,A$1*a!i!i!iii:: genus: Pan
==>I,A$1*a!i!i!iii!i:: species: Paniscus
==>I,A$1*a!i!i!iv:: genus: Gorilla
==>I,A$1*a!i!i!iv!i:: species: Gorilla
==>I,A$1*a!ii:: order: Carnivora
==>I,A$1*a!ii!i:: family: Felidae
==>I,A$1*a!ii!i!i:: genus: Felis
==>I,A$1*a!ii!i!i!i:: species: Catus
==>I,A$1*a!ii!i!ii:: genus: Panthera
==>I,A$1*a!ii!i!ii!i:: species: Pardus
==>I,A$1*a!ii!i!iii:: genus: Panthera
==>I,A$1*a!ii!i!iii!i:: species: Tigris
==>I,A$1*a!ii!i!iv:: genus: Panthera
==>I,A$1*a!ii!i!iv!i:: species: Leo
==>I,A$1*a!ii!ii:: family: Canidae
==>I,A$1*a!ii!ii!i:: genus: Canis
==>I,A$1*a!ii!ii!i!i:: species: Familiaris
==>I,A$1*a!ii!ii!ii:: genus: Canis
==>I,A$1*a!ii!ii!ii!i:: species: Lupus
==>I,A$1*a!ii!ii!iii:: genus: Vulpes
==>I,A$1*a!ii!ii!iii!i:: species: Vulpes
==>I,B:: kingdom: Plantae
==>I,B$1:: division: Magnoliophyta
==>I,B$1*b:: class: Magnoliopsida
==>I,B$1*b!ii:: order: Rutaceae
==>I,B$1*b!ii!i:: family: Citrus
==>I,B$1*b!ii!i!i:: genus: Citrus
==>I,B$1*b!ii!i!i!i:: species: Aurantiifolia
==>I,B$1*b!ii!i!ii:: genus: Citrus
==>I,B$1*b!ii!i!ii!i:: species: Limon
==>I,B$1*b!ii!i!iii:: genus: Citrus
==>I,B$1*b!ii!i!iii!i:: species: Sinensis
==>I,C:: kingdom: Protista
==>I,D:: kingdom: Archaea
==>I,E:: kingdom: Eubacteria
"""

sheet_7 = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:strip-space elements="*"/>

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="para">
    <p>
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <xsl:template match="div1">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="div2">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="div1/head">
    <h2>
      <xsl:apply-templates select=".." mode="divnum"/>
      <xsl:apply-templates/>
    </h2>
  </xsl:template>

  <xsl:template match="div2/head">
    <h3>
      <xsl:apply-templates select=".." mode="divnum"/>
      <xsl:apply-templates/>
    </h3>
  </xsl:template>

  <xsl:template mode="divnum" match="div1">
    <xsl:number format="1 "/>
  </xsl:template>

  <xsl:template mode="divnum" match="div2">
    <xsl:number level="multiple" count="div1 | div2" format="1.1 "/>
  </xsl:template>

</xsl:stylesheet>"""

expected_7 = """<?xml version="1.0" encoding="UTF-8"?>
<h2>1 Chapter 1</h2>
<p>Chapter 1 content.</p>
<h3>1.1 Section 1.1</h3>
<p>Section 1.1 content.</p>
<h3>1.2 Section 1.2</h3>
<p>Section 1.2 content.</p>
<h2>2 Chapter 2</h2>
<p>Chapter 2 content.</p>
<h3>2.1 Section 2.1</h3>
<p>Section 2.1 content.</p>
<h3>2.2 Section 2.2</h3>
<p>Section 2.2 content.</p>"""

# http://bugs.4suite.org/1162303
# formatting bug reported by Nicholas Piper on 2003-09-09
# http://lists.fourthought.com/pipermail/4suite/2003-September/012132.html
# (also affects sheet_6, above)
#
sheet_8="""<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <xsl:apply-templates select="/taxonomy/kingdom/phylum/class/order/family/genus/species"/>
    </result>
  </xsl:template>

  <xsl:template match="species">
    <species>
      <xsl:number level="multiple" count="*" from="/" format="/1/1"/>
      <xsl:value-of select="concat(' ', @name)"/>
    </species>
  </xsl:template>

</xsl:stylesheet>"""

expected_8 = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <species>/1/1/1/1/1/1/1/1 Sapiens</species>
  <species>/1/1/1/1/1/1/2/1 Troglodytes</species>
  <species>/1/1/1/1/1/1/3/1 Paniscus</species>
  <species>/1/1/1/1/1/1/4/1 Gorilla</species>
  <species>/1/1/1/1/2/1/1/1 Catus</species>
  <species>/1/1/1/1/2/1/2/1 Pardus</species>
  <species>/1/1/1/1/2/1/3/1 Tigris</species>
  <species>/1/1/1/1/2/1/4/1 Leo</species>
  <species>/1/1/1/1/2/2/1/1 Familiaris</species>
  <species>/1/1/1/1/2/2/2/1 Lupus</species>
  <species>/1/1/1/1/2/2/3/1 Vulpes</species>
</result>"""

def Test(tester):

    tester.startGroup('xsl:sort and xsl:number')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='xsl:sort and xsl:number in combination')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='xsl:sort 1')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='xsl:sort 2')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_4)
    test_harness.XsltTest(tester, source, [sheet], expected_4,
                          title='xsl:sort 3')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_5)
    test_harness.XsltTest(tester, source, [sheet], expected_5,
                          title='xsl:number 1')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_6)
    test_harness.XsltTest(tester, source, [sheet], expected_6,
                          title='xsl:number 2')

    # From http://bugs.4suite.org/225186
    source = test_harness.FileInfo(string=source_3)
    sheet = test_harness.FileInfo(string=sheet_7)
    test_harness.XsltTest(tester, source, [sheet], expected_7,
                          title='xsl:number 3')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_8)
    test_harness.XsltTest(tester, source, [sheet], expected_8,
                          title='xsl:number 4')

    tester.groupDone()
    return
