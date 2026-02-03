from django.contrib import admin
from django.urls import path, include

# --- THÊM 2 DÒNG IMPORT NÀY ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Đường dẫn vào trang quản trị (http://127.0.0.1:8000/admin/)
    path('admin/', admin.site.urls),

    # Đường dẫn trỏ về app quanlysan (Trang chủ)
    path('', include('quanlysan.urls')),
]

# --- QUAN TRỌNG: CẤU HÌNH ĐỂ HIỂN THỊ ẢNH UPLOAD ---
# (Chỉ chạy khi DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)