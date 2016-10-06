#Jason Diamond's <jason@injektilo.org> tool for converting RDF to a normalized XML serilization
#See http://lists.w3.org/Archives/Public/www-rdf-interest/2000Sep/0097.html

from Xml.Xslt import test_harness

source_1 = """<?xml version="1.0" standalone="yes"?>
<rdf:RDF xmlns="http://my.netscape.com/rdf/simple/0.9/"
     xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
>
  <channel>
    <title>JavaWorld</title>
    <link>http://www.javaworld.com</link>
    <description>
      Add JavaWorld to your My Netscape page! The
      JavaWorld channel lets you stay on top of the latest
      developer tips, tutorials, news, and resources offered by
      JavaWorld.
    </description>
  </channel>
  <image>
    <title>JavaWorld Logo</title>
    <url>http://www.javaworld.com/icons/jw-mynetscape.gif</url>
    <link>http://www.javaworld.com</link>
  </image>
  <item>
    <title>&quot;Streaming JavaWorld&quot; -- the streaming audio news and talk for Java project managers</title>
    <link>http://www.javaworld.com/common/jw-streaming.html?myns</link>
  </item>
  <item>
    <title>Streaming JavaWord: An audio program for Java project managers and programmers</title>
    <link>http://www.javaworld.com/common/jw-streaming.html?myns</link>
  </item>
  <item>
    <title>Programming Java Devices: An Overview</title>
    <link>http://www.javaworld.com/jw-07-1999/jw-07-device.html?myns</link>
  </item>
  <textinput>
    <title>GO!</title>
    <description>Search JavaWorld</description>
    <name>col=jw&amp;qt</name>
    <link>http://search.javaworld.com/query.html</link>
  </textinput>
</rdf:RDF>"""

