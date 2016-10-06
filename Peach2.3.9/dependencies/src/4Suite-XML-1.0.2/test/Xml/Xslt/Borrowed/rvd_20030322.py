# key()-less grouping tests, including divide-and-conquer (DVC)
# From: "Robbert van Dalen" <juicer@xs4all.nl>
# posted to xsl-list on 22-Mar-2003.

from Xml.Xslt import test_harness

# The author mistakenly thought that key() could not be used on
# result tree fragments that had been converted to node-sets, so
# he devised an efficient DVC-based algorithm and several examples
# that led up to it.

# Input XML (taken from Michael Kay's book)
#
source_1 = """<?xml version="1.0" encoding="utf-8"?>
<cities>
  <city name="Barcelona" country="Espana"/>
  <city name="Paris" country="France"/>
  <city name="Roma" country="Italia"/>
  <city name="Madrid" country="Espana"/>
  <city name="Milano" country="Italia"/>
  <city name="Firenze" country="Italia"/>
  <city name="Napoli" country="Italia"/>
  <city name="Lyon" country="France"/>
</cities>"""

# The following example will give you an idea of grouping
# tree-fragments without using the key() function.
# (partly copied from Michael Kay's book)
#
# 1) First the cities are sorted on the @country attribute. After this, cities
# that share the same @country value will be following each other, which is a
# property we can exploit in step 2.
#
# 2) Then the template that matches city nodes will be called N times if there are
# N cities to be grouped. For each city node in the sorted set the
# 'following-sibling::*[1]' node(s) are matched. If they're not equal, the city
# node will mark a new group.
#
# As Michael Kay already pointed out in his book, the efficiency of this approach
# depends on the implementation of 'following-sibling::*[1]'. If this expression
# has time complexity O(1) then the overall time complexity of getting all the
# groups will be O(N) (leaving sorting out of the equation).
#
# 3) Strangely enough, the last step is actually the most problematic. Let's say
# the second step gave us 3 groups. Then, for each group, the expression
# '$sorted-tree-fragment[country = $country] will be evaluated with time
# complexity O(N).
#
# So, does this mean the overall time complexity will be 3*N = O(N)?
# The answer is definitely no! It does hold for a small number of groups, but if
# we have N/2 groups then time complexity will be O(N^2).
# Selecting nodes with XPATH expressions is usually OK, but in this example we
# want to select the K cities that share the same @country value in O(K) time, not
# O(N) time.
#
# So the question we really want to anwer is: 'how can we efficiently select a
# subset of nodes without traversing them all?'. The anwser is: 'this all depends
# on the selection criterium.'
# Still, if the selection criterium isn't too complex, we can still hope for a
# better solution.
# One solution is that we don't use XPATH expressions to select nodes, but rather
# walk through the nodes by using recursive calls.
#
sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <xsl:apply-templates/>
    </result>
  </xsl:template>

  <xsl:template match="cities">
    <xsl:variable name="sorted">
      <xsl:for-each select="./city">
        <xsl:sort select="@country"/>
        <xsl:copy-of select="."/>
      </xsl:for-each>
    </xsl:variable>

    <xsl:variable name="sorted-tree-fragment" select="exsl:node-set($sorted)/*"/>

    <!-- Gets the groups -->
    <xsl:variable name="groups">
      <xsl:apply-templates select="$sorted-tree-fragment"/>
    </xsl:variable>

    <!-- Iterate through all the groups -->
    <xsl:for-each select="exsl:node-set($groups)/*">
      <xsl:variable name="country" select="@id"/>
      <xsl:copy>
        <xsl:copy-of select="@*"/>
        <!-- Copy the nodes with the same country -->
        <xsl:copy-of select="$sorted-tree-fragment[@country = $country]"/>
      </xsl:copy>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="city">
    <xsl:variable name="preceding" select="./preceding-sibling::*[1]"/>
    <xsl:if test="not(./@country = $preceding/@country)">
      <group id="{./@country}"/>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>"""


expected_1 = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <group id="Espana">
    <city name="Barcelona" country="Espana"/>
    <city name="Madrid" country="Espana"/>
  </group>
  <group id="France">
    <city name="Paris" country="France"/>
    <city name="Lyon" country="France"/>
  </group>
  <group id="Italia">
    <city name="Roma" country="Italia"/>
    <city name="Milano" country="Italia"/>
    <city name="Firenze" country="Italia"/>
    <city name="Napoli" country="Italia"/>
  </group>
</result>"""

