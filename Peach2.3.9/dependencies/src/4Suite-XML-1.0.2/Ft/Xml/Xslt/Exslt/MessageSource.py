from Ft import TranslateMessage as _

# this works around a circular import
from Ft.Xml.Xslt.MessageSource import g_errorMessages

class Error:

    UNSUPPORTED_DOCUMENT_URI_SCHEME = 3000
    ABORTED_EXSLDOCUMENT_OVERWRITE = 3010
    NO_EXSLTDOCUMENT_BASE_URI = 3020

    ILLEGAL_DURATION_FORMAT = 3100

    RESULT_NOT_IN_FUNCTION = 3200
    ILLEGAL_RESULT_SIBLINGS = 3201


g_exsltErrorMessages = {
    Error.UNSUPPORTED_DOCUMENT_URI_SCHEME: _('4Suite\'s implementation of exsl:document only supports an href value having the "file" URI scheme, which may be implicit. Scheme "%s" was found.'),
    Error.ABORTED_EXSLDOCUMENT_OVERWRITE: _('An attempt was made to write to %s, which already exists.  The attempt to save the contents of this file to %s also failed, and so the instruction has been aborted.  If you are sure it is OK to overwrite this file, please indicate this by adding the f:overwrite-okay attribute to the exsl:document instruction.'),
    Error.NO_EXSLTDOCUMENT_BASE_URI: _('An `exsl:document` element referred to a relative reference "%s", but there is no explicit output document to provide a base URI in order to resolve this relative reference.'),
    Error.ILLEGAL_DURATION_FORMAT: _('Duration string "%s" not in xs:duration format.'),
    Error.RESULT_NOT_IN_FUNCTION: _('An EXSLT func:result element must occur within a func:function element.'),
    Error.ILLEGAL_RESULT_SIBLINGS: _('An EXSLT func:result element must not have following sibling elements besides xsl:fallback.'),
}

g_errorMessages.update(g_exsltErrorMessages)


