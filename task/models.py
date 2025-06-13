from django.db import models
from django.conf import settings
from project.models import Project
# from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
User = get_user_model()

class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField()

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # history = HistoricalRecords()

    def __str__(self):
        return self.title

class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="logs")
    field_changed = models.CharField(max_length=50)  # مثل 'status' أو 'assignee'
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    modified_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.field_changed} changed on {self.task.title} at {self.modified_at}"