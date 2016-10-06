
from Ft.Lib import Set

def test_intersection(tester):

    tester.startTest("Intersection")
    a = [1,2,3]
    b = [2,3,4]
    res = Set.Intersection(a,b)
    tester.compare(2,len(res))
    tester.compareIn(res,2)
    tester.compareIn(res,3)
    tester.testDone()    

def test_not(tester):

    tester.startTest("Not")
    a = [1,2,3]
    b = [2,3,4]
    res = Set.Not(a,b)
    tester.compare(1,len(res))
    tester.compareIn(res,1)
    tester.testDone()    

def test_union(tester):

    tester.startTest("Union")
    a = [1,2,3]
    b = [2,3,4]
    res = Set.Union(a,b)
    tester.compare(4,len(res))
    tester.compareIn(res,1)
    tester.compareIn(res,2)
    tester.compareIn(res,3)
    tester.compareIn(res,4)
    tester.testDone()    

def test_unique(tester):

    tester.startTest("Unique")
    a = [1,2,3,2]
    res = Set.Unique(a)
    tester.compare(3,len(res))
    tester.compareIn(res,1)
    tester.compareIn(res,2)
    tester.compareIn(res,3)
    tester.testDone()    


def Test(tester):

    test_intersection(tester)
    test_not(tester)
    test_union(tester)
    test_unique(tester)
