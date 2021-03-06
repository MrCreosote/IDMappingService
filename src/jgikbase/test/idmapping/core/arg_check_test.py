from jgikbase.idmapping.core.arg_check import not_none, check_string, no_Nones_in_iterable
from jgikbase.test.idmapping.test_utils import assert_exception_correct
from pytest import raises
from jgikbase.idmapping.core import arg_check
from jgikbase.idmapping.core.errors import MissingParameterError, IllegalParameterError


def test_not_none_pass():
    not_none(4, 'integer')
    not_none(0, 'integer')
    not_none('four', 'text')
    not_none(True, 'bool')
    not_none(False, 'bool')
    not_none('', 'str')


def test_not_none_fail():
    with raises(Exception) as got:
        not_none(None, 'my name')
    assert_exception_correct(got.value, TypeError('my name cannot be None'))


def test_check_string_pass():
    check_string('mystring', 'myname')
    check_string('foo', 'bar', max_len=3)
    check_string('foo', 'bar', legal_characters='fo')
    check_string('foo', 'bar', 'fo', 3)


def test_check_string_fail():
    fail_check_string(None, 'foo', None, None, MissingParameterError('foo'))
    fail_check_string('   \t   \n   ', 'foo', None, None,
                      MissingParameterError('foo'))
    fail_check_string('bar', 'foo', None, 2,
                      IllegalParameterError('foo bar exceeds maximum length of 2'))
    fail_check_string('b_ar&_1', 'foo', 'a-z_', None,
                      IllegalParameterError('Illegal character in foo b_ar&_1: &'))

    # this is reaching into the implementation which is very naughty but I don't see a good way
    # to check the cache is actually working otherwise
    assert arg_check._REGEX_CACHE['a-z_'].pattern == '[^a-z_]'

    # test with cache
    fail_check_string('b_ar&_1', 'foo', 'a-z_', None,
                      IllegalParameterError('Illegal character in foo b_ar&_1: &'))


def fail_check_string(string, name, illegal_characters, max_len, expected):
    with raises(Exception) as got:
        check_string(string, name, illegal_characters, max_len)
    assert_exception_correct(got.value, expected)


def test_no_Nones_in_iterable_pass():
    no_Nones_in_iterable([], 'foo')
    no_Nones_in_iterable(set(), 'foo')
    no_Nones_in_iterable(['a', 'b', 'c'], 'foo')
    no_Nones_in_iterable({'a', 'b', 'c'}, 'foo')


def test_no_Nones_in_iterable_fail():
    fail_no_Nones_in_iterable(None, 'my name', TypeError('my name cannot be None'))
    fail_no_Nones_in_iterable(['a', None, 'c'], 'thingy', TypeError('None item in thingy'))
    fail_no_Nones_in_iterable({'a', 'c', None}, 'thingy2', TypeError('None item in thingy2'))


def fail_no_Nones_in_iterable(iterable, name, expected):
    with raises(Exception) as got:
        no_Nones_in_iterable(iterable, name)
    assert_exception_correct(got.value, expected)
