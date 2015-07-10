from django.core.management.base import NoArgsCommand
from django.db.utils import DatabaseError
from django.db import transaction, connection
from django.contrib.sessions.models import Session


class Command(NoArgsCommand):
    help = 'flush all django orm sessions'

    def handle_noargs(self, *args, **wargs):
        cursor = connection.cursor()

        try:  # raw sql truncate
            cursor.execute(
                'TRUNCATE TABLE %s' % Session._meta.db_table
            )
            if hasattr(transaction, 'commit_unless_managed'):
                transaction.commit_unless_managed()
        except DatabaseError:  # sqlite fix
            cursor.execute(
                'DELETE FROM %s' % Session._meta.db_table
            )
            if hasattr(transaction, 'commit_unless_managed'):
                transaction.commit_unless_managed()
        except DatabaseError:  # otherwise via django orm
            Session.objects.all.delete()
