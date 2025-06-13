from rest_framework import serializers
from .models import Task
from .models import TaskLog

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskLogSerializer(serializers.ModelSerializer):
    modified_by = serializers.StringRelatedField()  # يعرض اسم المستخدم بدلاً من ID

    class Meta:
        model = TaskLog
        fields = [
            'id',
            'field_changed',
            'old_value',
            'new_value',
            'modified_by',
            'modified_at',
        ]