# GROUPING USING RECURSION
# 
# One idea to reduce time complexity of the previous example is by slightly
# modifying the match='city' template [...see original post for more...]
#
# The time complexity of the recursive solution can be proven to be O(N) but with
# the recursion depth also to be O(N).
#
# Unfortunately, most XSLT implementations have a maximum recursion depth (~1000)
# so this is not a general solution.
#
source_2 = source_1

sheet_2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <xsl:apply-templates/>
    </result>
  </xsl:template>

  <xsl:template match="cities">
    <xsl:variable name="sorted">
      <xsl:for-each select="./city">
        <xsl:sort select="@country"/>
        <xsl:copy-of select="."/>
      </xsl:for-each>
    </xsl:variable>

    <xsl:variable name="sorted-tree-fragment" select="exsl:node-set($sorted)/*"/>

    <xsl:variable name="groups">
      <xsl:apply-templates select="exsl:node-set($sorted)/*[1]"/>
    </xsl:variable>

    <xsl:apply-templates select="exsl:node-set($groups)/*"/>

  </xsl:template>

  <xsl:template match="city">
    <xsl:variable name="preceding" select="./preceding-sibling::*[1]"/>
    <xsl:choose>
      <xsl:when test="not(./@country = $preceding/@country)">
        <group id="{./@country}">
          <xsl:copy-of select="."/>
          <xsl:apply-templates select="./following-sibling::*[1]"/>
        </group>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy-of select="."/>
        <xsl:apply-templates select="./following-sibling::*[1]"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

<!-- bad: unoptimizable
  <xsl:template match="group">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:copy-of select="./city"/>
    </xsl:copy>
    <xsl:apply-templates select="./group"/>
  </xsl:template>
-->

  <xsl:template match="group">
    <xsl:call-template name="process-group">
      <xsl:with-param name="group-node" select="."/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="process-group">
    <xsl:param name="group-node"/>
    <xsl:if test="$group-node">
      <xsl:copy>
        <xsl:copy-of select="$group-node/@*"/>
        <xsl:copy-of select="$group-node/city"/>
      </xsl:copy>
      <xsl:call-template name="process-group">
        <xsl:with-param name="group-node" select="$group-node/group"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>"""

expected_2 = expected_1


# DVC AND THE BINARY TREE
#
# Dimitre Novatchev was one of the first to mention Divide and Conquer (DVC)
# algorithms to reduce recursion depth. Because most XSLT implementations out
# there still do not support tail-recursion elimination, DVC is the way to go if
# you want to process a lot of nodes.
#
# The idea behind DVC is that to attack a big problem, you should divide it into a
# number of smaller problems.
#
# Not surprisingly, dividing a problem into just 2 subproblems is enough to reduce
# recursion depth to be O(log2(N)).
#
# The following example will give you an idea of how this works:
#
source_3 = """<nodes>
  <node v="1"/>
  <node v="2"/>
  <node v="3"/>
  <node v="4"/>
  <node v="5"/>
  <node v="6"/>
  <node v="7"/>
  <node v="8"/>
</nodes>"""

sheet_3 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <xsl:call-template name="partition">
      <xsl:with-param name="nodes" select="//node"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="partition">
    <xsl:param name="nodes"/>

    <xsl:variable name="half" select="floor(count($nodes) div 2)"/>

    <b>
      <xsl:choose>
        <xsl:when test="count($nodes) &lt;= 1">
          <!-- There is only one node left: stop dividing problem -->
          <xsl:copy-of select="$nodes"/>
        </xsl:when>
        <xsl:otherwise>
          <!-- divide in first half of nodes (left) -->
          <xsl:call-template name="partition">
            <xsl:with-param name="nodes" select="$nodes[position() &lt;= $half]"/>
          </xsl:call-template>
          <!-- divide in second half of nodes (right) -->
          <xsl:call-template name="partition">
            <xsl:with-param name="nodes" select="$nodes[position() &gt; $half]"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </b>
  </xsl:template>

</xsl:stylesheet>"""


