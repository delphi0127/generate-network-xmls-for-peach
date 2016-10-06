from Ft.Xml.Domlette import implementation
from Ft.Xml.XPath import Compile, ParsedAbsoluteLocationPath

def test_compile(tester):

    tester.startTest("Compile")
    exp = Compile("/")
    tester.compare(True, isinstance(exp,ParsedAbsoluteLocationPath.ParsedAbsoluteLocationPath))
    tester.testDone()

def Test(tester):
    test_compile(tester)
