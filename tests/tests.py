# -*- coding: utf-8 -*-.
import os
import time
from imp import reload

from django.conf import settings as django_settings
from django.contrib.sessions.backends.base import CreateError
from django.core import management
from django.contrib.sessions.models import Session

from redis_sessions_fork import settings as session_settings
from redis_sessions_fork import connection, utils, backend


session_module = utils.import_module(django_settings.SESSION_ENGINE)
session = session_module.SessionStore()


management.call_command('syncdb', interactive=False)


def test_redis_prefix():
    assert utils.add_prefix('foo') == \
        '%s:foo' % django_settings.SESSION_REDIS_PREFIX

    assert 'foo' == utils.remove_prefix(utils.add_prefix('foo'))

    session_settings.SESSION_REDIS_PREFIX = ''

    assert utils.add_prefix('foo') == 'foo'
    assert 'foo' == utils.remove_prefix(utils.add_prefix('foo'))


def test_modify_and_keys():
    assert not session.modified

    session['test'] = 'test_me'

    assert session.modified

    assert session['test'] == 'test_me'


def test_save_and_delete():
    session['key'] = 'value'
    session.save()

    assert session.exists(session.session_key)

    session.delete(session.session_key)

    assert not session.exists(session.session_key)


def test_flush():
    session['key'] = 'another_value'
    session.save()

    key = session.session_key

    session.flush()

    assert not session.exists(key)


def test_items():
    session['item1'], session['item2'] = 1, 2
    session.save()

    # Python 3.* fix
    assert sorted(list(session.items())) == [('item1', 1), ('item2', 2)]


def test_expiry():
    session.set_expiry(1)

    assert session.get_expiry_age() == 1

    session['key'] = 'expiring_value'
    session.save()

    key = session.session_key

    assert session.exists(key)

    time.sleep(2)

    assert not session.exists(key)


def test_save_and_load():
    session.set_expiry(60)
    session.setdefault('item_test', 8)
    session.save()

    session_data = session.load()

    assert session_data.get('item_test') == 8


def test_save_and_load_nonascii():
    session['nonascii'] = 'тест'
    session.save()

    session_data = session.load()

    assert utils.force_unicode(session_data['nonascii']) == \
        utils.force_unicode('тест')


def test_save_existing_key():
    try:
        session.save(must_create=True)

        assert False
    except CreateError:
        pass


def test_redis_url_config():
    reload(session_settings)

    session_settings.SESSION_REDIS_URL = 'redis://localhost:6379/0'

    reload(connection)

    redis_server = connection.redis_server

    host = redis_server.connection_pool.connection_kwargs.get('host')
    port = redis_server.connection_pool.connection_kwargs.get('port')
    db = redis_server.connection_pool.connection_kwargs.get('db')

    assert host == 'localhost'
    assert port == 6379
    assert db == 0


def test_unix_socket():
    # Uncomment this in `redis.conf`:
    #
    # unixsocket /tmp/redis.sock
    # unixsocketperm 755
    reload(session_settings)

    session_settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH = \
        'unix:///tmp/redis.sock'

    reload(connection)

    redis_server = connection.redis_server

    path = redis_server.connection_pool.connection_kwargs.get('path')
    db = redis_server.connection_pool.connection_kwargs.get('db')

    assert path == session_settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH

    assert db == 0


test_connection_pool = connection.redis.ConnectionPool(
    host=session_settings.SESSION_REDIS_HOST,
    port=session_settings.SESSION_REDIS_PORT,
    db=session_settings.SESSION_REDIS_DB,
    password=session_settings.SESSION_REDIS_PASSWORD
)


def test_with_connection_pool_config():
    reload(session_settings)

    session_settings.SESSION_REDIS_CONNECTION_POOL = \
        'tests.tests.test_connection_pool'

    reload(connection)

    redis_server = connection.redis_server

    assert redis_server.connection_pool == test_connection_pool


def test_redis_url_config_from_env():
    reload(session_settings)

    os.environ['MYREDIS_URL'] = 'redis://localhost:6379/0'

    reload(session_settings)
    reload(connection)

    redis_server = connection.redis_server

    host = redis_server.connection_pool.connection_kwargs.get('host')
    port = redis_server.connection_pool.connection_kwargs.get('port')
    db = redis_server.connection_pool.connection_kwargs.get('db')

    assert host == 'localhost'
    assert port == 6379
    assert db == 0


def test_serializers():
    test_object = {'foo': 'bar'}

    for class_name in ('UjsonSerializer',):
        try:
            serializer = utils.import_by_path(
                'redis_sessions_fork.serializers.%s' % class_name
            )()
        except ImportError:
            continue

        serializer_data = serializer.loads(serializer.dumps(test_object))

        assert test_object == serializer_data


def test_flush_redis_sessions():
    session['foo'] = 'bar'
    session.save()

    keys_before_flush = backend.keys('*')

    management.call_command('flush_redis_sessions')

    keys_after_flush = backend.keys('*')

    assert not keys_before_flush == keys_after_flush

    assert len(keys_after_flush) == 0


def test_migrate_to_orm():
    session['foo'] = 'bar'
    session.save()

    management.call_command('migrate_sessions_to_orm')

    orm_session = Session.objects.all()[0]

    assert session.decode(orm_session.session_data)['foo'] == 'bar'


def test_migrate_to_redis():
    management.call_command('flush_redis_sessions')

    management.call_command('migrate_sessions_to_redis')

    orm_session = Session.objects.all()[0]

    check_session = session_module.SessionStore(
        session_key=orm_session.session_key
    )

    assert check_session.load()['foo'] == 'bar'


def test_flush_orm_sessions():
    management.call_command('flush_orm_sessions')

    orm_session = Session.objects.all()

    assert orm_session.count() == 0
