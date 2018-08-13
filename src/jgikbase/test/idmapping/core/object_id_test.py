from jgikbase.idmapping.core.object_id import NamespaceID, Namespace, ObjectID,\
    NamespaceUserAttributes
from pytest import raises
from jgikbase.test.idmapping.test_utils import assert_exception_correct
from jgikbase.idmapping.core.errors import MissingParameterError, IllegalParameterError
from jgikbase.idmapping.core.user import AuthsourceID, User, Username


def test_namespace_id_init_pass():
    ns = NamespaceID('abcdefghijklmnopqrstuvwxyz0123456789_')
    assert ns.id == 'abcdefghijklmnopqrstuvwxyz0123456789_'

    ns = NamespaceID('abcdefghijklmnopqrstuvwxyz0123456789_'.upper())
    assert ns.id == 'abcdefghijklmnopqrstuvwxyz0123456789_'.upper()

    ns = NamespaceID('a' * 256)
    assert ns.id == 'a' * 256


def test_namespace_id_init_fail():
    fail_namespace_id_init(None, MissingParameterError('namespace id'))
    fail_namespace_id_init('   \t    \n   ',
                           MissingParameterError('namespace id'))
    fail_namespace_id_init('a' * 257, IllegalParameterError(
        'namespace id ' + ('a' * 257) + ' exceeds maximum length of 256'))
    fail_namespace_id_init('fooo1b&_*',
                           IllegalParameterError('Illegal character in namespace id fooo1b&_*: &'))


def fail_namespace_id_init(id_: str, expected: Exception):
    with raises(Exception) as got:
        NamespaceID(id_)
    assert_exception_correct(got.value, expected)


def test_namespace_id_equals():
    assert NamespaceID('foo') == NamespaceID('foo')
    assert NamespaceID('foo') != NamespaceID('bar')
    assert NamespaceID('foo') != 'foo'


def test_namespace_id_hash():
    # string hashes will change from instance to instance of the python interpreter, and therefore
    # tests can't be written that directly test the hash value. See
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    assert hash(NamespaceID('foo')) == hash(NamespaceID('foo'))
    assert hash(NamespaceID('bar')) == hash(NamespaceID('bar'))
    assert hash(NamespaceID('foo')) != hash(NamespaceID('bar'))


def test_namespace_id_slots():
    assert NamespaceID('foo').__slots__ == ['id']

    with raises(Exception) as got:
        NamespaceID('foo').attrib = 'whoops'
    assert_exception_correct(got.value, AttributeError(
        "'NamespaceID' object has no attribute 'attrib'"))


def test_namespace_attribs_init_pass():
    nsa = NamespaceUserAttributes()

    assert nsa.org is None
    assert nsa.env is None
    assert nsa.db is None
    assert nsa.desc is None

    nsa = NamespaceUserAttributes(None, None, None, None)

    assert nsa.org is None
    assert nsa.env is None
    assert nsa.db is None
    assert nsa.desc is None

    nsa = NamespaceUserAttributes('   \t    ', '   \t    ', '   \t    ', '   \t    ')

    assert nsa.org is None
    assert nsa.env is None
    assert nsa.db is None
    assert nsa.desc is None

    nsa = NamespaceUserAttributes('a' * 100, 'b' * 100, 'c' * 100, 'd' * 10000)

    assert nsa.org == 'a' * 100
    assert nsa.env == 'b' * 100
    assert nsa.db == 'c' * 100
    assert nsa.desc == 'd' * 10000


def test_namespace_attribs_init_fail():
    s101 = 'a' * 101
    s10001 = 'a' * 10001
    fail_namespace_attribs_init(s101, None, None, None, IllegalParameterError(
        'org ' + s101 + ' exceeds maximum length of 100'))
    fail_namespace_attribs_init(None, s101, None, None, IllegalParameterError(
        'env ' + s101 + ' exceeds maximum length of 100'))
    fail_namespace_attribs_init(None, None, s101, None, IllegalParameterError(
        'db ' + s101 + ' exceeds maximum length of 100'))
    fail_namespace_attribs_init(None, None, None, s10001, IllegalParameterError(
        'desc ' + s10001 + ' exceeds maximum length of 10000'))


