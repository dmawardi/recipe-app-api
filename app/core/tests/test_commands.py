"""
Test custom Django management commands.
"""

# Import for mocking behavior of DB
from unittest.mock import patch

# Import Errors that can be used to recoginise DB error
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError

# Allows calling of shell commands
from django.core.management import call_command
from django.test import SimpleTestCase

# Creates a mock to be used as argument in function (patched_check)


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test if database is ready"""
        # Mock response init
        patched_check.return_value = True

        # calls wait for db command
        call_command('wait_for_db')

        # checks that patched command is being called with argument with default db
        patched_check.assert_called_once_with(databases=["default"])

    # Replaces sleep object with mock function
    @patch('time.sleep')
    # patched arguments are applied inside out. patched sleep before patched check
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        # side effect allows mocking multiple times.
        # This will mock psycopg2error twice, OperErorr 3 times, then return true
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        # Checks that call_count is equal to 6
        self.assertEqual(patched_check.call_count, 6)
        # Check that patched_check was called with default db settings
        patched_check.assert_called_with(databases=["default"])
