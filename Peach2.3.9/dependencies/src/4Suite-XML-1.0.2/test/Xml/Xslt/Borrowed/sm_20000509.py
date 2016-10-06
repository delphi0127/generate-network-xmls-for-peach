#Steve Meunch's Grouping revelation, with some replication for performance testing.  9 May 2000.

"""
From: "Steve Muench" <smuench@us.oracle.com>
To: <xsl-list@mulberrytech.com>
Subject: Re: grouping (was: if or template?)
Date: Tue, 9 May 2000 01:10:53 -0700 (02:10 MDT)

| ><xsl:key name="tid" use="tracker-id" select="."/>
| >
| ><xsl:for-each
| >select="//tracker-id[generate-id(.)=generate-id(key('tid',.)[1])]">
| >
| >I hope Steve will forgive me for announcing this discovery 
| >before he does,
| >I'm quite excited by it because it gives much better performance.
| 
| All it does to me is make me scratch my head!
| Steve/Mike, would you give us the idiots view on this please,
| whats happening? *Why* does it provide the unique tracker-id please?

When you're doing grouping, you basically want to select
exactly one of each unique thing.

   //tracker-id

would select all tracker-id elements in the document.

Declaring a 'tid' key like:

  <xsl:key name="tid" use="tracker-id" select="."/>

The key('tid','tidvalue') function looks up all nodes having 
tracker-id = 'tidvalue'. In order to support this lookup,
the processor will be keeping a list in memory like this:

"tid" Key lookup Table
======================
tracker-id   Ref to tracker-id elements
  value      having that value
-----------  --------------------------
  abc123     node(109),node(344),node(496)
  def456     node(15)
  hij332     node(89),node(101)

Where the notation node(nnn) means "the node whose node-id is nnn"
as defined by generated-id(). To be concrete, the processor
is likely keeping some kind of Hashtable with the tracker-id
*value* as the hash key, and a node-list as the hash value.  

  //tracker-id[generate-id(.)=generate-id(key('tid',.)[1])]

selects all tracker-id elements in the document having
a node-id equal to the node-id of the first node in the
"key lookup table's" list of nodes having the current 
tracker-id.

Said more simply, it selects the first tracker-id element
for each unique tracker-id value.

Or even more simply, it selects a list of distinct tracker-id values.

Here's an example.

Take the "Task.xml" File below...

[snip xml_source_1]

The stylesheet:

[snip sheet_str_1]

Produces a sorted, grouped list of tasks by owner and
is much faster than the equivalent "scan-my-preceding" 
approach...

[snip expected_1]

For testing, here is a slower.xsl stylesheet that
does the same job without using the key() technique:

[snip sheet_str_2]

as you scale up the size of the Task.xml input file, the performance
difference can be dramatic. Try copy/pasting the elements
in the Task.xml above to creates a couple thousand <Task>
elements to give it a spin...

[snip]
"""
#"

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output indent="yes"/>
  <xsl:key name="xxx" match="/Tasks/Task/Owner" use="."/>
  <xsl:template match="/">
  <Tasks>
    <xsl:for-each select="/Tasks/Task/Owner[generate-id(.)=generate-id(key('xxx',.))]">
      <xsl:sort select="."/>
      <Owner name="{.}">
        <xsl:for-each select="key('xxx',.)/..">
          <xsl:copy-of select="."/>
        </xsl:for-each>
      </Owner>
    </xsl:for-each>
  </Tasks>
  </xsl:template>
</xsl:stylesheet>
"""


sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <!-- Slower.xsl -->
  <xsl:output indent="yes"/>
  <xsl:template match="/">
  <Tasks>
    <xsl:for-each
        select="/Tasks/Task[not(preceding-sibling::Task/Owner=./Owner)]/Owner">
      <xsl:sort select="."/>
      <xsl:variable name="owner" select="."/>
      <Owner name="{.}">
        <xsl:for-each select="/Tasks/Task[Owner = $owner ]">
          <xsl:copy-of select="."/>
        </xsl:for-each>
      </Owner>
    </xsl:for-each>
  </Tasks>
  </xsl:template>
</xsl:stylesheet>
"""