def fail_namespace_attribs_init(org, env, db, desc, expected):
    with raises(Exception) as got:
        NamespaceUserAttributes(org, env, db, desc)
    assert_exception_correct(got.value, expected)


def test_namespace_attribs_equals():
    assert NamespaceUserAttributes() == NamespaceUserAttributes()
    assert NamespaceUserAttributes('foo', 'bar') == NamespaceUserAttributes('foo', 'bar')
    assert NamespaceUserAttributes(db='baz', desc='bat') == NamespaceUserAttributes(
        db='baz', desc='bat')
    assert NamespaceUserAttributes('foo', 'bar', 'baz', 'bat') == NamespaceUserAttributes(
        'foo', 'bar', 'baz', 'bat')

    assert NamespaceUserAttributes('foo', 'bar', 'baz', 'bat') != NamespaceUserAttributes(
        'foo1', 'bar', 'baz', 'bat')
    assert NamespaceUserAttributes('foo', 'bar', 'baz', 'bat') != NamespaceUserAttributes(
        'foo', 'bar1', 'baz', 'bat')
    assert NamespaceUserAttributes('foo', 'bar', 'baz', 'bat') != NamespaceUserAttributes(
        'foo', 'bar', 'baz1', 'bat')
    assert NamespaceUserAttributes('foo', 'bar', 'baz', 'bat') != NamespaceUserAttributes(
        'foo', 'bar', 'baz', 'bat1')
    assert NamespaceUserAttributes('bar') != NamespaceID('bar')


def test_namespace_attribs_hash():
    assert hash(NamespaceUserAttributes()) == hash(NamespaceUserAttributes())
    assert hash(NamespaceUserAttributes('foo', 'bar')) == hash(
        NamespaceUserAttributes('foo', 'bar'))
    assert hash(NamespaceUserAttributes(db='baz', desc='bat')) == hash(NamespaceUserAttributes(
        db='baz', desc='bat'))
    assert hash(NamespaceUserAttributes('foo', 'bar', 'baz', 'bat')) == hash(
        NamespaceUserAttributes('foo', 'bar', 'baz', 'bat'))

    assert hash(NamespaceUserAttributes('foo', 'bar', 'baz', 'bat')) != hash(
        NamespaceUserAttributes('foo1', 'bar', 'baz', 'bat'))
    assert hash(NamespaceUserAttributes('foo', 'bar', 'baz', 'bat')) != hash(
        NamespaceUserAttributes('foo', 'bar1', 'baz', 'bat'))
    assert hash(NamespaceUserAttributes('foo', 'bar', 'baz', 'bat')) != hash(
        NamespaceUserAttributes('foo', 'bar', 'baz1', 'bat'))
    assert hash(NamespaceUserAttributes('foo', 'bar', 'baz', 'bat')) != hash(
        NamespaceUserAttributes('foo', 'bar', 'baz', 'bat1'))


