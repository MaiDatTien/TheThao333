from django.db import models
from django.contrib.auth.models import User

# 1. Bảng Sân Bóng
class SanBong(models.Model):
    ten_san = models.CharField(max_length=100, verbose_name="Tên sân")
    dia_chi = models.CharField(max_length=200, verbose_name="Địa chỉ")
    gia_tien = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá thuê (VNĐ/h)")
    vi_do = models.FloatField(verbose_name="Vĩ độ")
    kinh_do = models.FloatField(verbose_name="Kinh độ")
    hinh_anh = models.ImageField(upload_to='san_bong/', blank=True, null=True, verbose_name="Hình ảnh sân")
    
    # Các trường bổ sung cho giao diện đẹp
    danh_gia = models.FloatField(default=5.0, verbose_name="Điểm đánh giá")
    so_luot_danh_gia = models.IntegerField(default=0, verbose_name="Số lượt review")
    khoang_cach = models.FloatField(default=1.5, verbose_name="Khoảng cách demo (km)") 
    
    # Quản lý người yêu thích sân
    nguoi_yeu_thich = models.ManyToManyField(User, related_name='san_yeu_thich', blank=True)

    def __str__(self):
        return self.ten_san

# 2. Bảng Sản Phẩm / Dịch Vụ
class SanPham(models.Model):
    LOAI_CHOICES = [('THUE', 'Thuê (Giày/Vợt/Áo)'), ('DO_AN', 'Đồ Ăn / Nước Uống')]
    ten_sp = models.CharField(max_length=100, verbose_name="Tên sản phẩm")
    loai = models.CharField(max_length=20, choices=LOAI_CHOICES, default='DO_AN', verbose_name="Loại")
    gia = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá tiền")
    hinh_anh = models.ImageField(upload_to='san_pham/', blank=True, null=True, verbose_name="Hình ảnh")
    
    def __str__(self):
        return f"{self.ten_sp} ({self.gia:,.0f}đ)"

# 3. Bảng Đặt Sân
class DatSan(models.Model):
    TRANG_THAI_CHOICES = [('CHO_DUYET', 'Chờ Duyệt'), ('DA_DUYET', 'Đã Duyệt (Đã Cọc)'), ('TU_CHOI', 'Hủy Bỏ')]
    khach_hang = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Khách hàng", null=True, blank=True)
    san = models.ForeignKey(SanBong, on_delete=models.CASCADE, verbose_name="Sân bóng")
    ho_ten = models.CharField(max_length=100, verbose_name="Họ tên")
    sdt = models.CharField(max_length=15, verbose_name="SĐT")
    ngay_dat = models.DateField(verbose_name="Ngày đặt")
    gio_bat_dau = models.TimeField(verbose_name="Giờ bắt đầu")
    thoi_luong = models.IntegerField(default=60, verbose_name="Thời lượng (phút)")
    dich_vu_kem = models.ManyToManyField(SanPham, blank=True, verbose_name="Dịch vụ")
    tong_tien = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    tien_coc = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='CHO_DUYET')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ho_ten} đặt {self.san.ten_san}"