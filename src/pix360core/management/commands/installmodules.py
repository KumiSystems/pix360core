from django.core.management.base import BaseCommand

from ...installer import Installer

class Command(BaseCommand):
    help = 'Run the worker'

    def handle(self, *args, **options):
        """Handle the command
        """
        installer = Installer()
        installer.install_all()
