from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, Sum
from django.utils import timezone


class TaskQuerySet(QuerySet):
    def with_total_duration(self):
        return self.annotate(total_duration=Sum('timelog__duration'))


class Task(models.Model):
    objects = TaskQuerySet.as_manager()

    title = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    completed = models.BooleanField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created', null=True)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned', null=True)

    def __str__(self):
        return self.title

    def complete(self):
        self.completed = True


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()

    def __str__(self):
        return self.task.title


class Timelog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='timelog')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    duration = models.DurationField()

    def __str__(self):
        return self.task.title


class Timer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_stopped = models.BooleanField(default=False)
    is_running = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True)
    duration = models.DurationField(default=timedelta())

    def start(self):
        if self.is_stopped:
            raise ValueError("Timer is stopped")

        if not self.is_running:
            self.started_at = timezone.now()
            self.is_running = True
            self.save()

    def pause(self):
        if self.is_stopped:
            raise ValueError("Timer is stopped")

        if self.is_running:
            duration = timezone.now() - self.started_at
            self.duration += duration
            self.started_at = self.started_at
            self.is_running = False
            self.save()

            Timelog.objects.create(
                task=self.task,
                user=self.user,
                started_at=self.started_at,
                duration=duration
            )

    def reset(self):
        if self.is_stopped:
            raise ValueError("Timer is stopped")

        self.is_running = False
        self.is_stopped = False
        self.started_at = None
        self.duration = timedelta()
        self.save()

    def stop(self):
        if self.is_stopped:
            raise ValueError("Timer is stopped")

        self.pause()
        self.is_stopped = True
        self.save()

    @property
    def total_duration(self):
        now = timezone.now()
        return self.duration + ((now - (self.started_at or now)) * int(self.is_running))
