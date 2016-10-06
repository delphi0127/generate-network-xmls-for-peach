from cDeepCopy import deepcopy

def _test():
    l = [None, 1, 2L, 3.14, 'xyzzy', (1, 2L), [3.14, 'abc'],
         {'abc': 'ABC'}, (), [], {}]
    l1 = deepcopy(l)
    print l1==l
    class C:
        def __init__(self, arg=None):
            self.a = 1
            self.arg = arg
            if __name__ == '__main__':
                import sys
                file = sys.argv[0]
            else:
                file = __file__
            self.fp = open(file)
            self.fp.close()
        def __getstate__(self):
            return {'a': self.a, 'arg': self.arg}
        def __setstate__(self, state):
            for key, value in state.iteritems():
                setattr(self, key, value)
        def __deepcopy__(self, memo=None):
            new = self.__class__(deepcopy(self.arg, memo))
            new.a = self.a
            return new
    c = C('argument sketch')
    l.append(c)
    l2 = deepcopy(l)
    print l == l2
    print l
    print l2
    l.append({l[1]: l, 'xyz': l[2]})
    l3 = deepcopy(l)
    import repr
    print map(repr.repr, l)
    print map(repr.repr, l1)
    print map(repr.repr, l2)
    print map(repr.repr, l3)

if __name__ == '__main__':
    _test()