# The result is what is called a binary tree representation. At first this
# representation doesn't seem all that useful. Later we will see that specialised
# binary trees can be (re-)used to implement almost any recursive function without
# exceeding the maximum recursion depth.
#
expected_3 = """<?xml version="1.0" encoding="UTF-8"?>
<b>
  <b>
    <b>
      <b>
        <node v="1"/>
      </b>
      <b>
        <node v="2"/>
      </b>
    </b>
    <b>
      <b>
        <node v="3"/>
      </b>
      <b>
        <node v="4"/>
      </b>
    </b>
  </b>
  <b>
    <b>
      <b>
        <node v="5"/>
      </b>
      <b>
        <node v="6"/>
      </b>
    </b>
    <b>
      <b>
        <node v="7"/>
      </b>
      <b>
        <node v="8"/>
      </b>
    </b>
  </b>
</b>"""

# Let's sum all the @v values with the use of the binary (fragment) tree:
#
# [...] the overall 'copy' complexity is O(log2(N)*N).
#
# Although the number of recursive calls is O(N) the XSLT processor still spends
# at least O(log2(N)*N) time because it must copy (and select) half of the nodes
# for the each recursive call (twice).
#
# Copying nodes should be avoided as much as possible because it slows down
# recursion considerably.
#
source_4 = expected_3

sheet_4 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  exclude-result-prefixes="exsl">

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name="btree">
        <xsl:call-template name="partition">
          <xsl:with-param name="nodes" select="//node"/>
        </xsl:call-template>
    </xsl:variable>

    <xsl:call-template name="sum-binary-tree">
      <xsl:with-param name="bnode" select="exsl:node-set($btree)/*"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="sum-binary-tree">
    <xsl:param name="bnode"/>

    <xsl:choose>
      <xsl:when test="$bnode/node">
        <xsl:value-of select="$bnode/node/@v"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="first">
          <xsl:call-template name="sum-binary-tree">
            <xsl:with-param name="bnode" select="$bnode/b[1]"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="second">
          <xsl:call-template name="sum-binary-tree">
            <xsl:with-param name="bnode" select="$bnode/b[2]"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:value-of select="$first + $second"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="partition">
    <xsl:param name="nodes"/>

    <xsl:variable name="half" select="floor(count($nodes) div 2)"/>

    <b>
      <xsl:choose>
        <xsl:when test="count($nodes) &lt;= 1">
          <!-- There is only one node left: stop dividing problem -->
          <xsl:copy-of select="$nodes"/>
        </xsl:when>
        <xsl:otherwise>
          <!-- divide in first half of nodes (left) -->
          <xsl:call-template name="partition">
            <xsl:with-param name="nodes" select="$nodes[position() &lt;= $half]"/>
          </xsl:call-template>
          <!-- divide in second half of nodes (right) -->
          <xsl:call-template name="partition">
            <xsl:with-param name="nodes" select="$nodes[position() &gt; $half]"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </b>
  </xsl:template>

