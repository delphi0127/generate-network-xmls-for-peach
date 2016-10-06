source = """<?xml version = "1.0"?>
<ADDRBOOK>
    <ENTRY ID="pa">
        <NAME>Pieter Aaron</NAME>
        <ADDRESS>404 Error Way</ADDRESS>
        <PHONENUM DESC="Work">404-555-1234</PHONENUM>
        <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
        <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
        <EMAIL>pieter.aaron@inter.net</EMAIL>
    </ENTRY>
    <ENTRY ID="en">
        <NAME>Emeka Ndubuisi</NAME>
        <ADDRESS>42 Spam Blvd</ADDRESS>
        <PHONENUM DESC="Work">767-555-7676</PHONENUM>
        <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
        <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
        <EMAIL>endubuisi@spamtron.com</EMAIL>
    </ENTRY>
    <ENTRY ID="vz">
        <NAME>Vasia Zhugenev</NAME>
        <ADDRESS>2000 Disaster Plaza</ADDRESS>
        <PHONENUM DESC="Work">000-987-6543</PHONENUM>
        <PHONENUM DESC="Cell">000-000-0000</PHONENUM>
        <EMAIL>vxz@magog.ru</EMAIL>
    </ENTRY>
</ADDRBOOK>"""

from Ft.Xml import Domlette, InputSource
from xml.dom import Node

def ReadDoc():
    global ADDRBOOK
    global ENTRIES
    global PA
    global PA_NAME
    global PA_ADDR
    global PA_WORK
    global PA_FAX
    global PA_PAGER
    global PA_EMAIL
    global EN
    global EN_NAME
    global EN_ADDR
    global EN_WORK
    global EN_FAX
    global EN_PAGER
    global EN_EMAIL
    global VZ
    
    isrc = InputSource.DefaultFactory.fromString(source, "addrbook.xml")
    doc = Domlette.NonvalParse(isrc)
    ADDRBOOK = doc.documentElement
    elements_only = lambda n, nt=Node.ELEMENT_NODE: n.nodeType == nt
    ENTRIES = filter(elements_only, ADDRBOOK.childNodes)

    PA = ENTRIES[0]
    children = filter(elements_only, PA.childNodes)
    PA_NAME = children[0]
    PA_ADDR = children[1]
    PA_WORK = children[2]
    PA_FAX = children[3]
    PA_PAGER = children[4]
    PA_EMAIL = children[5]

    EN = ENTRIES[1]
    children = filter(elements_only, EN.childNodes)
    EN_NAME = children[0]
    EN_ADDR = children[1]
    EN_WORK = children[2]
    EN_FAX = children[3]
    EN_PAGER = children[4]
    EN_EMAIL = children[5]
    
    VZ = ENTRIES[2]

    return doc


try:
    from xml.dom.Range import Range
except ImportError:
    Range = None

