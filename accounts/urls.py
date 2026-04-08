from django.urls import path
from .views import SignUpView # Import view đăng ký
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    # Thêm URL cho trang đăng ký
    path("signup/", SignUpView.as_view(), name="signup"),
    # Các URL khác của accounts (nếu có)
     path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Sử dụng LogoutView có sẵn
    # next_page='login' sẽ chuyển hướng người dùng về trang đăng nhập sau khi logout
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # Bạn có thể thêm các URL khác liên quan đến tài khoản ở đây (ví dụ: password reset)
]