from django.core.management.base import BaseCommand

from bikeme.apps.core.utils import update_all_markets


class Command(BaseCommand):
    help = 'Scrape all markets. Specify slugs to restrict to those markets.'

    def handle(self, *args, **options):
        update_all_markets(*args)
