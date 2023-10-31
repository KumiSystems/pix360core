from django.core.management.base import BaseCommand, CommandError

from ...installer import Installer

import logging

class Command(BaseCommand):
    help = 'Run the worker'

    def handle(self, *args, **options):
        """Handle the command
        """
        installer = Installer()
        installer.install_all()
