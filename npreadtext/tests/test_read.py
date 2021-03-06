from os import path
from io import StringIO
import pytest
import numpy as np
from numpy.testing import assert_array_equal, assert_equal
from npreadtext import read


def _get_full_name(basename):
    return path.join(path.dirname(__file__), 'data', basename)


@pytest.mark.parametrize('basename,delim', [('test1.csv', ','),
                                            ('test1.tsv', '\t')])
def test1_read1(basename, delim):
    filename = _get_full_name(basename)
    al = np.loadtxt(filename, delimiter=delim)

    a = read(filename, delimiter=delim)
    assert_array_equal(a, al)

    with open(filename, 'r') as f:
        a = read(f, delimiter=delim)
        assert_array_equal(a, al)


@pytest.mark.parametrize('basename,sci', [('test1e.csv', 'E'),
                                          ('test1d.csv', 'D')])
def test1_read_sci(basename, sci):
    filename = path.join(path.dirname(__file__), 'data', basename)
    filename_e = path.join(path.dirname(__file__), 'data', 'test1e.csv')
    al = np.loadtxt(filename_e, delimiter=',')

    a = read(filename, sci=sci)
    assert_array_equal(a, al)

    with open(filename, 'r') as f:
        a = read(f, sci=sci)
        assert_array_equal(a, al)


@pytest.mark.parametrize('basename,delim', [('test1.csv', ','),
                                            ('test1.tsv', '\t')])
def test1_read_usecols(basename, delim):
    filename = path.join(path.dirname(__file__), 'data', basename)
    al = np.loadtxt(filename, delimiter=delim, usecols=[0, 2])

    a = read(filename, usecols=[0, 2], delimiter=delim)
    assert_array_equal(a, al)

    with open(filename, 'r') as f:
        a = read(f, usecols=[0, 2], delimiter=delim)
        assert_array_equal(a, al)


def test1_read_with_comment():
    filename = _get_full_name('test1_with_comments.csv')
    al = np.loadtxt(filename, delimiter=',')

    a = read(filename, comment='#')
    assert_array_equal(a, al)

    with open(filename, 'r') as f:
        a = read(f, comment='#')
        assert_array_equal(a, al)


@pytest.mark.parametrize('comment', ['..', '//', '@-'])
def test_comment_two_chars(comment):
    content = '# IGNORE\n1.5,2.5# ABC\n3.0,4.0# XXX\n5.5,6.0\n'
    txt = StringIO(content.replace('#', comment))
    a = read(txt, dtype=np.float64, comment=comment)
    assert_equal(a, [[1.5, 2.5], [3.0, 4.0], [5.5, 6.0]])


def test_decimal_is_comma():
    filename = path.join(path.dirname(__file__),
                         'data', 'decimal_is_comma.txt')
    a = read(filename, decimal=',', delimiter=' ')
    expected = np.array([[1.5, 1.75, 2.0],
                         [2.5, 2.75, 3.0],
                         [3.5, 3.75, 4.0],
                         [4.5, 4.75, 5.0]])
    assert_array_equal(a, expected)


def test_quoted_field():
    filename = _get_full_name('quoted_field.csv')
    a = read(filename)
    expected_dtype = np.dtype([('f0', 'S8'), ('f1', np.float64)])
    assert a.dtype == expected_dtype
    expected = np.array([('alpha, x', 2.5),
                         ('beta, x', 4.5),
                         ('gamma, x', 5.0)], dtype=expected_dtype)
    assert_array_equal(a, expected)


@pytest.mark.parametrize('explicit_dtype', [False, True])
@pytest.mark.parametrize('skiprows', [0, 1, 3])
def test_dtype_and_skiprows(explicit_dtype: bool, skiprows: int):
    filename = _get_full_name('mixed_types1.dat')

    expected_dtype = np.dtype([('f0', np.uint16),
                               ('f1', np.float64),
                               ('f2', 'S7'),
                               ('f3', np.int8)])
    expected = np.array([(1000, 2.4, "alpha", -34),
                         (2000, 3.1, "beta", 29),
                         (3500, 9.9, "gamma", 120),
                         (4090, 8.1, "delta", 0),
                         (5001, 4.4, "epsilon", -99),
                         (6543, 7.8, "omega", -1)], dtype=expected_dtype)

    dt = expected_dtype if explicit_dtype else None
    a = read(filename, quote="'", delimiter=';', skiprows=skiprows, dtype=dt)
    assert_array_equal(a, expected[skiprows:])


def test_structured_dtype_1():
    dt = [("a", 'u1', 2), ("b", 'u1', 2)]
    a = read(StringIO("0,1,2,3\n6,7,8,9\n"), dtype=dt)
    expected = np.array([((0, 1), (2, 3)), ((6, 7), (8, 9))],
                        dtype=dt)
    assert_array_equal(a, expected)