source_2 = """\
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:s="http://s.com#"
    xmlns:v="http://v.com#">

    <!-- A simple Example of a contained bag -->
    <!--  <rdf:Description about="http://mycollege.edu/courses/6.001">
        <s:students>
          <rdf:Bag>
            <rdf:li resource="http://mycollege.edu/students/Amy"/>
            <rdf:li resource="http://mycollege.edu/students/Tim"/>
            <rdf:li resource="http://mycollege.edu/students/John"/>
            <rdf:li resource="http://mycollege.edu/students/Mary"/>
            <rdf:li resource="http://mycollege.edu/students/Sue"/>
          </rdf:Bag>
        </s:students>
      </rdf:Description>-->

    <!-- A simple Example of a contained Seq -->
    <!-- <rdf:Description about="http://mycollege.edu/courses/6.002">
        <s:students>
          <rdf:Seq>
            <rdf:li resource="http://mycollege.edu/students/Amy2"/>
            <rdf:li resource="http://mycollege.edu/students/Tim2"/>
            <rdf:li resource="http://mycollege.edu/students/John2"/>
            <rdf:li resource="http://mycollege.edu/students/Mary2"/>
            <rdf:li resource="http://mycollege.edu/students/Sue2"/>
          </rdf:Seq>
        </s:students>
      </rdf:Description> -->

  <!-- A contained Alt -->
  <!-- <rdf:Description about="http://x.org/packages/X11">
      <s:DistributionSite>
        <rdf:Alt>
          <rdf:li resource="ftp://ftp.x.org"/>
          <rdf:li resource="ftp://ftp.cs.purdue.edu"/>
          <rdf:li resource="ftp://ftp.eu.net"/>
        </rdf:Alt>
      </s:DistributionSite>
    </rdf:Description> -->


    <!-- A simple Example of a contained bag with _ attrs -->
    <!-- <rdf:Description about="http://mycollege.edu/courses/6.003">
        <s:students>
          <rdf:Bag 
             rdf:_1="http://mycollege.edu/students/Amy4"
             rdf:_2="http://mycollege.edu/students/Tim4"
             rdf:_3="http://mycollege.edu/students/John4"
             rdf:_4="http://mycollege.edu/students/Mary4"
             rdf:_5="http://mycollege.edu/students/Sue4" />
        </s:students>
      </rdf:Description> -->



  <!-- top level container -->
  <rdf:Bag ID="pages">
    <rdf:li resource="http://foo.org/foo.html" />
    <rdf:li resource="http://bar.org/bar.html" />
  </rdf:Bag>

  <!-- speak about the bag -->
  <!--<rdf:Description about="#pages">
    <s:Creator>Ora Lassila</s:Creator>
  </rdf:Description>-->

  <!-- Speak about each item in the bag -->
  <!--<rdf:Description aboutEach="#pages">
    <s:Creator>Mike Olson</s:Creator>
  </rdf:Description>-->


  <!-- set up resources for aboutEachPrefix -->
  <!--<rdf:Description about="http://foo.org/doc/page1">
    <s:Copyright>1998, The Foo Organization</s:Copyright>
  </rdf:Description>
  <rdf:Description about="http://foo.org/doc/page2">
    <s:Copyright>1998, The Foo Organization</s:Copyright>
  </rdf:Description>-->

  <!-- test aboutEachPrefix  -->
  <!--<rdf:Description aboutEachPrefix="http://foo.org/doc">
    <s:Copyright>1998, The Foo Organization</s:Copyright>
  </rdf:Description>-->

  </rdf:RDF>
"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<model>
  <statement>
    <subject>anonymous:id1</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/title</predicate>
    <object type='literal'>JavaWorld</object>
  </statement>
  <statement>
    <subject>anonymous:id1</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/link</predicate>
    <object type='literal'>http://www.javaworld.com</object>
  </statement>
  <statement>
    <subject>anonymous:id1</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/description</predicate>
    <object type='literal'>
      Add JavaWorld to your My Netscape page! The
      JavaWorld channel lets you stay on top of the latest
      developer tips, tutorials, news, and resources offered by
      JavaWorld.
    </object>
  </statement>
  <statement>
    <subject>anonymous:id2</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/title</predicate>
    <object type='literal'>JavaWorld Logo</object>
  </statement>
  <statement>
    <subject>anonymous:id2</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/url</predicate>
    <object type='literal'>http://www.javaworld.com/icons/jw-mynetscape.gif</object>
  </statement>
  <statement>
    <subject>anonymous:id2</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/link</predicate>
    <object type='literal'>http://www.javaworld.com</object>
  </statement>
  <statement>
    <subject>anonymous:id3</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/title</predicate>
    <object type='literal'>"Streaming JavaWorld" -- the streaming audio news and talk for Java project managers</object>
  </statement>
  <statement>
    <subject>anonymous:id3</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/link</predicate>
    <object type='literal'>http://www.javaworld.com/common/jw-streaming.html?myns</object>
  </statement>
  <statement>
    <subject>anonymous:id4</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/title</predicate>
    <object type='literal'>Streaming JavaWord: An audio program for Java project managers and programmers</object>
  </statement>
  <statement>
    <subject>anonymous:id4</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/link</predicate>
    <object type='literal'>http://www.javaworld.com/common/jw-streaming.html?myns</object>
  </statement>
  <statement>
    <subject>anonymous:id5</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/title</predicate>
    <object type='literal'>Programming Java Devices: An Overview</object>
  </statement>
  <statement>
    <subject>anonymous:id5</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/link</predicate>
    <object type='literal'>http://www.javaworld.com/jw-07-1999/jw-07-device.html?myns</object>
  </statement>
  <statement>
    <subject>anonymous:id6</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/title</predicate>
    <object type='literal'>GO!</object>
  </statement>
  <statement>
    <subject>anonymous:id6</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/description</predicate>
    <object type='literal'>Search JavaWorld</object>
  </statement>
  <statement>
    <subject>anonymous:id6</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/name</predicate>
    <object type='literal'>col=jw&amp;qt</object>
  </statement>
  <statement>
    <subject>anonymous:id6</subject>
    <predicate>http://my.netscape.com/rdf/simple/0.9/link</predicate>
    <object type='literal'>http://search.javaworld.com/query.html</object>
  </statement>
</model>"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<model>
  <statement>
    <subject>anonymous:id1</subject>
    <predicate>http://www.w3.org/1999/02/22-rdf-syntax-ns#li</predicate>
    <object type='resource'>http://foo.org/foo.html</object>
  </statement>
  <statement>
    <subject>anonymous:id1</subject>
    <predicate>http://www.w3.org/1999/02/22-rdf-syntax-ns#li</predicate>
    <object type='resource'>http://bar.org/bar.html</object>
  </statement>
</model>"""

# "

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(uri='Xml/Xslt/Borrowed/rdftripledump.xslt')
    test_harness.XsltTest(tester, source, [sheet], expected_1)

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(uri='Xml/Xslt/Borrowed/rdftripledump.xslt')
    test_harness.XsltTest(tester, source, [sheet], expected_2)
    return
    
