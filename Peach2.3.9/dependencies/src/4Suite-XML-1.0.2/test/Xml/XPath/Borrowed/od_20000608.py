#4XPath Performance test from "Olivier Deckmyn" <odeckmyn.list@teaser.fr>, with import and filename updates
"""
Subject: [4suite] 4XPath performance ?
Date: Thu, 8 Jun 2000 16:30:21 +0200
From: "Olivier Deckmyn" <odeckmyn.list@teaser.fr>
To: "4Suite list" <4suite@dollar.fourthought.com>

I am playing and testing 4XPath....
And I am a little afraid of the results I see...
The machine is a Dell Server (2400) with a single PIII-750 and 256MB RAM,
USCSI disks (10K RPM), running FreeBSD4.

There is a lot of memory, cpu is not used for anything else than the test...

With a 100KB xml file, I have applied the attached test1.py

Here are the results :
QUERY="//author" (no match in the file)
Reading document
took 1.336457 sec
Starting query
took 307.572385 sec
Indexing DOM
took 0.125362 sec
Starting query
took 84.692544 sec

QUERY="//date" (few matches in the file)
Reading document
took 1.341848 sec
Starting query
took 308.466919 sec
<date> 10 October 1996</date><date>1 August 1996</date><date>17 April
1996</date><date> 17 April 1996</date><date> 17 April 1996</date><date> 12
April 1996</date><date>27 March 1996</date><date>27 March
1996</date><date>23 February 1996</date><date>9 December 1996</date><date>
29 November 1996</date><date> 31 October 1996</date>Indexing DOM
took 0.128668 sec
Starting query
took 85.145023 sec
<date> 10 October 1996</date><date>1 August 1996</date><date>17 April
1996</date><date> 17 April 1996</date><date> 17 April 1996</date><date> 12
April 1996</date><date>27 March 1996</date><date>27 March
1996</date><date>23 February 1996</date><date>9 December 1996</date><date>
29 November 1996</date><date> 31 October 1996</date>


Result :
Indexing is worth the price ! Very quick index build, and 3.5x speed gain
...
But, it very slow anyway :(

Is this the "normal" performance ? Can I do better?
"""


from Ft.Lib import Uri
from Ft.Xml import InputSource
from Ft.Xml.XPath import Evaluate
from Ft.Xml.XPath import Util


def dom_from_file(tester, uri):
    tester.startTest("Reading Document")
    isrc = InputSource.DefaultFactory.fromUri(uri)
    result=tester.test_data['parse'](isrc)
    tester.testDone()
    return result
    

def test_query(tester, dom_object, query):
    tester.startTest("Starting query")
    result = Evaluate(query, contextNode = dom_object.documentElement)
    tester.testDone()
    return result

def test1(tester, uri, queryString, name):

    tester.startGroup(name)
    xml_dom_object = dom_from_file(tester, uri)

    test_query(tester, xml_dom_object, queryString)
    
    tester.groupDone()


def Test(tester):
    base = Uri.OsPathToUri(__file__, attemptAbsolute=True)
    uri = Uri.Absolutize('od_20000608.xml', base)
    test1(tester, uri, '//author', 'no match')
    test1(tester, uri, '//date', 'Some Matches')
    return
