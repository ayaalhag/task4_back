from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'assignee', 'due_date', 'project']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
