# pages/urls.py
from django.urls import path,include
from .views import HomePageView, ContactPageView, FAQPageView, diagnose, predict
from django.conf import settings
from django.conf.urls.static import static


app_name = 'pages' 

urlpatterns = [
   


    # URLs của ứng dụng pages (yêu cầu đăng nhập được xử lý trong views)
    path("", HomePageView.as_view(), name="home"),
    path("contact/", ContactPageView.as_view(), name="contact"),
    path("faq/", FAQPageView.as_view(), name="faq"),

    # Sử dụng hàm diagnose cho đường dẫn /diagnose/ (Function-based view)
    path("diagnose/", diagnose, name="diagnose"),
    # Hàm predict xử lý POST request từ form trên trang diagnose
    path('predict/', predict, name='predict'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

