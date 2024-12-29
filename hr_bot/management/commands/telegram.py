from django.core.management.base import BaseCommand, CommandError

from .telegram_main import main as bot_main
class Command(BaseCommand):
    help = "HR agent"

    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        try:
            bot_main()
            # self.stdout.write(
            #     self.style.SUCCESS('Hello from hr_bot')
            # )
        except Exception as e:
            raise CommandError(f'Error: {e}')
        