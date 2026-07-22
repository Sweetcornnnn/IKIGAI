from django.core.management.base import BaseCommand
import os
import sys
import subprocess

class Command(BaseCommand):
    help = 'Runs the server with Daphne (ASGI)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting IKIGAI with Daphne ASGI server...'))
        os.system('daphne core.asgi:application')