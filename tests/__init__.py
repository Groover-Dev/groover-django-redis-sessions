from __future__ import absolute_import, unicode_literals

from django.conf import settings


settings.configure(
    SESSION_ENGINE='redis_sessions_fork.session',
    # SESSION_SERIALIZER='redis_sessions_fork.serializers.UjsonSerializer',
    SESSION_REDIS_PREFIX='django_sessions_tests',
    INSTALLED_APPS=(
        'django.contrib.sessions',
        'redis_sessions_fork'
    ),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }
)


try:
    # django 1.7 standalone app setup
    import django
    django.setup()
except AttributeError:
    pass
