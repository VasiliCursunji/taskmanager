from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    completed = models.BooleanField(default=False)
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


class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time-logs')
    is_running = models.BooleanField()
    is_paused = models.BooleanField()
    is_stopped = models.BooleanField()
    started_at = models.DateTimeField()
    stopped_at = models.DateTimeField()
    duration = models.DurationField(default=timedelta(0))

    def __str__(self):
        return self.task.title

    def set_duration(self):
        self.duration += self.stopped_at - self.started_at

    def start(self):
        if self.is_stopped is False and self.is_running is False:
            self.is_running = True
            self.is_paused = False
            self.started_at = datetime.now()

    def pause(self):
        if self.is_stopped is False and self.is_running is True:
            self.is_running = False
            self.is_paused = True

    def stop(self):
        if self.is_stopped is False:
            self.stopped_at = datetime.now()
            self.set_duration()
            self.is_running = False
            self.is_paused = False
            self.is_stopped = True
