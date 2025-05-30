from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def manager(self):
        membership = self.projectmembership_set.filter(role='manager').first()
        if membership:
            return membership.user
        return None

from django.db import models
from django.conf import settings

class ProjectMembership(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('member', 'Member'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f'{self.user.username} - {self.project.name} ({self.role})'
