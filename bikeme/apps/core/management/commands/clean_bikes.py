import datetime

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.timezone import now

from bikeme.apps.core.models import Station, Snapshot


class Command(BaseCommand):
    help = 'Clean old data'

    def handle(self, *args, **options):
        from_datetime = now() - datetime.timedelta(days=60)  # XXX magic number
        # manually clear Stations linked to old snapshots
        print (Station.objects.filter(latest_snapshot__timestamp__lte=from_datetime)
            .update(latest_snapshot=None))
        total_start = Snapshot.objects.count()
        # delete using raw SQL because django is slow
        cursor = connection.cursor()
        cursor.execute("DELETE FROM core_snapshot "
            "WHERE timestamp < now() - interval '60 days'")
        total_end = Snapshot.objects.count()
        print 'Started with {}, deleted {} ({}%)'.format(
            total_start,
            total_start - total_end,
            (total_start - total_end) * 100 / total_start
        )
