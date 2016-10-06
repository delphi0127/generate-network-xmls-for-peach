########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/Gettext.py,v 1.2 2006/08/13 22:44:33 jkloth Exp $
"""
Internationalization and localization support.

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os
import sys
import gettext
from Ft.Lib import ImportUtil

__all__ = ['GetTranslation']

if sys.version < '2.3':
    def test(condition, true, false):
        """
        Implements the C expression:

        condition ? true : false

        Required to correctly interpret plural forms.
        """
        if condition:
            return true
        else:
            return false

    def c2py(plural):
        """Gets a C expression as used in PO files for plural forms and
        returns a Python lambda function that implements an equivalent
        expression.
        """
        # Security check, allow only the "n" identifier
        from cStringIO import StringIO
        import token, tokenize
        tokens = tokenize.generate_tokens(StringIO(plural).readline)
        try:
            danger = [x for x in tokens if x[0] == token.NAME and x[1] != 'n']
        except tokenize.TokenError:
            raise ValueError(
                'plural forms expression error, maybe unbalanced parenthesis')
        else:
            if danger:
                raise ValueError('plural forms expression could be dangerous')

        # Replace some C operators by their Python equivalents
        plural = plural.replace('&&', ' and ')
        plural = plural.replace('||', ' or ')

        expr = re.compile(r'\!([^=])')
        plural = expr.sub(' not \\1', plural)

        # Regular expression and replacement function used to transform
        # "a?b:c" to "test(a,b,c)".
        expr = re.compile(r'(.*?)\?(.*?):(.*)')
        def repl(x):
            return "test(%s, %s, %s)" % (x.group(1), x.group(2),
                                        expr.sub(repl, x.group(3)))

        # Code to transform the plural expression, taking care of parentheses
        stack = ['']
        for c in plural:
            if c == '(':
                stack.append('')
            elif c == ')':
                if len(stack) == 1:
                    # Actually, we never reach this code, because unbalanced
                    # parentheses get caught in the security check at the
                    # beginning.
                    raise ValueError, 'unbalanced parenthesis in plural form'
                s = expr.sub(repl, stack.pop())
                stack[-1] += '(%s)' % s
            else:
                stack[-1] += c
        plural = expr.sub(repl, stack.pop())

        return eval('lambda n: int(%s)' % plural)

if sys.version >= '2.4':
    NullTranslations = gettext.NullTranslations
    GNUTranslations = gettext.GNUTranslations
else:
    import locale
    try:
        getpreferredencoding = locale.getpreferredencoding
    except AttributeError:
        import sys
        if sys.platform in ('win32', 'darwin', 'mac'):
            def getpreferredencoding(do_setlocale=True):
                import _locale
                return _locale._getdefaultlocale()[1]
        elif hasattr(locale, 'CODESET'):
            # Return the charset that the user is likely using, according
            # to the system configuration.
            def getpreferredencoding(do_setlocale=True):
                if do_setlocale:
                    oldloc = locale.setlocale(locale.LC_CTYPE)
                    locale.setlocale(locale.LC_CTYPE, "")
                    result = locale.nl_langinfo(locale.CODESET)
                    locale.setlocale(locale.LC_CTYPE, oldloc)
                    return result
                else:
                    return locale.nl_langinfo(locale.CODESET)
        else:
            # Fall back to parsing environment variables
            def getpreferredencoding(do_setlocale=True):
                return locale.getdefaultlocale()[1]

    class NullTranslations(gettext.NullTranslations):
        _output_charset = None

        if sys.version < '2.3':
            _fallback = None
            def add_fallback(self, fallback):
                if self._fallback:
                    self._fallback.add_fallback(fallback)
                else:
                    self._fallback = fallback

            def gettext(self, message):
                if self._fallback:
                    return self._fallback.gettext(message)
                return message

            def ngettext(self, msgid1, msgid2, n):
                if self._fallback:
                    return self._fallback.ngettext(msgid1, msgid2, n)
                if n == 1:
                    return msgid1
                else:
                    return msgid2

            def ugettext(self, message):
                if self._fallback:
                    return self._fallback.ugettext(message)
                return unicode(message)

            def ungettext(self, msgid1, msgid2, n):
                if self._fallback:
                    return self._fallback.ungettext(msgid1, msgid2, n)
                if n == 1:
                    return unicode(msgid1)
                else:
                    return unicode(msgid2)

        def lgettext(self, message):
            if self._fallback:
                return self._fallback.lgettext(message)
            return message

        def lngettext(self, msgid1, msgid2, n):
            if self._fallback:
                return self._fallback.lngettext(msgid1, msgid2, n)
            if n == 1:
                return msgid1
            else:
                return msgid2

        def output_charset(self):
            return self._output_charset

        def set_output_charset(self, charset):
            self._output_charset = charset

    class GNUTranslations(gettext.GNUTranslations, NullTranslations):
        _output_charset = None

        if sys.version < '2.3':
            def _parse(self, fp):
                gettext.GNUTranslations._parse(self, fp)
                # Get the plural selector function
                if 'plural-forms' in self._info:
                    v = self._info['plural-forms'].split(';')
                    plural = v[1].split('plural=')[1]
                    self.plural = c2py(plural)
                else:
                    # germanic plural by default
                    self.plural = lambda n: int(n != 1)
                # Unconditionally convert both msgids and msgstrs to
                # Unicode using the character encoding specified in the
                # charset parameter of the Content-Type header.
                messages = self._catalog.iteritems()
                self._catalog = catalog = {}
                for msg, tmsg in messages:
                    if '\x00' in msg:
                        # Plural forms
                        msgid1, msgid2 = msg.split('\x00')
                        tmsg = tmsg.split('\x00')
                        if self._charset:
                            msgid1 = unicode(msgid1, self._charset)
                            tmsg = [unicode(x, self._charset) for x in tmsg]
                        for i in range(len(tmsg)):
                            catalog[(msgid1, i)] = tmsg[i]
                    else:
                        if self._charset:
                            msg = unicode(msg, self._charset)
                            tmsg = unicode(tmsg, self._charset)
                        catalog[msg] = tmsg
                return

        def gettext(self, message):
            missing = object()
            tmsg = self._catalog.get(message, missing)
            if tmsg is missing:
                if self._fallback:
                    return self._fallback.gettext(message)
                return message
            # Encode the Unicode tmsg back to an 8-bit string, if possible
            if self._output_charset:
                return tmsg.encode(self._output_charset)
            elif self._charset:
                return tmsg.encode(self._charset)
            return tmsg

        def lgettext(self, message):
            missing = object()
            tmsg = self._catalog.get(message, missing)
            if tmsg is missing:
                if self._fallback:
                    return self._fallback.lgettext(message)
                return message
            if self._output_charset:
                return tmsg.encode(self._output_charset)
            return tmsg.encode(locale.getpreferredencoding())

        def ngettext(self, msgid1, msgid2, n):
            try:
                tmsg = self._catalog[(msgid1, self.plural(n))]
                if self._output_charset:
                    return tmsg.encode(self._output_charset)
                elif self._charset:
                    return tmsg.encode(self._charset)
                return tmsg
            except KeyError:
                if self._fallback:
                    return self._fallback.ngettext(msgid1, msgid2, n)
                if n == 1:
                    return msgid1
                else:
                    return msgid2

        def lngettext(self, msgid1, msgid2, n):
            try:
                tmsg = self._catalog[(msgid1, self.plural(n))]
                if self._output_charset:
                    return tmsg.encode(self._output_charset)
                return tmsg.encode(locale.getpreferredencoding())
            except KeyError:
                if self._fallback:
                    return self._fallback.lngettext(msgid1, msgid2, n)
                if n == 1:
                    return msgid1
                else:
                    return msgid2

        def ugettext(self, message):
            missing = object()
            tmsg = self._catalog.get(message, missing)
            if tmsg is missing:
                if self._fallback:
                    return self._fallback.ugettext(message)
                return unicode(message)
            return tmsg

        def ungettext(self, msgid1, msgid2, n):
            try:
                tmsg = self._catalog[(msgid1, self.plural(n))]
            except KeyError:
                if self._fallback:
                    return self._fallback.ungettext(msgid1, msgid2, n)
                if n == 1:
                    tmsg = unicode(msgid1)
                else:
                    tmsg = unicode(msgid2)
            return tmsg

# Locate a .mo file using the gettext strategy
def FindCatalogs(domain, localedir=None, languages=None):
    # Get some reasonable defaults for arguments that were not supplied
    if localedir is None:
        localedir = gettext._default_localedir
    if languages is None:
        languages = []
        for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            val = os.environ.get(envar)
            if val:
                languages = val.split(':')
                break
        if 'C' not in languages:
            languages.append('C')
    # now normalize and expand the languages
    nelangs = []
    for lang in languages:
        for nelang in gettext._expand_lang(lang):
            if nelang not in nelangs:
                nelangs.append(nelang)
    # select a language
    result = []
    for lang in nelangs:
        if lang == 'C':
            break
        mofile = os.path.join(localedir, lang, 'LC_MESSAGES', '%s.mo' % domain)
        result.append(mofile)
    return result

def GetTranslation(domain, localedir=None, languages=None, class_=None,
                   fallback=False, codeset=None, bundle=None):
    if class_ is None:
        class_ = GNUTranslations
    result = None
    for mofile in FindCatalogs(domain, localedir, languages):
        try:
            if bundle:
                resource = ImportUtil.OsPathToResource(mofile)
                stream = ImportUtil.GetResourceStream(bundle, resource)
            else:
                stream = open(mofile, 'rb')
        except IOError:
            continue
        t = class_(stream)
        if codeset:
            t.set_output_charset(codeset)
        if result is None:
            result = t
        else:
            result.add_fallback(t)
    if result is None:
        if fallback:
            return NullTranslations()
        from errno import ENOENT
        raise IOError(ENOENT, 'No translation file found for domain', domain)
    return result
