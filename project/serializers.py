from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, ProjectMembership
from task.serializers import TaskSerializer  # استخدمه لعرض المهام
from django.db import transaction

User = get_user_model()

class ProjectMembershipOutputSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = ProjectMembership
        fields = ['username', 'role']

class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField(read_only=True)
    members = serializers.SerializerMethodField(read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    members_input = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'manager', 'members', 'members_input','tasks']

    def get_manager(self, obj):
        manager = obj.manager
        return manager.username if manager else None

    def get_members(self, obj):
        memberships = obj.projectmembership_set.exclude(role='manager')
        return ProjectMembershipOutputSerializer(memberships, many=True).data

    def create(self, validated_data):
        print("Request user is:", self.context.get('request').user)

        members_data = validated_data.pop('members_input', [])
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request not found in context.")
        user = request.user
        with transaction.atomic():
            project = Project.objects.create(**validated_data)
            ProjectMembership.objects.create(user=user, project=project, role='manager')
            print("Manager membership created for user:", user.username)
        
            missing_users = []
            for member in members_data:
                user_id = member.get('user_id')
                role = member.get('role', 'member')

                if role not in ['manager', 'member']:
                    continue

                try:
                    member_user = User.objects.get(id=user_id)
                    if member_user == user:
                        continue

                    if ProjectMembership.objects.filter(user=member_user, project=project).exists():
                        continue

                    ProjectMembership.objects.create(user=member_user, project=project, role=role)
                    print("Added member:", member_user.username, "as", role)

                except User.DoesNotExist:
                    missing_users.append(user_id)
            if missing_users:
                raise serializers.ValidationError({
                    'detail': 'Some users were not found.',
                    'missing_users': missing_users
                })
        return project