def Test(tester):

    tester.startGroup('DOM Level II Ranges')

    if Range is None:
        tester.warning("PyXML needed to test Ranges")
        tester.groupDone()
        return


    tester.startTest('Creating test environment')
    doc = ReadDoc()
    tester.testDone()


    tester.startTest("Compare Positions")
    range = doc.createRange()

    #CASE 1
    tester.compare(Range.POSITION_EQUAL,range._Range__comparePositions(ADDRBOOK,0,ADDRBOOK,0))
    tester.compare(Range.POSITION_LESS_THAN,range._Range__comparePositions(ADDRBOOK,0,ADDRBOOK,1))
    tester.compare(Range.POSITION_GREATER_THAN,range._Range__comparePositions(ADDRBOOK,1,ADDRBOOK,0))

    #CASE 2
    tester.compare(Range.POSITION_LESS_THAN,range._Range__comparePositions(ADDRBOOK,0,EN,1))
    tester.compare(Range.POSITION_LESS_THAN,range._Range__comparePositions(ADDRBOOK,3,EN,1))
    tester.compare(Range.POSITION_GREATER_THAN,range._Range__comparePositions(ADDRBOOK,5,EN,1))
    #CASE 3
    tester.compare(Range.POSITION_GREATER_THAN,range._Range__comparePositions(EN,1,ADDRBOOK,0))
    tester.compare(Range.POSITION_GREATER_THAN,range._Range__comparePositions(EN,1,ADDRBOOK,3))
    tester.compare(Range.POSITION_LESS_THAN,range._Range__comparePositions(EN,1,ADDRBOOK,5))
    
    #CASE 4
    tester.compare(Range.POSITION_LESS_THAN,range._Range__comparePositions(PA,0,EN_NAME,0))
    tester.compare(Range.POSITION_GREATER_THAN,range._Range__comparePositions(EN,0,PA_NAME,0))

    #Test with one as doc
    tester.compare(Range.POSITION_LESS_THAN,range._Range__comparePositions(doc,0,EN_NAME,0))
    tester.testDone()

    tester.startTest("Range.setStart")
    range.setStart(PA,1)
    tester.compare(PA,range.startContainer,msg='setStart 1')
    tester.compare(1,range.startOffset,msg='setStart 2')
    tester.compare(PA,range.endContainer,msg='setStart 3')
    tester.compare(1,range.endOffset,msg='setStart 4')
    tester.compare(PA,range.commonAncestorContainer,msg='setStart 5')
    tester.compare(1,range.collapsed,msg='collapsed')
    tester.testDone()

    tester.startTest("Range.setEnd")
    range.setEnd(PA_NAME,1)
    tester.compare(PA,range.startContainer,msg='setEnd 1')
    tester.compare(1,range.startOffset,msg='setEnd 2')
    tester.compare(PA_NAME,range.endContainer,msg='setEnd 3')
    tester.compare(1,range.endOffset,msg='setEnd 4')
    tester.compare(PA,range.commonAncestorContainer,msg='setEnd 5')
    tester.compare(0,range.collapsed,msg='collapsed')

    range.setEnd(EN_NAME,1)
    tester.compare(PA,range.startContainer,msg='setEnd 6')
    tester.compare(1,range.startOffset,msg='setEnd 7')
    tester.compare(EN_NAME,range.endContainer,msg='setEnd 8')
    tester.compare(1,range.endOffset,msg='setEnd 9')
    tester.compare(ADDRBOOK,range.commonAncestorContainer,msg='setEnd 10')
    tester.compare(0,range.collapsed,msg='collapsed')

    range.setEnd(doc,0)
    tester.compare(doc,range.startContainer,msg='setEnd 11')
    tester.compare(0,range.startOffset,msg='setEnd 12')
    tester.compare(doc,range.endContainer,msg='setEnd 13')
    tester.compare(0,range.endOffset,msg='setEnd 14')
    tester.compare(doc,range.commonAncestorContainer,msg='setEnd 15')
    tester.compare(1,range.collapsed,msg='collapsed')
    tester.testDone()

    tester.startTest("setStartAfter")
    range.setEnd(EN_NAME,1)
    range.setStartAfter(EN)
    tester.compare(ADDRBOOK,range.startContainer,msg='startAfter 1')
    tester.compare(4,range.startOffset,msg='startAfter 2')
    tester.compare(ADDRBOOK,range.commonAncestorContainer,msg='startAfter 3')
    tester.testDone()

    tester.startTest("setStartBefore")
    range.setStartBefore(EN)
    range.setEnd(EN_NAME,1)
    tester.compare(ADDRBOOK,range.startContainer,msg='startBefore 1')
    tester.compare(3,range.startOffset,msg='startBefore 2')
    tester.compare(ADDRBOOK,range.commonAncestorContainer,msg='startBefore 3')
    tester.testDone()

    tester.startTest("setEndAfter")
    range.setStart(ADDRBOOK,0)
    range.setEndAfter(EN_NAME)
    tester.compare(EN,range.endContainer,msg='endAfter 1')
    tester.compare(2,range.endOffset,msg='endAfter 2')
    tester.compare(ADDRBOOK,range.commonAncestorContainer,msg='endAfter 3')
    tester.testDone()

    tester.startTest("setEndBefore")
    range.setStart(ADDRBOOK,0)
    range.setEndBefore(EN_NAME)
    tester.compare(EN,range.endContainer,msg='endBefore 1')
    tester.compare(1,range.endOffset,msg='endBefore 2')
    tester.compare(ADDRBOOK,range.commonAncestorContainer,msg='endBefore 3')
    tester.testDone()

    tester.startTest("collapse")
    range.setStart(ADDRBOOK,0)
    range.setEndBefore(EN_NAME)
    range.collapse(1)
    tester.compare(ADDRBOOK,range.startContainer,msg='collapse 1')
    tester.compare(0,range.startOffset,msg='collapse 2')
    tester.compare(ADDRBOOK,range.endContainer,msg='collapse 3')
    tester.compare(0,range.endOffset,msg='collapse 4')
    range.setStart(ADDRBOOK,0)
    range.setEndBefore(EN_NAME)
    range.collapse(0)
    tester.compare(EN,range.startContainer,msg='collapse 5')
    tester.compare(1,range.startOffset,msg='collapse 6')
    tester.compare(EN,range.endContainer,msg='collapse 7')
    tester.compare(1,range.endOffset,msg='collapse 8')
    tester.testDone()

    tester.startTest("selectNode")
    range.selectNode(EN)
    tester.compare(ADDRBOOK,range.startContainer,msg='selectNode 1')
    tester.compare(3,range.startOffset,msg='selectNode 2')
    tester.compare(ADDRBOOK,range.endContainer,msg='selectNode 3')
    tester.compare(4,range.endOffset,msg='selectNode 4')
    tester.testDone()

    tester.startTest("selectNodeContents")
    range.selectNodeContents(EN)
    tester.compare(EN,range.startContainer,msg='selectNodeContents 1')
    tester.compare(0,range.startOffset,msg='selectNodeContents 2')
    tester.compare(EN,range.endContainer,msg='selectNodeContents 3')
    tester.compare(13,range.endOffset,msg='selectNodeContents 4')
    tester.testDone()

    tester.startTest("compareBoundaryPoints")
    range.selectNodeContents(EN)
    r2 = doc.createRange()
    r2.selectNode(PA)

    tester.compare(1,range.compareBoundaryPoints(range.START_TO_START,r2))
    tester.compare(1,range.compareBoundaryPoints(range.START_TO_END,r2))
    tester.compare(1,range.compareBoundaryPoints(range.END_TO_START,r2))
    tester.compare(1,range.compareBoundaryPoints(range.END_TO_END,r2))
    tester.testDone()


    tester.startTest("deleteContents")
    range.setStart(EN_NAME.firstChild,2)
    range.setEnd(EN_NAME.firstChild,11)

    range.deleteContents()

    tester.compare('Emsi',EN_NAME.firstChild.data,msg='deleteContents 1')

    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(EN,2)
    range.setEnd(EN,12)

    range.deleteContents()

    tester.compare(2,len(EN.childNodes),msg='deleteContents 2')
    tester.compare(EN_NAME,EN.childNodes[1],msg='deleteContents 3')


    #Start is the ancestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(ADDRBOOK,0)
    range.setEnd(EN_PAGER,1)

    range.deleteContents()

    tester.compare(4,len(ADDRBOOK.childNodes),msg='deleteContents 4')
    tester.compare(4,len(EN.childNodes),msg='deleteContents 5')
    tester.compare(EN_PAGER,EN.childNodes[0],msg='deleteContents 6')
    tester.compare(None,EN.childNodes[0].firstChild,msg='deleteContents 7')


    #End is the acnestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME,0)
    range.setEnd(ADDRBOOK,4)

    range.deleteContents()

    tester.compare(4,len(ADDRBOOK.childNodes),msg='deleteContents 18')
    tester.compare(2,len(PA.childNodes),msg='deleteContents 19')
    tester.compare(PA_NAME,PA.childNodes[1],msg='deleteContents 20')
    tester.compare(None,PA.childNodes[1].firstChild,msg='deleteContents 21')


    #Text to text deep ancestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME.firstChild,2)
    range.setEnd(EN_PAGER.firstChild,4)

    range.deleteContents()


    tester.compare(2,len(PA.childNodes),msg='deleteContents 2')
    tester.compare(PA_NAME,PA.childNodes[1],msg='deleteContents 3')
    tester.compare(6,len(ADDRBOOK.childNodes),msg='deleteContents 4')
    tester.compare(4,len(EN.childNodes),msg='deleteContents 5')
    tester.compare(EN_PAGER,EN.childNodes[0],msg='deleteContents 6')


    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME,0)
    range.setEnd(EN_PAGER,1)

    range.deleteContents()

    tester.compare(2,len(PA.childNodes),msg='deleteContents 7')
    tester.compare(PA_NAME,PA.childNodes[1],msg='deleteContents 8')
    tester.compare(None,PA.childNodes[1].firstChild,msg='deleteContents 9')
    tester.compare(6,len(ADDRBOOK.childNodes),msg='deleteContents 10')
    tester.compare(4,len(EN.childNodes),msg='deleteContents 11')
    tester.compare(EN_PAGER,EN.childNodes[0],msg='deleteContents 12')
    tester.compare(None,EN.childNodes[0].firstChild,msg='deleteContents 13')


    tester.testDone()

    tester.startTest("Range.extractContents")

    #Test two text nodes same
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(EN_NAME.firstChild,2)
    range.setEnd(EN_NAME.firstChild,11)

    df = range.extractContents()

    tester.compare('Emsi',EN_NAME.firstChild.data,msg='extractContents 1')
    tester.compare(1,len(df.childNodes),msg='extractContents 2')
    tester.compare('eka Ndubui',df.childNodes[0].data,msg='extractContents 3')

    #Two elements, same node
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(EN,2)
    range.setEnd(EN,12)

    df = range.extractContents()

    tester.compare(2,len(EN.childNodes),msg='extractContents 4')
    tester.compare(EN_NAME,EN.childNodes[1],msg='extractContents 5')
    tester.compare(11,len(df.childNodes),msg='extractContents 6')
    tester.compare(EN_ADDR,df.childNodes[1],msg='extractContents 7')
    tester.compare(EN_EMAIL,df.childNodes[9],msg='extractContents 8')


    #Start is the ancestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(ADDRBOOK,0)
    range.setEnd(EN_PAGER,1)

    df = range.extractContents()

    tester.compare(4,len(ADDRBOOK.childNodes),msg='extractContents 9')
    tester.compare(4,len(EN.childNodes),msg='extractContents 10')
    tester.compare(EN_PAGER,EN.childNodes[0],msg='extractContents 11')
    tester.compare(None,EN.childNodes[0].firstChild,msg='extractContents 12')
    tester.compare(4,len(df.childNodes),msg='extractContents 13')

    #End is the acnestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME,0)
    range.setEnd(ADDRBOOK,4)

    df = range.extractContents()


    tester.compare(4,len(ADDRBOOK.childNodes),msg='extractContents 14')
    tester.compare(2,len(PA.childNodes),msg='extractContents 15')
    tester.compare(PA_NAME,PA.childNodes[1],msg='extractContents 16')
    tester.compare(None,PA.childNodes[1].firstChild,msg='extractContents 17')
    tester.compare(4,len(df.childNodes),msg='extractContents 18')





    #Text to text deep ancestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME.firstChild,2)
    range.setEnd(EN_PAGER.firstChild,4)

    df = range.extractContents()


    tester.compare(2,len(PA.childNodes),msg='extractContents 19')
    tester.compare(PA_NAME,PA.childNodes[1],msg='extractContents 20')
    tester.compare(6,len(ADDRBOOK.childNodes),msg='extractContents 21')
    tester.compare(4,len(EN.childNodes),msg='extractContents 22')
    tester.compare(EN_PAGER,EN.childNodes[0],msg='extractContents 23')
    tester.compare(3,len(df.childNodes),msg='extractContents 24')



    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME,0)
    range.setEnd(EN_PAGER,1)

    df = range.extractContents()

    tester.compare(2,len(PA.childNodes),msg='extractContents 25')
    tester.compare(PA_NAME,PA.childNodes[1],msg='extractContents 26')
    tester.compare(None,PA.childNodes[1].firstChild,msg='extractContents 27')
    tester.compare(6,len(ADDRBOOK.childNodes),msg='extractContents 28')
    tester.compare(4,len(EN.childNodes),msg='extractContents 29')
    tester.compare(EN_PAGER,EN.childNodes[0],msg='extractContents 30')
    tester.compare(None,EN.childNodes[0].firstChild,msg='extractContents 31')
    tester.compare(3,len(df.childNodes),msg='extractContents 32')


    tester.testDone()


    tester.startTest("cloneContents")

    #Test two text nodes same
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(EN_NAME.firstChild,2)
    range.setEnd(EN_NAME.firstChild,11)

    df = range.cloneContents()


    tester.compare('Emeka Ndubuisi',EN_NAME.firstChild.data,msg='cloneContents 1')
    tester.compare(1,len(df.childNodes),msg='cloneContents 2')
    tester.compare('eka Ndubui',df.childNodes[0].data,msg='cloneContents 3')



    #Two elements, same node
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(EN,2)
    range.setEnd(EN,12)

    df = range.cloneContents()


    tester.compare(13,len(EN.childNodes),msg='cloneContents 4')
    tester.compare(EN_NAME,EN.childNodes[1],msg='cloneContents 5')
    tester.compare(11,len(df.childNodes),msg='cloneContents 6')
    tester.compare('42 Spam Blvd',df.childNodes[1].firstChild.data,msg='cloneContents 7')
    tester.compare('endubuisi@spamtron.com',df.childNodes[9].firstChild.data,msg='cloneContents 8')


    #Start is the ancestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(ADDRBOOK,0)
    range.setEnd(EN_PAGER,1)

    df = range.cloneContents()
    tester.compare(7,len(ADDRBOOK.childNodes),msg='cloneContents 9')
    tester.compare(13,len(EN.childNodes),msg='cloneContents 10')
    tester.compare(EN_PAGER,EN.childNodes[9],msg='cloneContents 11')
    tester.compare('800-SKY-PAGEx767676',EN_PAGER.firstChild.data,msg='cloneContents 12')
    tester.compare(4,len(df.childNodes),msg='cloneContents 13')


    #End is the acnestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME,0)
    range.setEnd(ADDRBOOK,4)

    df = range.cloneContents()


    tester.compare(7,len(ADDRBOOK.childNodes),msg='cloneContents 14')
    tester.compare(13,len(PA.childNodes),msg='cloneContents 15')
    tester.compare(PA_NAME,PA.childNodes[1],msg='cloneContents 16')
    tester.compare('Pieter Aaron',PA_NAME.firstChild.data,msg='cloneContents 17')
    tester.compare(4,len(df.childNodes),msg='cloneContents 18')


    #Text to text deep ancestor
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME.firstChild,2)
    range.setEnd(EN_PAGER.firstChild,4)

    df = range.cloneContents()


    tester.compare(13,len(PA.childNodes),msg='cloneContents 19')
    tester.compare(PA_NAME,PA.childNodes[1],msg='cloneContents 20')
    tester.compare(7,len(ADDRBOOK.childNodes),msg='cloneContents 21')
    tester.compare(13,len(EN.childNodes),msg='cloneContents 22')
    tester.compare(EN_PAGER,EN.childNodes[9],msg='cloneContents 23')
    tester.compare(3,len(df.childNodes),msg='cloneContents 24')


    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME,0)
    range.setEnd(EN_PAGER,1)

    df = range.cloneContents()

    tester.compare(13,len(PA.childNodes),msg='cloneContents 25')
    tester.compare(PA_NAME,PA.childNodes[1],msg='cloneContents 26')
    tester.compare(7,len(ADDRBOOK.childNodes),msg='cloneContents 27')
    tester.compare(13,len(EN.childNodes),msg='cloneContents 29')
    tester.compare(EN_PAGER,EN.childNodes[9],msg='cloneContents 30')
    tester.compare(3,len(df.childNodes),msg='cloneContents 32')


    tester.testDone()

    tester.startTest("Range.insertNode")
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA_NAME.firstChild,1)
    range.setEnd(EN_PAGER,1)

    newNode = doc.createElementNS(None, 'FOO')

    range.insertNode(newNode)

    tester.compare(3,len(PA_NAME.childNodes),msg='insertNode 1')
    tester.compare('P',PA_NAME.firstChild.data,msg='insertNode 2')
    tester.compare(newNode,PA_NAME.childNodes[1],msg='insertNode 3')
    

    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA,1)
    range.setEnd(EN_PAGER,1)

    newNode = doc.createElementNS(None, 'FOO')

    range.insertNode(newNode)

    tester.compare(14,len(PA.childNodes),msg='insertNode 3')
    tester.compare(newNode,PA.childNodes[2],msg='insertNode 4')
    
    tester.testDone()


    tester.startTest("Range.surroundContents")
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA,0)
    range.setEnd(PA,9)

    newNode = doc.createElementNS(None, 'FOO')

    range.surroundContents(newNode)


    #I think these results are wrong because extractContent does not collapse properly

    tester.compare(4,len(PA.childNodes),msg='insertNode 1')
    tester.compare(newNode,PA.childNodes[1],msg='insertNode 2')
    tester.testDone()


    tester.startTest("Range.cloneRange")
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA,0)
    range.setEnd(PA,9)

    newRange = range.cloneRange()

    tester.compare(newRange.endOffset,range.endOffset,msg='cloneRange 1')
    tester.compare(newRange.endContainer,range.endContainer,msg='cloneRange 2')
    tester.compare(newRange.startOffset,range.startOffset,msg='cloneRange 3')
    tester.compare(newRange.startContainer,range.startContainer,msg='cloneRange 4')
    tester.compare(newRange.collapsed,range.collapsed,msg='cloneRange 5')
    tester.compare(newRange.commonAncestorContainer,range.commonAncestorContainer,msg='cloneRange 6')
    tester.testDone()

    tester.startTest("Range.toString")
    doc = ReadDoc()
    range = doc.createRange()
    range.setStart(PA,0)
    range.setEnd(PA,9)

    range.toString()

    range.setStart(PA_NAME.firstChild,3)
    range.setEnd(EN_EMAIL.firstChild,9)

    range.toString()

    tester.testDone()

    tester.startTest("Range.detach")

    doc = ReadDoc()
    range = doc.createRange()
    range.detach()
    from xml.dom import InvalidStateErr

    try:
        print range.startOffset
    except InvalidStateErr, e:
        tester.testDone
    else:
        tester.testError()

    tester.groupDone()


if __name__ == '__main__':
    from Ft.Lib.TestSuite import Tester
    tester = Tester.Tester()
    Test(tester)
