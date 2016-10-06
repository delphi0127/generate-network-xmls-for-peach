import sys
from Ft.Lib.Random import FtRandom, FtSystemRandom, Random, GetRandomBytes

# seed, then results, in order, of: random(), getrandbits(16),
# getrandbytes(3), getrandbytes(3) after jumpahead(1000000)
WH_TEST_DATA = (303, 0.72868220290585795, 39534L, '\x9a\x82\x8e', "\xd7`'")
MT_TEST_DATA = (303, 0.031657474042347089, 63491L, '\xbd\x17\x90', 'O\xf7\xee')


def test_ftrandom_instance(tester, seeded_generator, obj_to_read, expected):
    r1 = obj_to_read.random()
    r2 = obj_to_read.getrandbits(16)
    r3 = obj_to_read.getrandbytes(3)
    seeded_generator.jumpahead(1000000)
    r4 = obj_to_read.getrandbytes(3)
    tester.compare(expected, (r1, r2, r3, r4))
    return

def test_ftrandom_operation(tester, generator, obj_to_read):
    generator.seed()
    generator.seed(1000)
    generator.seed(tester)
    n = generator.random()
    tester.compare(float, type(n))
    n = generator.getrandbits(128)
    tester.compare(long, type(n))
    state = generator.getstate()
    bytes = obj_to_read.getrandbytes(5000)
    tester.compare(5000, len(bytes))
    generator.setstate(state)
    new_bytes = obj_to_read.getrandbytes(5000)
    tester.compare(bytes, new_bytes)
    return

def Test(tester):
    tester.startGroup('FtRandom')

    tester.startTest('Operation')
    g = FtRandom()
    test_ftrandom_operation(tester, g, g)
    tester.testDone()

    if sys.version < '2.3':
        expected = WH_TEST_DATA
    else:
        expected = MT_TEST_DATA
    seed = expected[0]
    tester.startTest('Sequence with seed: %d' % seed)
    for i in range(2):
        g = FtRandom(seed)
        test_ftrandom_instance(tester, g, g, expected[1:])
    for i in range(2):
        g.seed(seed)
        test_ftrandom_instance(tester, g, g, expected[1:])
    tester.testDone()
    tester.groupDone()

    tester.startGroup('FtRandom fallback instance in FtSystemRandom')
    tester.startTest('Sequence with seed: %d' % seed)
    for i in range(2):
        g = FtSystemRandom(seed)
        test_ftrandom_instance(tester, g, g._fallback_prng, expected[1:])
    for i in range(2):
        g.seed(seed)
        test_ftrandom_instance(tester, g, g._fallback_prng, expected[1:])
    tester.testDone()
    tester.groupDone()

    tester.startGroup('FtSystemRandom')
    tester.startTest('Operation')
    g = FtSystemRandom()
    test_ftrandom_operation(tester, g, g._fallback_prng)
    tester.testDone()
    tester.groupDone()

    tester.startGroup('Random()')
    tester.startTest('Operation')
    n = Random()
    tester.compare(float, type(n))
    tester.testDone()
    tester.groupDone()

    tester.startGroup('GetRandomBytes()')
    tester.startTest('Operation')
    bytes = GetRandomBytes(5000)
    tester.compare(5000, len(bytes))
    tester.testDone()
    tester.groupDone()
    return
