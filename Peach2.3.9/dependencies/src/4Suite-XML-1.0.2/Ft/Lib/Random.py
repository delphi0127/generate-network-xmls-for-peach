########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/Random.py,v 1.8 2006/01/13 06:12:55 mbrown Exp $
"""
Thread-safe random number generation

Random number generation capabilities, speed, and thread safety in
stdlib vary from version to version of Python. In addition, attempts to
use an OS-specific random number source can result in unexpected
exceptions being raised. Also, a bug in Python 2.3.0 can lead to a
reduction in entropy, and a bug in Python 2.4.0 and 2.4.1 can result
in exceptions related to open filehandles on some multithreaded Posix
platforms.

This module works around as many of these issues as it can by defining
random number generator classes that can be used safely by multiple
threads, using the best random number sources available. They support
all versions of Python from 2.1 up, and fall back on more reliable
generators when exception conditions occur. In addition, convenience
functions equivalent to random.random() and os.urandom() are exposed.

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__all__ = ['urandom', 'FtRandom', 'FtSystemRandom', 'DEFAULT_RNG',
           'Random', 'GetRandomBytes']

import random, threading, os, sys
from sys import version_info

py230 = version_info[0:3] == (2, 3, 0)
py23up = version_info[0:2] > (2, 2)
py24up = version_info[0:2] > (2, 3)
py242up = version_info[0:3] > (2, 4, 1)
posix = os.name == 'posix'
win32 = sys.platform == 'win32'

_lock = threading.Lock()

#=============================================================================
# Thread-safe implementation of os.urandom()
# (still raises NotImplementedError when no OS-specific random number source)
#
if win32 and py24up:
    urandom = os.urandom
elif posix:
    if py242up:
        urandom = os.urandom
    else:
        # Python 2.4.2's os.urandom()
        def urandom(n):
            """urandom(n) -> str

            Return a string of n random bytes suitable for cryptographic use.

            """
            try:
                _urandomfd = os.open("/dev/urandom", os.O_RDONLY)
            except:
                raise NotImplementedError("/dev/urandom (or equivalent) not found")
            bytes = ""
            while len(bytes) < n:
                bytes += os.read(_urandomfd, n - len(bytes))
            os.close(_urandomfd)
            return bytes
        if hasattr(random, '_urandom'):
            random._urandom = urandom
else:
    def urandom(n):
        """urandom(n) -> str

        Return a string of n random bytes suitable for cryptographic use.

        """
        raise NotImplementedError("There is no OS-specific random number source.")

#=============================================================================
# FtRandom: a non-crypto-safe PRNG (Mersenne Twister or Wichmann-Hill, made
# thread-safe). By default, seeded from an OS-specific random number source,
# if available.
#
if posix and not py24up:
    # posix py2.3 down: use urandom if possible
    from binascii import hexlify
    def _best_seed(self, a=None):
        """Initialize internal state from hashable object.

        None or no argument seeds from current time or from an operating
        system specific randomness source if available.

        If a is not None or an int or long, hash(a) is used instead.
        """
        if a is None:
            try:
                a = long(hexlify(urandom(16)), 16)
            except NotImplementedError:
                # posix py2.3.0: use system clock, but avoid buggy stdlib
                if py230:
                    import time
                    a = long(time.time() * 256)
        super(FtRandom, self).seed(a)
elif py230:
    # win32 py2.3.0: use system clock, but avoid buggy stdlib
    def _best_seed(self, a=None):
        import time
        a = long(time.time() * 256)
        super(FtRandom, self).seed(a)
else:
    # posix or win32 py2.4 up: urandom if possible, fall back on system clock
    # win32 py2.3 down: system clock only
    _best_seed = random.Random.seed

# random.Random.gauss() is not thread-safe
def _gauss(self, *args, **kwargs):
    """Gaussian distribution.

    mu is the mean, and sigma is the standard deviation.

    Thread-safe.
    """
    _lock.acquire()
    rv = super(self.__class__, self).gauss(*args, **kwargs)
    _lock.release()
    return rv

if py23up:
    # Mersenne Twister, already thread-safe
    _random = random.Random.random
    def _getrandbytes(self, k):
        """getrandbytes(k) -> x.  Returns k random bytes as a str."""
        bytes = ""
        while len(bytes) < k:
            n = super(FtRandom, self).random()
            bytes += chr(int(n * 256))
        return bytes
else:
    # Wichmann-Hill, made thread-safe
    def _random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        _lock.acquire()
        n = super(FtRandom, self).random()
        _lock.release()
        return n
    def _getrandbytes(self, k):
        """getrandbytes(k) -> x.  Returns k random bytes as a str."""
        bytes = ""
        _lock.acquire()
        while len(bytes) < k:
            n = super(FtRandom, self).random()
            bytes += chr(int(n * 256))
        _lock.release()
        return bytes

if py24up:
    _getrandbits = random.Random.getrandbits
else:
    # This is the py2.4 implementation
    from binascii import hexlify
    def _getrandbits(self, k):
        """getrandbits(k) -> x.  Generates a long int with k random bits."""
        if k <= 0:
            raise ValueError('number of bits must be greater than zero')
        if k != int(k):
            raise TypeError('number of bits should be an integer')
        bytes = (k + 7) // 8                    # bits / 8 and rounded up
        x = long(hexlify(self.getrandbytes(bytes)), 16)
        return x >> (bytes * 8 - k)             # trim excess bits

class FtRandom(random.Random, object):
    """
    The best available OS-agnostic PRNG, thread-safe.

    Implements getrandbits() in all versions of Python.
    Also adds getrandbytes(), which returns a str of bytes.
    """
    seed = _best_seed
    gauss = _gauss
    random = _random
    getrandbits = _getrandbits
    getrandbytes = _getrandbytes
    def __init__(self, *args, **kwargs):
        return super(FtRandom, self).__init__(*args, **kwargs)


#=============================================================================
# FtSystemRandom: a PRNG that uses an OS-specific random number source, if
# available, falling back on an instance of FtRandom. It is as crypto-safe as
# the OS-specific random number source, when such a source is available.
# Calls to seed() and jumpahead() only affect the fallback FtRandom instance.
#
if win32 and not py24up:
    # don't bother trying OS-specific sources on win32 before py2.4
    def _random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        return self._fallback_prng.random()
    def _getrandbits(self, k):
        """getrandbits(k) -> x.  Generates a long int with k random bits."""
        return self._fallback_prng.getrandbits(k)
    def _getrandbytes(self, k):
        """getrandbytes(k) -> x.  Returns k random bytes as a str."""
        return self._fallback_prng.getrandbytes(k)
else:
    # Functions that read random numbers from OS-specific sources
    # Use random() and getrandbits() from random.SystemRandom.
    # We've already replaced random._urandom with our urandom, so it's OK.
    try:
        # py2.4 up...
        from random import SystemRandom as _SystemRandom
        _sr_random = _SystemRandom.random.im_func
        _sr_getrandbits = _SystemRandom.getrandbits.im_func
    except ImportError:
        # py2.3 down, posix (since we tested for win32 above)...
        # These are based on the py2.4 implementation.
        from binascii import hexlify
        _BPF = 53        # Number of bits in a float
        _RECIP_BPF = 2**-_BPF
        def _sr_random(self):
            """Get the next random number in the range [0.0, 1.0)."""
            return (long(hexlify(urandom(7)), 16) >> 3) * _RECIP_BPF
        def _sr_getrandbits(self, k):
            """getrandbits(k) -> x.  Generates a long int with k random bits."""
            if k <= 0:
                raise ValueError('number of bits must be greater than zero')
            if k != int(k):
                raise TypeError('number of bits should be an integer')
            bytes = (k + 7) // 8                    # bits / 8 and rounded up
            x = long(hexlify(urandom(bytes)), 16)
            return x >> (bytes * 8 - k)             # trim excess bits

    # Wrapper functions that try OS-specific sources first, then fall back
    def _random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        try:
            return _sr_random(self)
        except NotImplementedError:
            return self._fallback_prng.random()
    def _getrandbits(self, *args, **kwargs):
        """getrandbits(k) -> x.  Generates a long int with k random bits."""
        try:
            return _sr_getrandbits(self, *args, **kwargs)
        except NotImplementedError:
            return self._fallback_prng.getrandbits(*args, **kwargs)
    def _getrandbytes(self, k):
        """getrandbytes(k) -> x.  Returns k random bytes as a str."""
        try:
            return urandom(k)
        except NotImplementedError:
            return self._fallback_prng.getrandbytes(k)

class FtSystemRandom(FtRandom):
    """
    A PRNG that uses an OS-specific random number source, if
    available, falling back on an instance of FtRandom.

    Calls to seed(), jumpahead(), getstate() and setstate() only affect
    the fallback FtRandom instance.

    Implements getrandbits() in all versions of Python.
    Also adds getrandbytes(), which returns a str of bytes.
    """
    random = _random
    getrandbits = _getrandbits
    getrandbytes = _getrandbytes
    def __init__(self, *args, **kwargs):
        self._fallback_prng = FtRandom()
        return super(FtSystemRandom, self).__init__(*args, **kwargs)
    def seed(self, *args, **kwargs):
        """Seed the fallback PRNG (an instance of FtRandom)"""
        return self._fallback_prng.seed(*args, **kwargs)
    def jumpahead(self, *args, **kwargs):
        """Make the fallback PRNG (an instance of FtRandom) jump ahead"""
        return self._fallback_prng.jumpahead(*args, **kwargs)
    def getstate(self):
        """Return internal state; can be passed to setstate() later."""
        return self._fallback_prng.getstate()
    def setstate(self, state):
        """Restore internal state from object returned by getstate()."""
        self._fallback_prng.setstate(state)
        return

#=============================================================================
# convenience functions
#
DEFAULT_RNG = FtSystemRandom()
def Random():
    """Returns a random float, n, where 0 <= n < 1"""
    return DEFAULT_RNG.random()

def GetRandomBytes(numBytes):
    """
    Returns a string of random bytes from the best RNG available.
    Equivalent to os.urandom(), but failsafe.
    """
    return DEFAULT_RNG.getrandbytes(numBytes)

