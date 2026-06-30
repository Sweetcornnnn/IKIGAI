from django.core.management.base import BaseCommand
from apps.gamification.models import Achievement


class Command(BaseCommand):
    help = 'Load initial achievements into the database'

    def handle(self, *args, **kwargs):
        achievements = [
            # Task achievements
            {
                'name': 'First Steps',
                'description': 'Complete your first task',
                'category': 'TASKS',
                'icon': '🌱',
                'requirement_type': 'TASKS_COMPLETED',
                'requirement_value': 1,
                'xp_reward': 10,
                'order': 1,
            },
            {
                'name': 'Task Novice',
                'description': 'Complete 10 tasks',
                'category': 'TASKS',
                'icon': '📋',
                'requirement_type': 'TASKS_COMPLETED',
                'requirement_value': 10,
                'xp_reward': 25,
                'order': 2,
            },
            {
                'name': 'Task Master',
                'description': 'Complete 50 tasks',
                'category': 'TASKS',
                'icon': '⭐',
                'requirement_type': 'TASKS_COMPLETED',
                'requirement_value': 50,
                'xp_reward': 50,
                'order': 3,
            },
            {
                'name': 'Productivity Legend',
                'description': 'Complete 100 tasks',
                'category': 'TASKS',
                'icon': '🏅',
                'requirement_type': 'TASKS_COMPLETED',
                'requirement_value': 100,
                'xp_reward': 100,
                'order': 4,
            },
            {
                'name': 'Task God',
                'description': 'Complete 500 tasks',
                'category': 'TASKS',
                'icon': '👑',
                'requirement_type': 'TASKS_COMPLETED',
                'requirement_value': 500,
                'xp_reward': 250,
                'order': 5,
            },

            # Streak achievements
            {
                'name': 'Consistency Beginner',
                'description': 'Maintain a 3-day streak',
                'category': 'STREAK',
                'icon': '🔥',
                'requirement_type': 'STREAK_DAYS',
                'requirement_value': 3,
                'xp_reward': 15,
                'order': 10,
            },
            {
                'name': 'Streak Warrior',
                'description': 'Maintain a 7-day streak',
                'category': 'STREAK',
                'icon': '⚔️',
                'requirement_type': 'STREAK_DAYS',
                'requirement_value': 7,
                'xp_reward': 30,
                'order': 11,
            },
            {
                'name': 'Habit Builder',
                'description': 'Maintain a 14-day streak',
                'category': 'STREAK',
                'icon': '🏗️',
                'requirement_type': 'STREAK_DAYS',
                'requirement_value': 14,
                'xp_reward': 50,
                'order': 12,
            },
            {
                'name': 'Dedicated Achiever',
                'description': 'Maintain a 30-day streak',
                'category': 'STREAK',
                'icon': '🎯',
                'requirement_type': 'STREAK_DAYS',
                'requirement_value': 30,
                'xp_reward': 100,
                'order': 13,
            },
            {
                'name': 'Iron Will',
                'description': 'Maintain a 100-day streak',
                'category': 'STREAK',
                'icon': '💎',
                'requirement_type': 'STREAK_DAYS',
                'requirement_value': 100,
                'xp_reward': 300,
                'order': 14,
            },

            # Level achievements
            {
                'name': 'Level 5',
                'description': 'Reach level 5',
                'category': 'LEVEL',
                'icon': '🌟',
                'requirement_type': 'LEVEL_REACHED',
                'requirement_value': 5,
                'xp_reward': 20,
                'order': 20,
            },
            {
                'name': 'Level 10',
                'description': 'Reach level 10',
                'category': 'LEVEL',
                'icon': '💫',
                'requirement_type': 'LEVEL_REACHED',
                'requirement_value': 10,
                'xp_reward': 50,
                'order': 21,
            },
            {
                'name': 'Level 25',
                'description': 'Reach level 25',
                'category': 'LEVEL',
                'icon': '🌟',
                'requirement_type': 'LEVEL_REACHED',
                'requirement_value': 25,
                'xp_reward': 100,
                'order': 22,
            },
            {
                'name': 'Level 50',
                'description': 'Reach level 50',
                'category': 'LEVEL',
                'icon': '✨',
                'requirement_type': 'LEVEL_REACHED',
                'requirement_value': 50,
                'xp_reward': 200,
                'order': 23,
            },
            {
                'name': 'Habit Starter',
                'description': 'Create your first habit',
                'category': 'HABITS',
                'icon': '🌱',
                'requirement_type': 'HABITS_CREATED',
                'requirement_value': 1,
                'xp_reward': 15,
                'order': 30,
            },
            {
                'name': 'Habit Builder',
                'description': 'Create 5 habits',
                'category': 'HABITS',
                'icon': '🌿',
                'requirement_type': 'HABITS_CREATED',
                'requirement_value': 5,
                'xp_reward': 30,
                'order': 31,
            },
            {
                'name': 'Habit Master',
                'description': 'Complete all habits for 7 days in a row',
                'category': 'HABITS',
                'icon': '🌳',
                'requirement_type': 'HABITS_COMPLETED',
                'requirement_value': 7,
                'xp_reward': 50,
                'order': 32,
            },
        ]

        for data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created achievement: {achievement.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Achievement already exists: {achievement.name}'))

        self.stdout.write(self.style.SUCCESS('All achievements loaded successfully!'))