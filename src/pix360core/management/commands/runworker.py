from django.core.management.base import BaseCommand, CommandError

from pix360core.models import Conversion, ConversionStatus
from pix360core.worker import Worker

import logging

class Command(BaseCommand):
    help = 'Run the worker'

    def handle(self, *args, **options):
        """Handle the command
        """
        worker = Worker()
        worker.run()
