from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from decimal import Decimal
from datetime import datetime, timedelta, date
from .models import DiaDiem, SanBong, DatSan, SanPham
from .forms import DiaDiemForm, SanBongForm, DatSanForm, LoginForm, SignUpForm, SanPhamForm
import folium

def trang_chu(request):
    query = request.GET.get('q', '')
    if query:
        cac_dia_diem = DiaDiem.objects.filter(
            Q(ten_dia_diem__icontains=query) | 
            Q(dia_chi__icontains=query) |
            Q(ds_san_con__ten_san__icontains=query)
        ).distinct()
    else:
        cac_dia_diem = DiaDiem.objects.all()
        
    return render(request, 'quanlysan/index.html', {
        'cac_dia_diem': cac_dia_diem, 
        'query': query
    })

def chi_tiet_dia_diem(request, pk):
    dia_diem = get_object_or_404(DiaDiem, pk=pk)
    ds_san_con = dia_diem.ds_san_con.all()
    return render(request, 'quanlysan/chi_tiet_dia_diem.html', {'dia_diem': dia_diem, 'ds_san_con': ds_san_con})

@login_required
def dat_san(request, pk):
    san_con = get_object_or_404(SanBong, pk=pk)
    error_msg = None
    
    if request.method == 'POST':
        form = DatSanForm(request.POST)
        if form.is_valid():
            ngay = form.cleaned_data['ngay_dat']
            gio_bd = form.cleaned_data['gio_bat_dau']
            phut_thue = form.cleaned_data['thoi_luong']
            
            dummy_date = datetime.combine(date.today(), gio_bd)
            gio_kt = (dummy_date + timedelta(minutes=phut_thue)).time()
            
            trung_lich = DatSan.objects.filter(
                san=san_con,
                ngay_dat=ngay,
                trang_thai__in=['CHO_DUYET', 'DA_DUYET']
            ).filter(
                Q(gio_bat_dau__lt=gio_kt) & Q(gio_bat_dau__gte=gio_bd) | 
                Q(gio_bat_dau__lte=gio_bd, thoi_luong__gt=0) 
            )
            
            is_conflict = False
            for don in trung_lich:
                don_start = datetime.combine(ngay, don.gio_bat_dau)
                don_end = don_start + timedelta(minutes=don.thoi_luong)
                req_start = datetime.combine(ngay, gio_bd)
                req_end = req_start + timedelta(minutes=phut_thue)
                if req_start < don_end and req_end > don_start:
                    is_conflict = True
                    break
            
            if is_conflict:
                error_msg = f"Giờ {gio_bd} ngày {ngay} đã có người đặt! Vui lòng chọn giờ khác."
            else:
                don = form.save(commit=False)
                don.san = san_con
                don.khach_hang = request.user
                
                don.tong_tien = (san_con.gia_tien / Decimal(60)) * Decimal(don.thoi_luong)
                don.save()
                form.save_m2m()
                
                don.tong_tien += sum([sp.gia for sp in don.dich_vu_kem.all()])
                don.tien_coc = don.tong_tien * Decimal('0.3')
                
                don.save()
                return render(request, 'quanlysan/thanh_cong.html', {'don': don})
    else:
        initial_data = {'ho_ten': f"{request.user.last_name} {request.user.first_name}", 'sdt': ''}
        form = DatSanForm(initial=initial_data)
        
    return render(request, 'quanlysan/dat_san.html', {'form': form, 'san': san_con, 'error_msg': error_msg})

@user_passes_test(lambda u: u.is_staff)
def them_dia_diem(request):
    if request.method == 'POST':
        form = DiaDiemForm(request.POST, request.FILES)
        if form.is_valid(): form.save(); return redirect('home')
    else: form = DiaDiemForm()
    return render(request, 'quanlysan/them_dia_diem.html', {'form': form, 'title': 'Thêm Cụm Sân'})

@user_passes_test(lambda u: u.is_staff)
def them_san_con(request):
    if request.method == 'POST':
        form = SanBongForm(request.POST)
        if form.is_valid(): form.save(); return redirect('home')
    else: form = SanBongForm()
    return render(request, 'quanlysan/them_dia_diem.html', {'form': form, 'title': 'Thêm Sân Con'})

@user_passes_test(lambda u: u.is_staff)
def ds_san_pham(request):
    san_pham = SanPham.objects.all()
    if request.method == 'POST':
        form = SanPhamForm(request.POST, request.FILES)
        if form.is_valid(): form.save(); return redirect('ds_san_pham')
    else: form = SanPhamForm()
    return render(request, 'quanlysan/ds_san_pham.html', {'san_pham': san_pham, 'form': form})

@user_passes_test(lambda u: u.is_staff)
def xoa_san_pham(request, pk):
    get_object_or_404(SanPham, pk=pk).delete()
    return redirect('ds_san_pham')

def dang_nhap(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid(): login(request, form.get_user()); return redirect('home')
    else: form = LoginForm()
    return render(request, 'quanlysan/login.html', {'form': form})

def dang_ky(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid(): user = form.save(); login(request, user); return redirect('home')
    else: form = SignUpForm()
    return render(request, 'quanlysan/signup.html', {'form': form})

def dang_xuat(request): logout(request); return redirect('home')

@login_required
def lich_su_dat(request):
    ds = DatSan.objects.filter(khach_hang=request.user).order_by('-created_at')
    return render(request, 'quanlysan/lich_su.html', {'ds_don': ds})

@login_required
def ho_so_ca_nhan(request): return render(request, 'quanlysan/ho_so.html')

@user_passes_test(lambda u: u.is_staff)
def quan_ly_thanh_vien(request):
    users = User.objects.filter(is_staff=False)
    return render(request, 'quanlysan/quan_ly_thanh_vien.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def xoa_thanh_vien(request, pk):
    u = get_object_or_404(User, pk=pk)
    if not u.is_staff: u.delete()
    return redirect('quan_ly_thanh_vien')

@user_passes_test(lambda u: u.is_staff)
def quan_ly_don(request): return render(request, 'quanlysan/quan_ly_don.html', {'ds_don': DatSan.objects.all().order_by('-created_at')})

@user_passes_test(lambda u: u.is_staff)
def duyet_don(request, pk, trang_thai):
    d = get_object_or_404(DatSan, pk=pk); d.trang_thai = trang_thai; d.save(); return redirect('quan_ly_don')

def ban_do_lon(request):
    cac_dia_diem = DiaDiem.objects.all()
    ban_do = folium.Map(location=[10.8231, 106.6297], zoom_start=12)
    for dd in cac_dia_diem:
        html = f"<b>{dd.ten_dia_diem}</b><br><a href='/dia-diem/{dd.id}/'>Xem chi tiết</a>"
        folium.Marker([dd.vi_do, dd.kinh_do], popup=html).add_to(ban_do)
    return render(request, 'quanlysan/ban_do.html', {'ban_do': ban_do._repr_html_()})