</xsl:stylesheet>"""

expected_4 = "36"

# MODIFIED DVC ALGORITHM: RANGE PARTITIONING
#
# The following implementation of a binary partition doesn't copy a list of nodes
# but just one node at each recursive call. It uses the so called 'sibling' axis
# to walk through the list. Because there are O(N) recursive calls, this means
# that O(N) nodes are copied. Does this mean that the overall time complexity will
# be O(N) too? The answer is: probably yes, but at worst it will be O(N^2).
#
# Let's compare overall time complexity with the possible implementations of
# 'following-sibling::[w]'
#
# following-sibling::*[w] | total time
# _____________________________________
# O(1)                    | O(N)
# O(w)                    | O(log2(N)*N)
# O(N)                    | O(N^2)
#
# So at worst it will be quadratic. So the question still remains if it is
# theoretically possible to do binary partitioning without copying to much nodes.
# Nevertheless, experiments with XALAN have shown that the implementation is not
# quadratic.
#
source_5 = source_3

sheet_5 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <xsl:call-template name="partition-ranges">
      <xsl:with-param name="node" select="//node[1]"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="partition-ranges">
    <xsl:param name="node"/>
    <xsl:param name="s" select="(count($node/preceding-sibling::*)) + 1"/>
    <xsl:param name="e" select="(count($node/following-sibling::*)) + $s"/>

    <xsl:if test="$node">
      <xsl:element name="r">
        <xsl:attribute name="s">
          <xsl:value-of select="$s"/>
        </xsl:attribute>
        <xsl:attribute name="e">
          <xsl:value-of select="$e"/>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="$s = $e">
            <xsl:copy-of select="$node"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="w" select="floor(($e - $s + 1) div 2)"/>
            <xsl:variable name="m" select="$s + $w"/>
            <xsl:call-template name="partition-ranges">
              <xsl:with-param name="node" select="$node"/>
              <xsl:with-param name="s" select="$s"/>
              <xsl:with-param name="e" select="$m - 1"/>
            </xsl:call-template>
            <xsl:call-template name="partition-ranges">
              <xsl:with-param name="node" select="$node/following-sibling::*[$w]"/>
              <xsl:with-param name="s" select="$m"/>
              <xsl:with-param name="e" select="$e"/>
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:element>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>"""

expected_5 = """<?xml version="1.0" encoding="UTF-8"?>
<r s="1" e="8">
  <r s="1" e="4">
    <r s="1" e="2">
      <r s="1" e="1">
        <node v="1"/>
      </r>
      <r s="2" e="2">
        <node v="2"/>
      </r>
    </r>
    <r s="3" e="4">
      <r s="3" e="3">
        <node v="3"/>
      </r>
      <r s="4" e="4">
        <node v="4"/>
      </r>
    </r>
  </r>
  <r s="5" e="8">
    <r s="5" e="6">
      <r s="5" e="5">
        <node v="5"/>
      </r>
      <r s="6" e="6">
        <node v="6"/>
      </r>
    </r>
    <r s="7" e="8">
      <r s="7" e="7">
        <node v="7"/>
      </r>
      <r s="8" e="8">
        <node v="8"/>
      </r>
    </r>
  </r>
</r>"""


# GROUPING WITH A BINARY TREE
#
# The new and improved grouping algorithm is more or less the same as the first
# one except where using ranges to select nodes which are in the same group.
# Thus:
#
# 1) we sort the nodes for a given key
# 2) then compute the ranges of nodes which have the same key
# 3) and then select the (sorted) nodes for each range.
# 
# To efficiently select a range of nodes we will be using the binary tree.
#
# Here's the whole solution:
#
source_6 = source_1

sheet_6 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="yes"/>

  <!-- Group cities on country -->
  <xsl:template match="/">
    <result>
      <xsl:call-template name="group-on-key">
        <xsl:with-param name="nodes" select="//city"/>
        <xsl:with-param name="key" select="'country'"/>
      </xsl:call-template>
    </result>
  </xsl:template>

<!--
  Template: group-on-key
  Use this template to group <nodes> which share a common attribute <key>
  The result will be sub-sets of <nodes> surrounded by <group/> tags
-->


<xsl:template name="group-on-key">
  <xsl:param name="nodes"/>
  <xsl:param name="key"/>

  <xsl:variable name="items">
    <xsl:for-each select="$nodes">
      <item>
        <key>
          <xsl:value-of select="./@*[name() = $key]"/>
        </key>
        <value>
          <xsl:copy-of select="."/>
        </value>
      </item>
    </xsl:for-each>
  </xsl:variable>

  <xsl:variable name="grouped-items">
    <xsl:call-template name="group-on-item">
      <xsl:with-param name="nodes" select="exsl:node-set($items)/*"/>
      <xsl:with-param name="key" select="$key"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:for-each select="exsl:node-set($grouped-items)/*">
    <xsl:copy>
      <xsl:for-each select="./*">
        <xsl:copy-of select="./value/*[1]"/>
      </xsl:for-each>
    </xsl:copy>
  </xsl:for-each>
</xsl:template>