source_1 = """<Tasks>
   <Task><Desc>Task1</Desc><Owner>Steve</Owner></Task>
   <Task><Desc>Task2</Desc><Owner>Mike</Owner></Task>
   <Task><Desc>Task3</Desc><Owner>Dave</Owner></Task>
   <Task><Desc>Task4</Desc><Owner>Steve</Owner></Task>
   <Task><Desc>Task5</Desc><Owner>Mike</Owner></Task>
   <Task><Desc>Task6</Desc><Owner>Mike</Owner></Task>
   <Task><Desc>Task7</Desc><Owner>Uche</Owner></Task>
   <Task><Desc>Task8</Desc><Owner>Jeremy</Owner></Task>
   <Task><Desc>Task9</Desc><Owner>Phil</Owner></Task>
   <Task><Desc>Task10</Desc><Owner>Chime</Owner></Task>
   <Task><Desc>Task11</Desc><Owner>Glenn</Owner></Task>
   <Task><Desc>Task12</Desc><Owner>Uche</Owner></Task>
   <Task><Desc>Task13</Desc><Owner>Steve</Owner></Task>
   <Task><Desc>Task14</Desc><Owner>Phil</Owner></Task>
   <Task><Desc>Task15</Desc><Owner>Dave</Owner></Task>
   <Task><Desc>Task16</Desc><Owner>Jeremy</Owner></Task>
   <Task><Desc>Task17</Desc><Owner>Steve</Owner></Task>
   <Task><Desc>Task18</Desc><Owner>Glenn</Owner></Task>
   <Task><Desc>Task19</Desc><Owner>Uche</Owner></Task>
   <Task><Desc>Task20</Desc><Owner>Uche</Owner></Task>
</Tasks>
"""


expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<Tasks>
  <Owner name='Chime'>
    <Task>
      <Desc>Task10</Desc>
      <Owner>Chime</Owner>
    </Task>
  </Owner>
  <Owner name='Dave'>
    <Task>
      <Desc>Task3</Desc>
      <Owner>Dave</Owner>
    </Task>
    <Task>
      <Desc>Task15</Desc>
      <Owner>Dave</Owner>
    </Task>
  </Owner>
  <Owner name='Glenn'>
    <Task>
      <Desc>Task11</Desc>
      <Owner>Glenn</Owner>
    </Task>
    <Task>
      <Desc>Task18</Desc>
      <Owner>Glenn</Owner>
    </Task>
  </Owner>
  <Owner name='Jeremy'>
    <Task>
      <Desc>Task8</Desc>
      <Owner>Jeremy</Owner>
    </Task>
    <Task>
      <Desc>Task16</Desc>
      <Owner>Jeremy</Owner>
    </Task>
  </Owner>
  <Owner name='Mike'>
    <Task>
      <Desc>Task2</Desc>
      <Owner>Mike</Owner>
    </Task>
    <Task>
      <Desc>Task5</Desc>
      <Owner>Mike</Owner>
    </Task>
    <Task>
      <Desc>Task6</Desc>
      <Owner>Mike</Owner>
    </Task>
  </Owner>
  <Owner name='Phil'>
    <Task>
      <Desc>Task9</Desc>
      <Owner>Phil</Owner>
    </Task>
    <Task>
      <Desc>Task14</Desc>
      <Owner>Phil</Owner>
    </Task>
  </Owner>
  <Owner name='Steve'>
    <Task>
      <Desc>Task1</Desc>
      <Owner>Steve</Owner>
    </Task>
    <Task>
      <Desc>Task4</Desc>
      <Owner>Steve</Owner>
    </Task>
    <Task>
      <Desc>Task13</Desc>
      <Owner>Steve</Owner>
    </Task>
    <Task>
      <Desc>Task17</Desc>
      <Owner>Steve</Owner>
    </Task>
  </Owner>
  <Owner name='Uche'>
    <Task>
      <Desc>Task7</Desc>
      <Owner>Uche</Owner>
    </Task>
    <Task>
      <Desc>Task12</Desc>
      <Owner>Uche</Owner>
    </Task>
    <Task>
      <Desc>Task19</Desc>
      <Owner>Uche</Owner>
    </Task>
    <Task>
      <Desc>Task20</Desc>
      <Owner>Uche</Owner>
    </Task>
  </Owner>
</Tasks>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 2')
    return
