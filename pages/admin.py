from django.contrib import admin
from .models import DiagnosisHistory # Import model DiagnosisHistory

# Register your models here.
# Đăng ký model DiagnosisHistory để quản lý trong trang admin
admin.site.register(DiagnosisHistory)