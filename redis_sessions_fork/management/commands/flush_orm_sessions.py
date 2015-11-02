from __future__ import absolute_import, unicode_literals

from django.contrib.sessions.models import Session
from django.core.management.base import NoArgsCommand
from django.db import connection, transaction
from django.db.utils import DatabaseError

if hasattr(transaction, 'atomic'):
    atomic = transaction.atomic
else:
    from contextlib import contextmanager

    @contextmanager
    def atomic(using=None):
        yield
        transaction.commit_unless_managed(using=using)


class Command(NoArgsCommand):
    help = 'flush all django orm sessions'

    def handle_noargs(self, *args, **wargs):
        cursor = connection.cursor()

        try:  # raw sql truncate
            with atomic():
                cursor.execute(
                    'TRUNCATE TABLE %s' % Session._meta.db_table
                )
        except DatabaseError:  # sqlite fix
            with atomic():
                cursor.execute(
                    'DELETE FROM %s' % Session._meta.db_table
                )
        except DatabaseError:  # otherwise via django orm
            with atomic():
                Session.objects.all.delete()
