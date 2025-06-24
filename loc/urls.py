from django.urls import path
from . import views

urlpatterns = [
    path("", views.verify_page, name="verify"),
    path("save-ip/", views.save_ip, name="save-ip"),
    path("save-gps/", views.save_gps, name="save-gps"),
    path("send-otp/", views.send_otp, name="send-otp"),
    path("verify-otp/", views.verify_otp, name="verify-otp"),
]
