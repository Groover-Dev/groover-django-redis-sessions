from __future__ import absolute_import, unicode_literals

import datetime
from binascii import Error

from django.contrib.sessions.models import Session
from django.core.management.base import NoArgsCommand

from ... import backend, utils
from ...session import SessionStore

try:  # Django >= 1.4
    from django.utils import timezone
except ImportError:  # Django < 1.4
    from datetime import datetime as timezone


class Command(NoArgsCommand):
    help = 'copy redis sessions to django orm'

    def handle_noargs(self, *args, **kwargs):
        session_keys = backend.keys('*')

        count = len(session_keys)
        counter = 1

        self.stdout.write('sessions to copy %d\n' % count)

        for session_key in session_keys:
            self.stdout.write('processing %d of %d\n' % (counter, count))

            session_data = backend.get(session_key)

            if session_data is not None:
                try:
                    SessionStore().decode(session_data)
                except (Error, TypeError):
                    continue

                expire_date = timezone.now() + datetime.timedelta(
                    seconds=backend.expire(session_key)
                )

                session_key = utils.remove_prefix(session_key)

                Session.objects.filter(session_key=session_key).delete()

                Session(
                    session_key=session_key,
                    session_data=session_data,
                    expire_date=expire_date
                ).save()

            counter += 1
