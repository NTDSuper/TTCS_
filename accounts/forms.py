# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User # Hoặc Custom User Model nếu bạn dùng

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    # Thêm các trường khác nếu bạn muốn (ví dụ: first_name, last_name)

    class Meta(UserCreationForm.Meta):
        model = User # Chỉ định User model (mặc định hoặc custom)
        # Thêm 'email' và các trường tùy chỉnh khác vào fields
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')
       