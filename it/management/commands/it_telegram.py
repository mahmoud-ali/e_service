from time import sleep
from django.core.management.base import BaseCommand, CommandError

from ._telegram_main import main as bot_main
class Command(BaseCommand):
    help = "IT agent"

    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        try:
            while True:
                bot_main()
                sleep(300)
            # self.stdout.write(
            #     self.style.SUCCESS('Hello from hr_bot')
            # )
        except Exception as e:
            raise CommandError(f'Error: {e}')
        