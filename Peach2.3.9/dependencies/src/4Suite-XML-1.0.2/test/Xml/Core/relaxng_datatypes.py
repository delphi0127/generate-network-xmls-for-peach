from Ft.Xml.Domlette import Print, PrettyPrint, NonvalidatingReader
from Ft.Xml.Xvif import RelaxNgValidator 
from Ft.Xml import InputSource 

RNG_1 = """\
<?xml version="1.0"?> 
    <element name="spam" xmlns="http://relaxng.org/ns/structure/1.0" datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes">
      <zeroOrMore>
        <element name="eggs"> 
          <attribute name="monty"><text/></attribute> 
            <data type="string"> 
              <param name="maxLength">10</param> 
            </data> 
        </element> 
      </zeroOrMore>
    </element> 
"""


RNG_2 = """\
<?xml version="1.0"?> 
<grammar ns="" xmlns="http://relaxng.org/ns/structure/1.0" datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes"> 
  <start>
    <element name="spam">
      <zeroOrMore>
        <element name="eggs"> 
          <attribute name="monty"><text/></attribute> 
            <data type="string"> 
              <param name="maxLength">10</param> 
            </data> 
        </element> 
      </zeroOrMore>
    </element> 
  </start>
</grammar>"""


RNG_3 = """\
<?xml version="1.0"?> 
<element name="spam" xmlns="http://relaxng.org/ns/structure/1.0" datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes">
  <zeroOrMore>
    <element name="eggs"> 
      <attribute name="monty"><text/></attribute> 
        <data type="string"> 
          <param name="pattern">(a|b|c)*</param> 
          </data> 
    </element> 
  </zeroOrMore>
</element> 
"""


DOC_1 = """\
<spam>
  <eggs monty="1"></eggs>
  <eggs monty="2">abc</eggs>
</spam>
"""

DOC_2 = """\
<spam>
  <eggs monty="1">aabbcc</eggs>
  <eggs monty="2">abcabcabcdef</eggs>
</spam>
"""

g_valid_cases = [
    ("valid string maxlength 1", RNG_1, DOC_1),
    ("valid string maxlength 2", RNG_2, DOC_1),
    ("valid string pattern", RNG_3, DOC_1),
    ]

g_invalid_cases = [
    ("invalid string maxlength", RNG_1, DOC_2),
    ("invalid string pattern", RNG_3, DOC_2),
    ]


#EXPECTED1 = """\
#"""


def Test(tester):
    tester.startGroup('RELAX NG WXS type facets')
    factory = InputSource.DefaultFactory
    
    for title, rng, doc in g_valid_cases:
        #doc = NonvalidatingReader.parseString(DOC1, __name__)
        tester.startTest(title)
        rng_isrc = factory.fromString(rng, __name__) 
        xml_isrc = factory.fromString(doc, __name__)
        validator = RelaxNgValidator(rng_isrc)
        result = not not validator.isValid(xml_isrc)
        tester.compare(True, result)
        tester.testDone()

    for title, rng, doc in g_invalid_cases:
        #doc = NonvalidatingReader.parseString(DOC1, __name__)
        tester.startTest(title)
        rng_isrc = factory.fromString(rng, __name__) 
        xml_isrc = factory.fromString(doc, __name__)
        validator = RelaxNgValidator(rng_isrc)
        result = not not validator.isValid(xml_isrc)
        tester.compare(False, result)
        tester.testDone()

    tester.groupDone()
    return