def test_namespace_init_pass():
    ns = Namespace(NamespaceID('foo'), True)
    assert ns.namespace_id == NamespaceID('foo')
    assert ns.is_publicly_mappable is True
    assert ns.authed_users == set()
    assert ns.attribs == NamespaceUserAttributes()

    ns = Namespace(NamespaceID('whee'), False, None)
    assert ns.namespace_id == NamespaceID('whee')
    assert ns.is_publicly_mappable is False
    assert ns.authed_users == set()
    assert ns.attribs == NamespaceUserAttributes()

    ns = Namespace(NamespaceID('baz'), True, set())
    assert ns.namespace_id == NamespaceID('baz')
    assert ns.is_publicly_mappable is True
    assert ns.authed_users == set()
    assert ns.attribs == NamespaceUserAttributes()

    ns = Namespace(NamespaceID('foo'), False, set([User(AuthsourceID('bar'), Username('baz'))]))
    assert ns.namespace_id == NamespaceID('foo')
    assert ns.is_publicly_mappable is False
    assert ns.authed_users == set([User(AuthsourceID('bar'), Username('baz'))])
    assert ns.attribs == NamespaceUserAttributes()

    ns = Namespace(NamespaceID('bar'), True, attribs=NamespaceUserAttributes('foo', 'bar'))
    assert ns.namespace_id == NamespaceID('bar')
    assert ns.is_publicly_mappable is True
    assert ns.authed_users == set()
    assert ns.attribs == NamespaceUserAttributes('foo', 'bar')

    ns = Namespace(NamespaceID('foo'), False, set([User(AuthsourceID('bar'), Username('baz'))]),
                   NamespaceUserAttributes('whee', 'whoo'))
    assert ns.namespace_id == NamespaceID('foo')
    assert ns.is_publicly_mappable is False
    assert ns.authed_users == set([User(AuthsourceID('bar'), Username('baz'))])
    assert ns.attribs == NamespaceUserAttributes('whee', 'whoo')


def test_namespace_init_fail():
    nsid = NamespaceID('foo')
    fail_namespace_init(None, None, TypeError('namespace_id cannot be None'))
    fail_namespace_init(nsid, set([User(AuthsourceID('as'), Username('foo')), None]),
                        TypeError('None item in authed_users'))


def fail_namespace_init(id_, authed_users, expected):
    with raises(Exception) as got:
        Namespace(id_, True, authed_users)
    assert_exception_correct(got.value, expected)


def test_namespace_without_users():
    ns = Namespace(NamespaceID('n'), True, set([User(AuthsourceID('a'), Username('u')),
                                                User(AuthsourceID('b'), Username('b'))]),
                   NamespaceUserAttributes('yay'))
    assert ns.without_users() == Namespace(NamespaceID('n'), True, set(),
                                           NamespaceUserAttributes('yay'))
    assert ns.without_users() == Namespace(NamespaceID('n'), True, None,
                                           NamespaceUserAttributes('yay'))


def test_namespace_equals():
    asid = AuthsourceID('as')
    assert Namespace(NamespaceID('foo'), True, None) == Namespace(NamespaceID('foo'), True, set())
    assert Namespace(NamespaceID('foo'), False, set([User(asid, 'foo'), User(asid, 'baz')])) == \
        Namespace(NamespaceID('foo'), False, set([User(asid, 'baz'), User(asid, 'foo')]))
    assert Namespace(NamespaceID('baz'), True, attribs=NamespaceUserAttributes('bleah')) == \
        Namespace(NamespaceID('baz'), True, set(), attribs=NamespaceUserAttributes('bleah'))

    assert Namespace(NamespaceID('bar'), True, set()) != Namespace(NamespaceID('foo'), True, set())
    assert Namespace(NamespaceID('foo'), False, set()) != \
        Namespace(NamespaceID('foo'), True, set())
    assert Namespace(NamespaceID('foo'), False, attribs=NamespaceUserAttributes('baz')) != \
        Namespace(NamespaceID('foo'), True, attribs=NamespaceUserAttributes(db='baz'))
    assert Namespace(NamespaceID('foo'), False, set([User(asid, 'foo'), User(asid, 'baz')])) != \
        Namespace(NamespaceID('foo'), False, set([User(asid, 'baz'), User(asid, 'fob')]))
    assert Namespace(NamespaceID('foo'), False, set()) != NamespaceID('foo')


