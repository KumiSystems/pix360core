from django.core.management.base import BaseCommand

from pix360core.worker import Worker

class Command(BaseCommand):
    help = "Run the worker"

    def handle(self, *args, **options):
        """Handle the command"""
        worker = Worker()
        worker.run()
