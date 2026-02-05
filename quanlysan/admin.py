from django.contrib import admin
from .models import SanBong  # Import model của bạn

# Đăng ký model để nó hiện trong trang Admin
admin.site.register(SanBong)