def test_structured_dtype_2():
    dt = [("a", 'u1', (2, 2))]
    a = read(StringIO("0 1 2 3"), delimiter=' ', dtype=dt)
    assert_array_equal(a, np.array([(((0, 1), (2, 3)),)], dtype=dt))


@pytest.mark.parametrize('param', ['skiprows', 'max_rows'])
@pytest.mark.parametrize('badval, exc', [(-3, ValueError), (1.0, TypeError)])
def test_bad_nonneg_int(param, badval, exc):
    with pytest.raises(exc):
        read('foo.bar', **{param: badval})


@pytest.mark.parametrize('fn,shape', [('onerow.txt', (1, 5)),
                                      ('onecol.txt', (5, 1))])
def test_ndmin_single_row_or_col(fn, shape):
    filename = _get_full_name(fn)
    data = [1, 2, 3, 4, 5]
    arr2d = np.array(data).reshape(shape)

    a = read(filename, delimiter=' ')
    assert_array_equal(a, arr2d)

    a = read(filename, delimiter=' ', ndmin=0)
    assert_array_equal(a, data)

    a = read(filename, delimiter=' ', ndmin=1)
    assert_array_equal(a, data)

    a = read(filename, delimiter=' ', ndmin=2)
    assert_array_equal(a, arr2d)


@pytest.mark.parametrize('badval', [-1, 3, "plate of shrimp"])
def test_bad_ndmin(badval):
    with pytest.raises(ValueError):
        read('foo.bar', ndmin=badval)


def test_unpack_structured():
    filename = _get_full_name('mixed_types1.dat')
    expected_dtype = np.dtype([('f0', np.uint16),
                               ('f1', np.float64),
                               ('f2', 'S7'),
                               ('f3', np.int8)])
    expected = np.array([(1000, 2.4, "alpha", -34),
                         (2000, 3.1, "beta", 29),
                         (3500, 9.9, "gamma", 120),
                         (4090, 8.1, "delta", 0),
                         (5001, 4.4, "epsilon", -99),
                         (6543, 7.8, "omega", -1)], dtype=expected_dtype)
    a, b, c, d = read(filename, delimiter=';', quote="'", unpack=True)
    assert_array_equal(a, expected['f0'])
    assert_array_equal(b, expected['f1'])
    assert_array_equal(c, expected['f2'])
    assert_array_equal(d, expected['f3'])


def test_unpack_array():
    filename = _get_full_name('test1.csv')
    a, b, c = read(filename, delimiter=',', unpack=True)
    assert_array_equal(a, np.array([1.0, 4.0, 7.0, 0.0]))
    assert_array_equal(b, np.array([2.0, 5.0, 8.0, 1.0]))
    assert_array_equal(c, np.array([3.0, 6.0, 9.0, 2.0]))


def test_blank_lines():
    txt = StringIO('1 2 30\n\n4 5 60\n     \n7 8 90')
    a = read(txt, delimiter=' ')
    assert_equal(a.dtype, np.uint8)
    assert_equal(a, np.array([[1, 2, 30], [4, 5, 60], [7, 8, 90]],
                             dtype=np.uint8))


def test_max_rows():
    txt = StringIO('1.5,2.5\n3.0,4.0\n5.5,6.0')
    a = read(txt, dtype=np.float64, max_rows=2)
    assert_equal(a.dtype, np.float64)
    assert_equal(a, np.array([[1.5, 2.5], [3.0, 4.0]]))


@pytest.mark.parametrize('dtype', [np.dtype('f8'), np.dtype('i2')])
def test_bad_values(dtype):
    txt = StringIO('1.5,2.5\n3.0,XXX\n5.5,6.0')
    with pytest.raises(RuntimeError, match=f'bad {dtype.name} value'):
        read(txt, dtype=dtype)


def test_converters():
    txt = StringIO('1.5,2.5\n3.0,XXX\n5.5,6.0')
    conv = {-1: lambda s: np.nan if s == 'XXX' else float(s)}
    a = read(txt, dtype=np.float64, converters=conv)
    assert_equal(a, [[1.5, 2.5], [3.0, np.nan], [5.5, 6.0]])


def test_converters_and_usecols():
    txt = StringIO('1.5,2.5,3.5\n3.0,4.0,XXX\n5.5,6.0,7.5\n')
    conv = {-1: lambda s: np.nan if s == 'XXX' else float(s)}
    a = read(txt, dtype=np.float64, converters=conv, usecols=[0, 2])
    assert_equal(a, [[1.5, 3.5], [3.0, np.nan], [5.5, 7.5]])


