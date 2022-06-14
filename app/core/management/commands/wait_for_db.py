"""
Django command to wait for DB to be available.
"""
import time
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        # standard output to screen
        self.stdout.write('Waiting for database...')
        # init db status variable
        db_up = False

        # as long as DB not up, keep attempting connection
        while db_up == False:
            try:
                # Check on connected status of default databases
                self.check(databases=['default'])
                # if no exception thrown, set db_up to true
                db_up = True

            # If below errors raised
            except (Psycopg2Error, OperationalError):
                self.stdout.write('DB unavailable. Waiting 1 second...')
                # wait 1 second
                time.sleep(1)

        # If db is already up
        self.stdout.write(self.style.SUCCESS('Database available!'))

    # return super().handle(*args, **options)
