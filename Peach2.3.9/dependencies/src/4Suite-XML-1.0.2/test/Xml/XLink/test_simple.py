import cStringIO
from Ft.Lib import Uri
from Ft.Xml.Domlette import Print
from Ft.Xml import InputSource
from Ft.Xml.Lib import TreeCompare

# whitespace is significant!!

EXPECTED_1 = """<?xml version="1.0" encoding="utf-8"?>
<ADDRBOOK xmlns:xlink='http://www.w3.org/1999/xlink'>
  <ENTRY ID='pa'>
    <NAME>Pieter Aaron</NAME>
    <ADDRESS>404 Error Way</ADDRESS>
    <PHONENUM DESC='Work'>404-555-1234</PHONENUM>
    <PHONENUM DESC='Fax'>404-555-4321</PHONENUM>
    <PHONENUM DESC='Pager'>404-555-5555</PHONENUM>
    <EMAIL>pieter.aaron@inter.net</EMAIL>
  </ENTRY>
  <ADDRBOOK>
  <ENTRY ID='gn'>
    <NAME>Gegbefuna Nwannem</NAME>
    <ADDRESS>666 Murtala Mohammed Blvd.</ADDRESS>
    <PHONENUM DESC='Home'>999-101-1001</PHONENUM>
    <EMAIL>nwanneg@naija.ng</EMAIL>
  </ENTRY>
</ADDRBOOK>
  <ENTRY ID='en'>
    <NAME>Emeka Ndubuisi</NAME>
    <ADDRESS>42 Spam Blvd</ADDRESS>
    <PHONENUM DESC='Work'>767-555-7676</PHONENUM>
    <PHONENUM DESC='Fax'>767-555-7642</PHONENUM>
    <PHONENUM DESC='Pager'>800-SKY-PAGEx767676</PHONENUM>
    <EMAIL>endubuisi@spamtron.com</EMAIL>
  </ENTRY>
  <ENTRY ID='vz'>
    <NAME>Vasia Zhugenev</NAME>
    <ADDRESS>2000 Disaster Plaza</ADDRESS>
    <PHONENUM DESC='Work'>000-987-6543</PHONENUM>
    <PHONENUM DESC='Cell'>000-000-0000</PHONENUM>
    <EMAIL>vxz@magog.ru</EMAIL>
  </ENTRY>
</ADDRBOOK>"""


EXPECTED_2 = """<?xml version="1.0" encoding="UTF-8"?>
<ADDRBOOK xmlns:xlink="http://www.w3.org/1999/xlink">
  <ENTRY ID="pa">
    <NAME>Pieter Aaron</NAME>
    <ADDRESS>404 Error Way</ADDRESS>
    <PHONENUM DESC="Work">404-555-1234</PHONENUM>
    <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
    <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
    <EMAIL>pieter.aaron@inter.net</EMAIL>
  </ENTRY>
  """"""
  <ENTRY ID="gn">
    <NAME>Gegbefuna Nwannem</NAME>
    <ADDRESS>666 Murtala Mohammed Blvd.</ADDRESS>
    <PHONENUM DESC="Home">999-101-1001</PHONENUM>
    <EMAIL>nwanneg@naija.ng</EMAIL>
  </ENTRY>

  <ENTRY ID="en">
    <NAME>Emeka Ndubuisi</NAME>
    <ADDRESS>42 Spam Blvd</ADDRESS>
    <PHONENUM DESC="Work">767-555-7676</PHONENUM>
    <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
    <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
    <EMAIL>endubuisi@spamtron.com</EMAIL>
  </ENTRY>
  """"""
  <ENTRY ID="gn">
    <NAME>Gegbefuna Nwannem</NAME>
    <ADDRESS>666 Murtala Mohammed Blvd.</ADDRESS>
    <PHONENUM DESC="Home">999-101-1001</PHONENUM>
    <EMAIL>nwanneg@naija.ng</EMAIL>
  </ENTRY>
<ENTRY ID="vz">
    <NAME>Vasia Zhugenev</NAME>
    <ADDRESS>2000 Disaster Plaza</ADDRESS>
    <PHONENUM DESC="Work">000-987-6543</PHONENUM>
    <PHONENUM DESC="Cell">000-000-0000</PHONENUM>
    <EMAIL>vxz@magog.ru</EMAIL>
  </ENTRY>
</ADDRBOOK>"""

def Test(tester):
    base = Uri.OsPathToUri(__file__, attemptAbsolute=True)

    tester.startGroup('Simple XLinks')
    from Ft.Xml.XLink.Processor import Processor

    tester.startTest('Process w/xlink:show="embed"')
    uri1 = Uri.Absolutize('addr_book1.xml', base)
    isrc = InputSource.DefaultFactory.fromUri(uri1)
    p = Processor()
    doc = p.run(isrc)
    stream = cStringIO.StringIO()
    Print(doc, stream)
    actual = stream.getvalue()
    tester.compare(EXPECTED_1, actual, func=TreeCompare.TreeCompare)
    tester.testDone()

    tester.startTest('Process w/xlink:show="replace"')
    uri3 = Uri.Absolutize('addr_book3.xml', base)
    isrc = InputSource.DefaultFactory.fromUri(uri3)
    p = Processor()
    doc = p.run(isrc)
    stream = cStringIO.StringIO()
    Print(doc, stream)
    actual = stream.getvalue()
    tester.compare(EXPECTED_2, actual, func=TreeCompare.TreeCompare)
    tester.testDone()

    return tester.groupDone()