def test_namespace_hash():
    # string hashes will change from instance to instance of the python interpreter, and therefore
    # tests can't be written that directly test the hash value. See
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    asid = AuthsourceID('as')
    assert hash(Namespace(NamespaceID('foo'), True, None)) == \
        hash(Namespace(NamespaceID('foo'), True, set()))
    assert hash(Namespace(NamespaceID('foo'), False,
                          set([User(asid, 'foo'), User(asid, 'baz')]))) == \
        hash(Namespace(NamespaceID('foo'), False, set([User(asid, 'baz'), User(asid, 'foo')])))
    assert hash(Namespace(NamespaceID('baz'), True, attribs=NamespaceUserAttributes('bleah'))) == \
        hash(Namespace(NamespaceID('baz'), True, set(), attribs=NamespaceUserAttributes('bleah')))

    assert hash(Namespace(NamespaceID('bar'), True, set())) != \
        hash(Namespace(NamespaceID('foo'), True, set()))
    assert hash(Namespace(NamespaceID('foo'), False, set())) != \
        hash(Namespace(NamespaceID('foo'), True, set()))
    assert hash(Namespace(NamespaceID('foo'), False,
                          set([User(asid, 'foo'), User(asid, 'baz')]))) != \
        hash(Namespace(NamespaceID('foo'), False, set([User(asid, 'baz'), User(asid, 'fob')])))
    assert hash(Namespace(NamespaceID('baz'), True, attribs=NamespaceUserAttributes('bleah'))) != \
        hash(Namespace(NamespaceID('baz'), True, set(), attribs=NamespaceUserAttributes('bleah1')))


def test_object_id_init_pass():
    a = 'abcdefghijklmnopqrstuvwxyz'
    oidstr = a + a.upper() + r'0123456789!@#$%^&*()_+`~{}[]\|/<>,.?' + ('a' * 912)
    oid = ObjectID(NamespaceID('foo'), oidstr)

    assert oid.namespace_id == NamespaceID('foo')
    assert oid.id == oidstr


def test_object_id_init_fail():
    ns = NamespaceID('foo')
    fail_object_id_init(None, 'o', TypeError('namespace_id cannot be None'))
    fail_object_id_init(ns, None, MissingParameterError('data id'))
    fail_object_id_init(ns, '   \t   \n    ', MissingParameterError('data id'))
    fail_object_id_init(ns, 'a' * 1001, IllegalParameterError(
        'data id ' + ('a' * 1001) + ' exceeds maximum length of 1000'))


def fail_object_id_init(namespace_id, obj_id, expected):
    with raises(Exception) as got:
        ObjectID(namespace_id, obj_id)
    assert_exception_correct(got.value, expected)


def test_object_id_equals():
    assert ObjectID(NamespaceID('foo'), 'baz') == ObjectID(NamespaceID('foo'), 'baz')
    assert ObjectID(NamespaceID('foo'), 'baz') != ObjectID(NamespaceID('bar'), 'baz')
    assert ObjectID(NamespaceID('foo'), 'baz') != ObjectID(NamespaceID('foo'), 'bar')
    assert ObjectID(NamespaceID('foo'), 'baz') != NamespaceID('foo')


def test_object_id_hash():
    # string hashes will change from instance to instance of the python interpreter, and therefore
    # tests can't be written that directly test the hash value. See
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    assert hash(ObjectID(NamespaceID('foo'), 'bar')) == hash(ObjectID(NamespaceID('foo'), 'bar'))
    assert hash(ObjectID(NamespaceID('bar'), 'foo')) == hash(ObjectID(NamespaceID('bar'), 'foo'))
    assert hash(ObjectID(NamespaceID('baz'), 'foo')) != hash(ObjectID(NamespaceID('bar'), 'foo'))
    assert hash(ObjectID(NamespaceID('bar'), 'fob')) != hash(ObjectID(NamespaceID('bar'), 'foo'))


def test_object_id_slots():
    assert ObjectID(NamespaceID('bar'), 'foo').__slots__ == ['namespace_id', 'id']

    with raises(Exception) as got:
        ObjectID(NamespaceID('foo'), 'bar').attrib = 'whoops'
    assert_exception_correct(got.value, AttributeError(
        "'ObjectID' object has no attribute 'attrib'"))