def test_unicode_with_converter():
    txt = StringIO('cat,dog\nαβγ,δεζ\nabc,def\n')
    conv = {0: lambda s: s.upper()}
    a = read(txt, dtype=np.dtype('U12'), converters=conv)
    assert_equal(a, [['CAT', 'dog'], ['ΑΒΓ', 'δεζ'], ['ABC', 'def']])


def test_converter_with_structured_dtype():
    txt = StringIO('1.5,2.5,Abc\n3.0,4.0,dEf\n5.5,6.0,ghI\n')
    dt = np.dtype([('m', np.int32), ('r', np.float32), ('code', 'U8')])
    conv = {0: lambda s: int(10*float(s)), -1: lambda s: s.upper()}
    a = read(txt, dtype=dt, converters=conv)
    expected = np.array([(15, 2.5, 'ABC'), (30, 4.0, 'DEF'), (55, 6.0, 'GHI')],
                        dtype=dt)
    assert_equal(a, expected)


@pytest.mark.parametrize('dtype, actual_dtype', [('S', np.dtype('S5')),
                                                 ('U', np.dtype('U5'))])
def test_string_no_length_given(dtype, actual_dtype):
    # The given dtype is just 'S' or 'U', with no length.  In these
    # cases, the length of the resulting dtype is determined by the
    # longest string found in the file.
    txt = StringIO('AAA,5-1\nBBBBB,0-3\nC,4-9\n')
    a = read(txt, dtype=dtype)
    expected = np.array([['AAA', '5-1'], ['BBBBB', '0-3'], ['C', '4-9']],
                        dtype=actual_dtype)
    assert_equal(a.dtype, expected.dtype)
    assert_equal(a, expected)


def test_float_conversion():
    # Some tests that the conversion to float64 works as accurately
    # as the Python built-in `float` function.  In a naive version of
    # the float parser, these strings resulted in values that were off
    # by a ULP or two.
    strings = ['0.9999999999999999',
               '9876543210.123456',
               '5.43215432154321e+300',
               '0.901',
               '0.333']
    txt = StringIO('\n'.join(strings))
    a = read(txt)
    expected = np.array([float(s) for s in strings]).reshape((len(strings), 1))
    assert_equal(a, expected)


@pytest.mark.parametrize('dt', [np.int8, np.int16, np.int32, np.int64,
                                np.uint8, np.uint16, np.uint32, np.uint64])
def test_cast_float_to_int(dt):
    # Currently the parser_config flag 'allow_float_for_int' is hardcoded
    # to be true.  This means that if the parsing of an integer value
    # fails, the code will attempt to parse it as a float, and then
    # cast the float value to an integer.  This flag is only used when
    # an explicit dtype is given.
    txt = StringIO('1.0,2.1,3.7\n4,5,6')
    a = read(txt, dtype=dt)
    expected = np.array([[1, 2, 3], [4, 5, 6]], dtype=dt)
    assert_equal(a, expected)


@pytest.mark.parametrize('dt', [np.complex64, np.complex128])
@pytest.mark.parametrize('imaginary_unit', ['i', 'j'])
@pytest.mark.parametrize('with_parens', [False, True])
def test_complex(dt, imaginary_unit, with_parens):
    s = '(1.0-2.5j),3.75,(7+-5.0j)\n(4),(-19e2j),(0)'.replace('j',
                                                              imaginary_unit)
    if not with_parens:
        s = s.replace('(', '').replace(')', '')
    a = read(StringIO(s), dtype=dt, imaginary_unit=imaginary_unit)
    expected = np.array([[1.0-2.5j, 3.75, 7-5j], [4.0, -1900j, 0]], dtype=dt)
    assert_equal(a, expected)


def test_complex_analyze():
    s = '3,2.0,199\n4,1.0+2.0j,225\n2,9.5-3.0j,432'
    a = read(StringIO(s))
    dt = np.dtype([('f0', np.uint8), ('f1', np.complex128), ('f2', np.uint16)])
    assert a.dtype == dt
    assert_equal(a['f0'], [3, 4, 2])
    assert_equal(a['f1'], [2.0, 1+2j, 9.5-3j])
    assert_equal(a['f2'], [199, 225, 432])


def test_read_from_generator_1():

    def gen():
        for i in range(4):
            yield f'{i},{2*i},{i**2}'

    data = read(gen(), dtype=int)
    assert_equal(data, [[0, 0, 0], [1, 2, 1], [2, 4, 4], [3, 6, 9]])


def test_read_from_generator_2():

    def gen():
        for i in range(3):
            yield f'{i} {i/4}'

    data = read(gen(), dtype='i,d', delimiter=' ')
    expected = np.array([(0, 0.0), (1, 0.25), (2, 0.5)], dtype='i,d')
    assert_equal(data, expected)
