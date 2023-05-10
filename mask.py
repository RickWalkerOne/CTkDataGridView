from typing import Callable, Optional, Any, List
from re import compile


class Mask:
    def __init__(self,
                 format_type: str,
                 mask: Optional[str] = None,
                 monetary: Optional[bool] = False,
                 decimal_places: Optional[int] = 2,
                 decimal_separator: Optional[str] = '.',
                 thousand_places: Optional[int] = 3,
                 thousand_separator: Optional[str] = ',',
                 symbol: Optional[str] = '',
                 format_negative: Optional[str] = '-%(symbol)s%(amount)s',
                 format_positive: Optional[str] = '%(symbol)s%(amount)s',
                 placeholder: Optional[str] = '_'):
        self._basestring = type(u'')
        self._type = format_type
        if str(self._type).lower() == 'fixed':
            assert self._type is not None, 'the fixed mask, is not present'
        self._mask = mask
        self._monetary = monetary
        self._dec_places = decimal_places
        self._dec_sep = decimal_separator
        self._tho_places = thousand_places
        self._tho_sep = thousand_separator
        self._symbol = symbol
        self._fmt_neg = format_negative
        self._fmt_pos = format_positive
        self._placeholder = placeholder
        self._callbacks = []
        self._buffer = []

        self._defs = {
            '9': '[0-9]',
            'a': '[a-zA-Z]',
            'x': '[a-zA-z0-9]'
        }
        self._tests = []
        self._partialPosition = None
        self._firstNonMaskPosition = None
        self._len = len(self._mask)
        self._start()

    def _start(self):
        self._tests = []
        self._partialPosition = None
        self._firstNonMaskPosition = None
        self._len = len(self._mask)
        for i, c in enumerate(self._mask.lower()):
            if c == '?':
                self._len -= 1
                self._partialPosition = i
            atom = self._defs.get(c, None)
            self._tests.append(compile('(%s)' % atom) if atom else atom)
            if not atom and self._firstNonMaskPosition is None:
                self._firstNonMaskPosition = len(self._tests) - 1

    def cget(self, key):
        if key == 'format_type':
            return self._type
        if key == 'decimal_places':
            return self._dec_places
        if key == 'decimal_separator':
            return self._dec_sep
        if key == 'thousand_places':
            return self._tho_places
        if key == 'thousand_separator':
            return self._tho_sep
        if key == 'format_negative':
            return self._fmt_neg
        if key == 'format_positive':
            return self._fmt_pos
        return getattr(self, '_' + key)

    def configure(self,
                  format_type: Optional[str] = None,
                  mask: Optional[str] = None,
                  monetary: Optional[bool] = None,
                  decimal_places: Optional[int] = None,
                  decimal_separator: Optional[str] = None,
                  thousand_places: Optional[int] = None,
                  thousand_separator: Optional[str] = None,
                  symbol: Optional[str] = None,
                  format_negative: Optional[str] = None,
                  format_positive: Optional[str] = None,
                  placeholder: Optional[str] = None):
        changed = []
        if format_type is not None:
            self._type = format_type
            changed.append('format_type')
        if mask is not None:
            self._mask = mask
            changed.append('mask')
        if monetary is not None:
            self._monetary = monetary
            changed.append('monetary')
        if decimal_places is not None:
            self._dec_places = decimal_places
            changed.append('decimal_places')
        if decimal_separator is not None:
            self._dec_sep = decimal_separator
            changed.append('decimal_separator')
        if thousand_places is not None:
            self._tho_places = thousand_places
            changed.append('thousand_places')
        if thousand_separator is not None:
            self._tho_sep = thousand_separator
            changed.append('thousand_separator')
        if symbol is not None:
            self._symbol = symbol
            changed.append('symbol')
        if format_negative is not None:
            self._fmt_neg = format_negative
            changed.append('format_negative')
        if format_positive is not None:
            self._fmt_pos = format_positive
            changed.append('format_positive')
        if placeholder is not None:
            self._placeholder = placeholder
            changed.append('placeholder')
        if len(changed) > 0:
            self._start()
        for func in self._callbacks:
            func(changed)

    def trace(self, func: Callable[[List[str]], Any], add: Optional[bool] = False):
        if add:
            self._callbacks.append(func)
        else:
            self._callbacks = [func]

    def clean_numeric(self, string):
        if not isinstance(string, self._basestring):
            string = str(string)
        string = string.replace(self._symbol + ' ', '') \
            .replace(self._tho_sep, '') \
            .replace(self._dec_sep, '.')
        if '.' not in string:
            string = list(string)
            string.insert(-2, '.')
            string = ''.join(string)
        return string.partition('.')

    def fmt_numeric(self, amount):
        temp = '00' if '.' not in str(amount) \
            else str(amount).split('.')[1]
        __l = []
        amount = amount.split('.')[0]
        try:
            minus = float(''.join(self.clean_numeric(amount))) < 0
        except ValueError:
            minus = 0
        if len(amount) > self._tho_places:
            __nn = amount[-self._tho_places:]
            __l.append(__nn)
            amount = amount[:len(amount) - self._tho_places]
            while len(amount) > self._tho_places:
                nn = amount[len(amount) - self._tho_places:]
                __l.insert(0, nn)
                amount = amount[0:len(amount) - self._tho_places]

        if len(''.join(self.clean_numeric(amount))) > 0:
            __l.insert(0, amount)
        amount = self._tho_sep.join(__l) + self._dec_sep + temp
        if minus:
            amount = self._fmt_neg % {
                'symbol': self._symbol,
                'amount': amount
            }
        else:
            amount = self._fmt_pos % {
                'symbol': (self._symbol + ' ') if self._symbol else '',
                'amount': amount
            }
        return amount

    def seeknext(self, pos):
        if 0 <= pos + 1 < self._len:
            if self._tests[pos + 1]:
                return pos + 1
            return self.seeknext(pos + 1)
        return pos

    def seekprev(self, pos):
        if 0 <= pos - 1 < self._len:
            if self._tests[pos - 1]:
                return pos - 1
            return self.seekprev(pos - 1)
        return pos

    def shiftl(self, begin):
        if begin < 0:
            return
        for i in range(self._len):
            j = self.seeknext(begin)
            if self._tests[i]:
                if j < self._len and self._tests[i].match(self._buffer[i]):
                    self._buffer[i] = self._buffer[j]
                    self._buffer[j] = self._placeholder
                else:
                    break

    def shiftr(self, pos, c):
        if pos in range(self._len):
            j = self.seeknext(pos)
            t = self._buffer[pos]
            if not t == c and j < self._len and t == self._placeholder:
                self._buffer[pos] = c

    def write(self) -> str:
        return ''.join(
            filter(
                lambda x: x is not None,
                map(
                    lambda c, self=self:
                    (self._placeholder
                     if self._defs.get(c, None)
                     else c)
                    if c != '?' else None, self._mask)
            )
        )

    def clear(self, value) -> str:
        return ''.join(
            filter(
                lambda x: x is not None,
                map(
                    lambda c, self=self, _value=value:
                    (value[self._mask.index(c)]
                     if self._defs.get(c, None)
                     else None)
                    if c != '?' else None, self._mask)
            )
        )

    def __len__(self) -> int:
        return self._len
