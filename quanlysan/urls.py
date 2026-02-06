from django.urls import path
from . import views

urlpatterns = [
    path('', views.trang_chu, name='home'),
    path('dia-diem/<int:pk>/', views.chi_tiet_dia_diem, name='chi_tiet_dia_diem'),
    path('dat-san/<int:pk>/', views.dat_san, name='dat_san'),
    path('them-dia-diem/', views.them_dia_diem, name='them_dia_diem'),
    path('them-san-con/', views.them_san_con, name='them_san_con'),
    path('san-pham/', views.ds_san_pham, name='ds_san_pham'),
    path('san-pham/xoa/<int:pk>/', views.xoa_san_pham, name='xoa_san_pham'),
    path('dang-nhap/', views.dang_nhap, name='login'),
    path('dang-ky/', views.dang_ky, name='signup'),
    path('dang-xuat/', views.dang_xuat, name='logout'),
    path('lich-su/', views.lich_su_dat, name='lich_su_dat'),
    path('ho-so/', views.ho_so_ca_nhan, name='ho_so'),
    path('quan-ly-thanh-vien/', views.quan_ly_thanh_vien, name='quan_ly_thanh_vien'),
    path('xoa-thanh-vien/<int:pk>/', views.xoa_thanh_vien, name='xoa_thanh_vien'),
    path('quan-ly-don/', views.quan_ly_don, name='quan_ly_don'),
    path('duyet-don/<int:pk>/<str:trang_thai>/', views.duyet_don, name='duyet_don'),
    path('ban-do/', views.ban_do_lon, name='ban_do_lon'),
]