<!--
 Template: group-on-item
 Use this template to group <nodes> which share a common structure.
 You can build this structure yourself if you want to group on something else

 The structure is the <item> structure and has the following layout
 <item>
  <key>
   aKey (can be anything, preferrably a string)
  </key>
  <value>
   aValue (can be anything, probably a node(set))
  </value>
 </item>

 <items> will we grouped on the string value of <key>
 The result will be sub-sets of <items> surrounded by <group/> tags
-->

<xsl:template name="group-on-item">
  <xsl:param name="nodes"/>

  <!-- Step 1 -->
  <xsl:variable name="sorted">
    <xsl:for-each select="$nodes">
      <xsl:sort select="./key[1]"/>
      <xsl:copy-of select="."/>
    </xsl:for-each>
  </xsl:variable>

  <xsl:variable name="sorted-tree" select="exsl:node-set($sorted)/*"/>

  <!-- Step 2.1 -->
  <xsl:variable name="pivots">
    <xsl:call-template name="pivots">
      <xsl:with-param name="nodes" select="$sorted-tree"/>
    </xsl:call-template>
  </xsl:variable>

  <!-- Step 2.2 -->
  <xsl:variable name="ranges">
    <xsl:call-template name="ranges">
      <xsl:with-param name="pivots" select="exsl:node-set($pivots)/*"/>
      <xsl:with-param name="length" select="count($sorted-tree)"/>
    </xsl:call-template>
  </xsl:variable>

  <!-- Step 3.1 -->
  <xsl:variable name="partition-ranges">
    <xsl:call-template name="partition-ranges">
      <xsl:with-param name="node" select="$sorted-tree[1]"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="root-partition" select="exsl:node-set($partition-ranges)/*[1]"/>

  <!-- Step 3.2 -->
  <xsl:for-each select="exsl:node-set($ranges)/r">
    <xsl:variable name="s" select="./@s"/>
    <xsl:variable name="e" select="./@e"/>

    <group>
      <xsl:call-template name="range-in-partition">
        <xsl:with-param name="s" select="$s"/>
        <xsl:with-param name="e" select="$e"/>
        <xsl:with-param name="p" select="$root-partition"/>
      </xsl:call-template>
    </group>
  </xsl:for-each>

</xsl:template>

<xsl:template name="pivots">
  <xsl:param name="nodes"/>
  <xsl:param name="key"/>

  <xsl:for-each select="$nodes">
    <xsl:if test="not(string(./key[1]) = string(./following-sibling::*[1]/key[1]))">
      <pivot>
        <xsl:value-of select="position()"/>
      </pivot>
    </xsl:if>
  </xsl:for-each>
</xsl:template>

<xsl:template name="ranges">
  <xsl:param name="pivots" select=".."/>
  <xsl:param name="length" select="0"/>

  <xsl:choose>
  <xsl:when test="count($pivots) &gt;= 1">
  <xsl:for-each select="$pivots">
    <xsl:variable name="p" select="./preceding-sibling::*[1]"/>
    <r>
      <xsl:attribute name="s">
        <xsl:choose>
          <xsl:when test="$p">
            <xsl:value-of select="$p + 1"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="1"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="e">
        <xsl:value-of select="string(.)"/>
      </xsl:attribute>
    </r>
  </xsl:for-each>
  </xsl:when>
  <xsl:otherwise>
    <r>
      <xsl:attribute name="s">
        <xsl:value-of select="1"/>
      </xsl:attribute>
      <xsl:attribute name="e">
        <xsl:value-of select="$length"/>
      </xsl:attribute>
    </r>
  </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!--
 Template: range-in-partition
 Selects a RANGE of nodes using a binary tree

 XSLT isn't really helping to make things easy but try to do this in a DVC style
directly without the help of a binary tree.
-->

