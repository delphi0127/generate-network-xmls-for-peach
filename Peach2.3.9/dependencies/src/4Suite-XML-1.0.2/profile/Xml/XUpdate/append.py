import sys, os
p = os.path.join("..","..")
sys.path.append(p)
import profile_util

from Ft.Xml import XUpdate, InputSource, Domlette
reader = XUpdate.Reader()
processor = XUpdate.Processor()

def do_append(node,isrc):
    xu = reader.fromSrc(isrc)
    processor.execute(node,xu)

   

src_2 = """\
<?xml version="1.0"?>
<addresses>
  <address>
    <town>Los Angeles</town>
  </address>
</addresses>
"""

xu_2 = """\
<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:append select="/addresses" child="last()">
    <xupdate:element name="address">
      <town>San Francisco</town>
    </xupdate:element>
  </xupdate:append>
  <xupdate:append select="/addresses" child="last()">
    <xupdate:element name="address">
      <town>Merrill</town>
    </xupdate:element>
  </xupdate:append>
  <xupdate:append select="/addresses" child="last()">
    <xupdate:element name="address">
      <town>Chicago</town>
    </xupdate:element>
  </xupdate:append>
  <xupdate:append select="/addresses">
    <address>
      <town>Vegas</town>
    </address>
  </xupdate:append>

</xupdate:modifications>
"""



def do_profile():
    
    node = Domlette.NonvalidatingReader.parseString(src_2,"dummy")
    isrc = InputSource.DefaultFactory.fromString(xu_2,"dummy")
    profile_util.run("do_append(node,isrc)",globals(),locals())


if __name__ == '__main__':
    do_profile()
