# from django.test import TestCase
# from rest_framework.test import APIClient
# from django.contrib.auth import get_user_model
# from project.models import Project
# from task.models import Task
# User = get_user_model()

# class TaskPermissionsTest(TestCase):
#     def setUp(self):
#         self.manager = User.objects.create_user(
#             username='manager', email='manager@example.com', password='pass123'
#         )
#         self.member = User.objects.create_user(
#             username='member', email='member@example.com', password='pass123'
#         )
#         self.other_user = User.objects.create_user(
#             username='other', email='other@example.com', password='pass123'
#         )

#         self.project = Project.objects.create(
#             name="Test Project",
#             description="Project description",
#             manager=self.manager
#         )
#         self.task = Task.objects.create(
#             title="Test Task",
#             description="Task description",
#             project=self.project,
#             assignee=self.member,
#             status='todo'
#         )

#         self.client_manager = APIClient()
#         self.client_manager.force_authenticate(user=self.manager)

#         self.client_member = APIClient()
#         self.client_member.force_authenticate(user=self.member)

#         self.client_other = APIClient()
#         self.client_other.force_authenticate(user=self.other_user)

#     def test_manager_can_edit_task(self):
#         response = self.client_manager.patch(f'/api/tasks/{self.task.id}/', {'status': 'done'}, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.task.refresh_from_db()
#         self.assertEqual(self.task.status, 'done')

#     # def test_assignee_can_edit_task(self):
#     #     # الشخص المكلف يستطيع تعديل المهمة
#     #     response = self.client_member.patch(f'/api/tasks/{self.task.id}/', {'status': 'in_progress'}, format='json')
#     #     self.assertEqual(response.status_code, 200)
#     #     self.task.refresh_from_db()
#     #     self.assertEqual(self.task.status, 'in_progress')

#     # def test_other_user_cannot_edit_task(self):
#     #     # مستخدم آخر لا يستطيع تعديل المهمة
#     #     response = self.client_other.patch(f'/api/tasks/{self.task.id}/', {'status': 'done'}, format='json')
#     #     self.assertEqual(response.status_code, 403)  # Forbidden

#     # def test_create_project(self):
#     #     # اختبار إنشاء مشروع جديد عبر API
#     #     data = {'name': 'New Project', 'description': 'Desc', 'owner': self.manager.id}
#     #     response = self.client_manager.post('/api/projects/', data, format='json')
#     #     self.assertEqual(response.status_code, 201)
#     #     self.assertEqual(response.data['name'], 'New Project')

#     # def test_task_filtering_by_status(self):
#     #     # اختبار التصفية: مثلاً جلب المهام بحالة معينة
#     #     response = self.client_manager.get('/api/tasks/?status=todo')
#     #     self.assertEqual(response.status_code, 200)
#     #     for task in response.data:
#     #         self.assertEqual(task['status'], 'todo')
