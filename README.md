# Task Manager API (Django + DRF)

هذا المشروع هو نظام إدارة مهام بسيط باستخدام Django و Django REST Framework.  
يوفر ميزات مثل تسجيل المستخدمين وتسجيل الدخول، وإنشاء المشاريع، وتعيين المهام، وتصفية المهام بناءً على الحالة.

---

## 🚀 كيفية تشغيل المشروع

### 1. استنساخ المشروع

```bash
git clone https://github.com/ayaalhag/task4_back.git
cd task4_back
python -m venv env
source env/Scripts/activate  
python manage.py migrate
python manage.py runserver
POST /api/register/
{
  "username": "example",
  "email": "user@example.com",
  "password": "yourpassword"
}
POST /api/login/
{
  "username": "example",
  "password": "yourpassword"
}
{
  "refresh": "token...",
  "access": "token..."
}




