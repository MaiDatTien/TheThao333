from django import forms
from .models import SanBong, DatSan, SanPham
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

# Form Đăng nhập
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}))

# --- FORM ĐĂNG KÝ (QUAN TRỌNG) ---
class SignUpForm(UserCreationForm):
    # Thêm các trường nhập liệu bổ sung
    first_name = forms.CharField(label="Tên", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Nam'}))
    last_name = forms.CharField(label="Họ đệm", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Nguyễn Văn'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}))

    class Meta:
        model = User
        # Các trường sẽ hiện ra (Lưu ý: password đã có sẵn trong UserCreationForm)
        fields = ('username', 'last_name', 'first_name', 'email')
        help_texts = {
            'username': None, # Ẩn dòng hướng dẫn rườm rà của Django
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập (viết liền)'}),
        }

# ... (Giữ nguyên các Form SanBong, DatSan, SanPham bên dưới) ...
class SanBongForm(forms.ModelForm):
    class Meta:
        model = SanBong
        fields = ['ten_san', 'dia_chi', 'gia_tien', 'vi_do', 'kinh_do', 'hinh_anh', 'danh_gia', 'khoang_cach']
        widgets = {
            'ten_san': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_chi': forms.TextInput(attrs={'class': 'form-control'}),
            'gia_tien': forms.NumberInput(attrs={'class': 'form-control'}),
            'vi_do': forms.TextInput(attrs={'class': 'form-control', 'id': 'txtLat'}),
            'kinh_do': forms.TextInput(attrs={'class': 'form-control', 'id': 'txtLng'}),
            'hinh_anh': forms.FileInput(attrs={'class': 'form-control'}),
            'danh_gia': forms.NumberInput(attrs={'class': 'form-control'}),
            'khoang_cach': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SanPhamForm(forms.ModelForm):
    class Meta:
        model = SanPham
        fields = ['ten_sp', 'loai', 'gia', 'hinh_anh']
        widgets = {
            'ten_sp': forms.TextInput(attrs={'class': 'form-control'}),
            'loai': forms.Select(attrs={'class': 'form-select'}),
            'gia': forms.NumberInput(attrs={'class': 'form-control'}),
            'hinh_anh': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DatSanForm(forms.ModelForm):
    dich_vu_kem = forms.ModelMultipleChoiceField(
        queryset=SanPham.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Dịch vụ thêm"
    )
    class Meta:
        model = DatSan
        fields = ['ho_ten', 'sdt', 'ngay_dat', 'gio_bat_dau', 'thoi_luong', 'dich_vu_kem']
        widgets = {
            'ho_ten': forms.TextInput(attrs={'class': 'form-control'}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'ngay_dat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gio_bat_dau': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'thoi_luong': forms.NumberInput(attrs={'class': 'form-control', 'step': 30}),
        }