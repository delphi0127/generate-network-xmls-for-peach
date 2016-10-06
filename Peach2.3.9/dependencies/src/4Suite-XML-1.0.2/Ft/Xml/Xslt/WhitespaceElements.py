from Ft.Xml.Xslt import XsltElement, XsltException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes
from Ft.Xml.Xslt import ContentInfo, AttributeInfo

class WhitespaceElement(XsltElement):

    category = CategoryTypes.TOP_LEVEL_ELEMENT
    content = ContentInfo.Empty
    legalAttrs = {
        'elements' : AttributeInfo.Tokens(required=1),
        }

    _strip_whitespace = None

    def getWhitespaceInfo(self):
        return (self._strip_whitespace, self._elements)

class PreserveSpaceElement(WhitespaceElement):
    _strip_whitespace = 0

class StripSpaceElement(WhitespaceElement):
    _strip_whitespace = 1
