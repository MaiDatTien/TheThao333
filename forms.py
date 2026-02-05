from django import forms
from .models import DiaDiem, SanBong, DatSan, SanPham
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class DiaDiemForm(forms.ModelForm):
    class Meta:
        model = DiaDiem
        fields = '__all__'
        widgets = {
            'ten_dia_diem': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_chi': forms.TextInput(attrs={'class': 'form-control'}),
            'vi_do': forms.TextInput(attrs={'class': 'form-control', 'id': 'txtLat', 'readonly': 'readonly'}),
            'kinh_do': forms.TextInput(attrs={'class': 'form-control', 'id': 'txtLng', 'readonly': 'readonly'}),
            'hinh_anh': forms.FileInput(attrs={'class': 'form-control'}),
            'mota': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SanBongForm(forms.ModelForm):
    class Meta:
        model = SanBong
        fields = '__all__'
        widgets = {
            'dia_diem': forms.Select(attrs={'class': 'form-select'}),
            'ten_san': forms.TextInput(attrs={'class': 'form-control'}),
            'loai_san': forms.Select(attrs={'class': 'form-select'}),
            'gia_tien': forms.NumberInput(attrs={'class': 'form-control'}),
            'vi_do': forms.TextInput(attrs={'class': 'form-control', 'id': 'txtLat', 'readonly': 'readonly'}),
            'kinh_do': forms.TextInput(attrs={'class': 'form-control', 'id': 'txtLng', 'readonly': 'readonly'}),
        }

class SanPhamForm(forms.ModelForm):
    class Meta:
        model = SanPham
        fields = '__all__'
        widgets = {
            'ten_sp': forms.TextInput(attrs={'class': 'form-control'}),
            'gia': forms.NumberInput(attrs={'class': 'form-control'}),
            'hinh_anh': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DatSanForm(forms.ModelForm):
    dich_vu_kem = forms.ModelMultipleChoiceField(
        queryset=SanPham.objects.all(), 
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}), 
        required=False,
        label="Dịch vụ kèm"
    )
    class Meta:
        model = DatSan
        fields = ['ho_ten', 'sdt', 'ngay_dat', 'gio_bat_dau', 'thoi_luong', 'dich_vu_kem']
        labels = {
            'ho_ten': 'Họ tên',
            'sdt': 'Số điện thoại',
            'ngay_dat': 'Ngày đá',
            'gio_bat_dau': 'Giờ bắt đầu',
            'thoi_luong': 'Thời lượng (phút)',
        }
        widgets = {
            'ho_ten': forms.TextInput(attrs={'class': 'form-control'}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'ngay_dat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gio_bat_dau': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'thoi_luong': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Tên", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Họ", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'email')