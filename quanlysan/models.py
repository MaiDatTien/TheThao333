from django.db import models
from django.contrib.auth.models import User

class DiaDiem(models.Model):
    ten_dia_diem = models.CharField(max_length=100)
    dia_chi = models.CharField(max_length=200)
    vi_do = models.FloatField()
    kinh_do = models.FloatField()
    hinh_anh = models.ImageField(upload_to='dia_diem/', blank=True, null=True)
    mota = models.TextField(blank=True)

    def __str__(self): return self.ten_dia_diem

class SanBong(models.Model):
    LOAI_SAN = [('5', 'Sân 5'), ('7', 'Sân 7'), ('11', 'Sân 11')]
    dia_diem = models.ForeignKey(DiaDiem, on_delete=models.CASCADE, related_name='ds_san_con')
    ten_san = models.CharField(max_length=50)
    loai_san = models.CharField(max_length=10, choices=LOAI_SAN, default='5')
    gia_tien = models.DecimalField(max_digits=10, decimal_places=0)
    vi_do = models.FloatField()
    kinh_do = models.FloatField()
    
    def __str__(self): return f"{self.ten_san} - {self.dia_diem.ten_dia_diem}"

class SanPham(models.Model):
    ten_sp = models.CharField(max_length=100)
    gia = models.DecimalField(max_digits=10, decimal_places=0)
    hinh_anh = models.ImageField(upload_to='san_pham/', blank=True, null=True)
    

    def __str__(self): 
        return f"{self.ten_sp} ({self.gia:,.0f}đ)"

class DatSan(models.Model):
    TRANG_THAI = [('CHO_DUYET', 'Chờ Duyệt'), ('DA_DUYET', 'Đã Duyệt'), ('TU_CHOI', 'Hủy')]
    khach_hang = models.ForeignKey(User, on_delete=models.CASCADE)
    san = models.ForeignKey(SanBong, on_delete=models.CASCADE)
    ho_ten = models.CharField(max_length=100)
    sdt = models.CharField(max_length=15)
    ngay_dat = models.DateField()
    gio_bat_dau = models.TimeField()
    thoi_luong = models.IntegerField(default=60)
    dich_vu_kem = models.ManyToManyField(SanPham, blank=True)
    tong_tien = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    tien_coc = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI, default='CHO_DUYET')
    created_at = models.DateTimeField(auto_now_add=True)