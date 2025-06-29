# accounts/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import login # Tùy chọn: tự động đăng nhập sau khi đăng ký
from .forms import SignUpForm
from django.contrib import messages # Để hiển thị thông báo

class SignUpView(View):
    form_class = SignUpForm
    template_name = 'registration/signup.html' # Template sẽ tạo ở bước sau

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save() # Lưu user mới, tự động hash password
            messages.success(request, 'Registration successful! You can now log in.')
            # Tùy chọn: Tự động đăng nhập người dùng sau khi đăng ký
            # login(request, user)
            # return redirect('pages:home') # Chuyển hướng đến trang chủ nếu tự động đăng nhập

            # Hoặc chuyển hướng đến trang đăng nhập
            return redirect('login') # 'login' là name mặc định của Django auth login url
        else:
            # Form không hợp lệ, hiển thị lại form với lỗi
            messages.error(request, 'Please correct the errors below.')
            return render(request, self.template_name, {'form': form})