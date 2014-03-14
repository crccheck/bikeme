from django.core.management.base import BaseCommand

from bikeme.apps.core.utils import update_all_markets


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        update_all_markets()
