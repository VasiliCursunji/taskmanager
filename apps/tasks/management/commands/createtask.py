from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone

from apps.tasks.models import Task, Timelog


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(id=1)
        for i in range(25000):
            task = Task.objects.create(
                title=f'string{i}',
                description=f'string{i}',
                completed=False,
                created_by=user,
                assigned_by=user,
            )

            Timelog.objects.create(
                task=task,
                user=user,
                started_at=timezone.now(),
                duration=timedelta(10)
            )

