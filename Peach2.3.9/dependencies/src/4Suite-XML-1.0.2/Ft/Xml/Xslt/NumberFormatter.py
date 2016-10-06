import re
from Ft.Xml.Xslt import XsltException, Error

# Pattern for format tokens (see spec 7.7.1)
_token_re = re.compile('(\W*)(\w+)(\W*)', re.UNICODE)

class Formatter:

    def __init__(self, format):
        self._format = format
        groups = _token_re.findall(format)
        if not groups:
            raise XsltException(Error.ILLEGAL_NUMBER_FORMAT_VALUE,
                                self._format)

        self.prefix = groups[0][0]
        self.suffix = groups[-1][2]
        
        toks = self.tokens = []
        seps = self.separators = []
        for group in groups[:-1]:
            toks.append(group[1])
            seps.append(group[2])
        toks.append(groups[-1][1])
        if not seps:
            seps.append('.')
        return

    def format(self, numbers, groupSize, groupSeparator):
        raise NotImplementedError
    

class DefaultFormatter(Formatter):

    def format(self, numbers, groupSize, groupSeparator):
        result = []
        zipped = map(None, numbers, self.tokens, self.separators)
        last_separator = self.prefix
        for number, token, separator in zipped[:len(numbers)]:
            if number < 0: number = 0
            result.append(last_separator)
            token = token or self.tokens[-1]
            last_separator = separator or self.separators[-1]
            if token[-1] == '1':
                result.append(self._numeric(number, len(token), groupSize,
                                            groupSeparator))
            elif re.match('[A-HJ-Za-hj-z]$', token):
                result.append(self._alpha(number, token[0]))
            elif token in ('I', 'i'):
                result.append(self._roman(number, token.islower()))
            else:
                raise XsltException(Error.ILLEGAL_NUMBER_FORMAT_VALUE,
                                    self._format)

        result.append(self.suffix)
        return u''.join(result)

    def _numeric(self, number, digits, groupSize, groupSeparator):
        numeric = '%0*d' % (digits, number)
        if not groupSize: return numeric

        result = []
        start_seg = 0
        end_seg = len(numeric) % groupSize
        while end_seg <= len(numeric):
            if end_seg:
                result.append(numeric[start_seg:end_seg])
            start_seg = end_seg
            end_seg += size
        return groupSeparator.join(result)

    def _alpha(self, number, baseLetter):
        base = ord(baseLetter)
        result = []
        while number:
            number, remainder = divmod(number - 1, 26)
            result.insert(0, chr(base + remainder))
        return ''.join(result)
    
    _roman_1000 = ('', 'M', 'MM', 'MMM', 'MMMM')
    _roman_100 = ('', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM')
    _roman_10 = ('', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC')
    _roman_1 = ('', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX')

    def _roman(self, number, lowercase):
        if number >= 5000:
            raise ValueError('unable to convert %d to roman numerals' % number)

        roman = self._roman_1000[number / 1000] + \
                self._roman_100[(number / 100) % 10] + \
                self._roman_10[(number / 10) % 10] + \
                self._roman_1[number % 10]

        if lowercase:
            return roman.lower()
        return roman
