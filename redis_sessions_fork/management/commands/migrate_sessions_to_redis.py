from __future__ import absolute_import, unicode_literals

from django.contrib.sessions.models import Session
from django.core.management.base import NoArgsCommand

from ... import backend
from ...utils import total_seconds

try:  # Django >= 1.4
    from django.utils import timezone
except ImportError:  # Django < 1.4
    from datetime import datetime as timezone


class Command(NoArgsCommand):
    help = 'copy django orm sessions to redis'

    def handle_noargs(self, *args, **kwargs):
        sessions = Session.objects.filter(expire_date__gt=timezone.now())
        count = sessions.count()
        counter = 1

        self.stdout.write('sessions to copy %d\n' % count)

        for session in sessions:
            self.stdout.write('processing %d of %d\n' % (counter, count))

            expire_in = session.expire_date - timezone.now()
            expire_in = round(total_seconds(expire_in))

            if expire_in < 0:
                continue

            backend.delete(session.session_key)

            backend.save(
                session.session_key,
                expire_in,
                session.session_data,
                False
            )

            counter += 1
