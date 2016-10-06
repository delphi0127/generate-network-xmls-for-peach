

#From the spec (and a few more)
pointers = [('xpointer(id("list37")/item)',
             'xpointer(id("list37")/child::item)'),
            ('xpointer(id("list37")/item[1]/range-to(following-sibling::item[2]))',
             'xpointer(id("list37")/child::item[1]/range-to(following-sibling::item[2]))'),
            ('xpointer(id("chap1"))xpointer(//*[@id="chap1"])',
             'xpointer(id("chap1")) xpointer(//child::*[attribute::id = "chap1"])'),
            ('intro',
             'intro'),
            ('xpointer(id("intro"))',
             'xpointer(id("intro"))'),
            ('element(intro/14/3)',
             'element(intro/14/3)'),
            ('element(/1/2/5/14/3)',
             'element(/1/2/5/14/3)'),
            ('xpointer(//x:a)',
             'xpointer(//child::x:a)'),
            ('xmlns(x=http://example.com/foo) xpointer(//x:a)',
             'xmlns(x=http://example.com/foo) xpointer(//child::x:a)'),
            ('xmlns(x=http://example.com/foo) xmlns(y=http://examples.org/bar) xpointer(//x:a/y:a)',
             'xmlns(x=http://example.com/foo) xmlns(y=http://examples.org/bar) xpointer(//child::x:a/child::y:a)'),
            ('xpointer(id("chap1")/range-to(id("chap2")))',
             'xpointer(id("chap1")/range-to(id("chap2")))'),
            ('xpointer(descendant::REVST/range-to(following::REVEND[1]))',
             'xpointer(descendant::REVST/range-to(following::REVEND[1]))'),
            ('xpointer(string-range(//title,"Thomas Pynchon")[17])',
             'xpointer(string-range(//child::title, "Thomas Pynchon")[17])'),
            ('xpointer(string-range(//title,"Thomas Pynchon",8,0)[3])',
             'xpointer(string-range(//child::title, "Thomas Pynchon", 8, 0)[3])'),
            ('xpointer(string-range(string-range(//P,"Thomas Pynchon")[3],"P",1,0))',
             'xpointer(string-range(string-range(//child::P, "Thomas Pynchon")[3], "P", 1, 0))'),
            ('xpointer(string-range(/,"!",1,2)[5])',
             'xpointer(string-range(/, "!", 1, 2)[5])'),
            ('xpointer(here()/ancestor::slide[1]/preceding::slide[1])',
             'xpointer(here()/ancestor::slide[1]/preceding::slide[1])'),
            ('xmlns(x=foo.com) xpointer(1)',
             'xmlns(x=foo.com) xpointer(1)'),
            ('xpointer(range-to(range-to(foo)))',
             'xpointer(range-to(range-to(child::foo)))'),
            ]


def Test(tester):
    from Ft.Xml.XPointer import XPointerParser
    for ptr, expected in pointers:
        tester.startTest(ptr)
        result = XPointerParser.new().parse(ptr)
        tester.compare(expected, repr(result))
        tester.testDone()
    return
