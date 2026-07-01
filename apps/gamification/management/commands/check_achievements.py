from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.gamification.utils import check_achievements


class Command(BaseCommand):
    help = 'Manually check and unlock achievements for all users'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username to check (optional)')

    def handle(self, *args, **options):
        if options.get('user'):
            users = User.objects.filter(username=options['user'])
        else:
            users = User.objects.all()

        for user in users:
            unlocked = check_achievements(user)
            if unlocked:
                self.stdout.write(self.style.SUCCESS(f'✅ {user.username}: Unlocked {len(unlocked)} new achievements'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ {user.username}: No new achievements'))

        self.stdout.write(self.style.SUCCESS('🎉 Achievement check complete!'))