<xsl:template name="range-in-partition">
  <xsl:param name="p"/>
  <xsl:param name="s" select="$p/@s"/>
  <xsl:param name="e" select="$p/@e"/>

  <xsl:variable name="ps" select="number($p/@s)"/>
  <xsl:variable name="pe" select="number($p/@e)"/>

  <xsl:if test="$s &lt;= $pe and $e &gt;= $ps">
    <xsl:if test="$ps = $pe">
      <xsl:copy-of select="$p/*[1]"/>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="$s &gt; $ps">
        <xsl:variable name="s1" select="$s"/>
        <xsl:choose>
          <xsl:when test="$e &lt; $pe">
            <xsl:variable name="e1" select="$e"/>
            <xsl:for-each select="$p/*">
              <xsl:call-template name="range-in-partition">
                <xsl:with-param name="s" select="$s1"/>
                <xsl:with-param name="e" select="$e1"/>
                <xsl:with-param name="p" select="."/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="e1" select="$pe"/>
            <xsl:for-each select="$p/*">
              <xsl:call-template name="range-in-partition">
                <xsl:with-param name="s" select="$s1"/>
                <xsl:with-param name="e" select="$e1"/>
                <xsl:with-param name="p" select="."/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="s1" select="$ps"/>
        <xsl:choose>
          <xsl:when test="$e &lt; $pe">
            <xsl:variable name="e1" select="$e"/>
            <xsl:for-each select="$p/*">
              <xsl:call-template name="range-in-partition">
                <xsl:with-param name="s" select="$s1"/>
                <xsl:with-param name="e" select="$e1"/>
                <xsl:with-param name="p" select="."/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="e1" select="$pe"/>
            <xsl:for-each select="$p/*">
              <xsl:call-template name="range-in-partition">
                <xsl:with-param name="s" select="$s1"/>
                <xsl:with-param name="e" select="$e1"/>
                <xsl:with-param name="p" select="."/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:if>
</xsl:template>

  <xsl:template name="partition-ranges">
    <xsl:param name="node"/>
    <xsl:param name="s" select="(count($node/preceding-sibling::*)) + 1"/>
    <xsl:param name="e" select="(count($node/following-sibling::*)) + $s"/>

    <xsl:if test="$node">
      <xsl:element name="r">
        <xsl:attribute name="s">
          <xsl:value-of select="$s"/>
        </xsl:attribute>
        <xsl:attribute name="e">
          <xsl:value-of select="$e"/>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="$s = $e">
            <xsl:copy-of select="$node"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="w" select="floor(($e - $s + 1) div 2)"/>
            <xsl:variable name="m" select="$s + $w"/>
            <xsl:call-template name="partition-ranges">
              <xsl:with-param name="node" select="$node"/>
              <xsl:with-param name="s" select="$s"/>
              <xsl:with-param name="e" select="$m - 1"/>
            </xsl:call-template>
            <xsl:call-template name="partition-ranges">
              <xsl:with-param name="node" select="$node/following-sibling::*[$w]"/>
              <xsl:with-param name="s" select="$m"/>
              <xsl:with-param name="e" select="$e"/>
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:element>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>"""

# note this is missing the group ids as compared to the first example
#
expected_6 = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <group>
    <city name="Barcelona" country="Espana"/>
    <city name="Madrid" country="Espana"/>
  </group>
  <group>
    <city name="Paris" country="France"/>
    <city name="Lyon" country="France"/>
  </group>
  <group>
    <city name="Roma" country="Italia"/>
    <city name="Milano" country="Italia"/>
    <city name="Firenze" country="Italia"/>
    <city name="Napoli" country="Italia"/>
  </group>
</result>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='grouping without keys')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='grouping using recursion')

    source = test_harness.FileInfo(string=source_3)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='generate a binary tree')

    source = test_harness.FileInfo(string=source_4)
    sheet = test_harness.FileInfo(string=sheet_4)
    test_harness.XsltTest(tester, source, [sheet], expected_4,
                          title='sum nodes in a binary tree')

    source = test_harness.FileInfo(string=source_5)
    sheet = test_harness.FileInfo(string=sheet_5)
    test_harness.XsltTest(tester, source, [sheet], expected_5,
                          title='generate a binary tree with range partitioning')

    source = test_harness.FileInfo(string=source_6)
    sheet = test_harness.FileInfo(string=sheet_6)
    test_harness.XsltTest(tester, source, [sheet], expected_6,
                          title='efficient divide-and-conquer based grouping')

    return
