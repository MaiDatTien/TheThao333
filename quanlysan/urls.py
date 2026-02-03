from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ
    path('', views.trang_chu, name='home'),
    
    # --- MỚI: TRANG CHI TIẾT SÂN ---
    path('chi-tiet/<int:pk>/', views.chi_tiet_san, name='chi_tiet_san'),

    # Auth (Đăng nhập/Đăng ký/Đăng xuất)
    path('dang-nhap/', views.dang_nhap, name='login'),
    path('dang-ky/', views.dang_ky, name='signup'), 
    path('dang-xuat/', views.dang_xuat, name='logout'),

    # Các trang chức năng phụ
    path('ban-do/', views.ban_do_lon, name='ban_do_lon'),
    path('lich-su/', views.lich_su_dat, name='lich_su_dat'),
    path('ho-so/', views.ho_so_ca_nhan, name='ho_so'),
    path('yeu-thich/<int:pk>/', views.toggle_yeu_thich, name='toggle_yeu_thich'),
    path('dat-san/<int:pk>/', views.dat_san, name='dat_san'),

    # Admin Management
    path('them-moi/', views.them_moi_san, name='them_moi'),
    path('sua/<int:pk>/', views.sua_san, name='sua_san'),
    path('xoa/<int:pk>/', views.xoa_san, name='xoa_san'),
    path('san-pham/', views.ds_san_pham, name='ds_san_pham'),
    path('san-pham/xoa/<int:pk>/', views.xoa_san_pham, name='xoa_san_pham'),
    path('quan-ly-don/', views.quan_ly_don, name='quan_ly_don'),
    path('duyet-don/<int:pk>/<str:trang_thai>/', views.duyet_don, name='duyet_don'),
]