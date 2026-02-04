from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from .models import SanBong, DatSan, SanPham
from .forms import SanBongForm, DatSanForm, LoginForm, SignUpForm, SanPhamForm
import folium
from decimal import Decimal # <--- MỚI THÊM: Để xử lý tính toán tiền chính xác

# --- 1. AUTHENTICATION (Đăng nhập - Đăng ký - Đăng xuất) ---

def dang_nhap(request):
    """Xử lý đăng nhập"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'quanlysan/login.html', {'form': form})

def dang_ky(request):
    """Xử lý đăng ký thành viên mới"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'quanlysan/signup.html', {'form': form})

def dang_xuat(request):
    logout(request)
    return redirect('home')

def is_admin(user):
    return user.is_authenticated and user.is_staff

# --- 2. TRANG CHỦ & CHI TIẾT SÂN ---

def trang_chu(request):
    """Hiển thị danh sách sân và tìm kiếm"""
    query = request.GET.get('q', '')
    if query:
        danh_sach_san = SanBong.objects.filter(Q(ten_san__icontains=query) | Q(dia_chi__icontains=query))
    else:
        danh_sach_san = SanBong.objects.all()
    
    return render(request, 'quanlysan/index.html', {
        'cac_san': danh_sach_san, 
        'query': query
    })

def chi_tiet_san(request, pk):
    """Trang chi tiết"""
    san = get_object_or_404(SanBong, pk=pk)
    return render(request, 'quanlysan/chi_tiet_san.html', {'san': san})

# --- 3. CÁC TRANG PHỤ ---

def ban_do_lon(request):
    cac_san = SanBong.objects.all()
    ban_do = folium.Map(location=[10.8231, 106.6297], zoom_start=12)
    
    for san in cac_san:
        html = f"<b>{san.ten_san}</b><br><a href='/chi-tiet/{san.id}/' target='_blank'>Xem chi tiết</a>"
        folium.Marker(
            [san.vi_do, san.kinh_do], 
            popup=html, 
            tooltip=san.ten_san,
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(ban_do)
        
    return render(request, 'quanlysan/ban_do.html', {'ban_do': ban_do._repr_html_()})

@login_required(login_url='login')
def lich_su_dat(request):
    ds_don = DatSan.objects.filter(khach_hang=request.user).order_by('-created_at')
    return render(request, 'quanlysan/lich_su.html', {'ds_don': ds_don})

@login_required(login_url='login')
def ho_so_ca_nhan(request):
    return render(request, 'quanlysan/ho_so.html')

# --- 4. CHỨC NĂNG (Thả tim, Đặt sân) ---

@login_required(login_url='login')
def toggle_yeu_thich(request, pk):
    san = get_object_or_404(SanBong, pk=pk)
    if san.nguoi_yeu_thich.filter(id=request.user.id).exists():
        san.nguoi_yeu_thich.remove(request.user)
    else:
        san.nguoi_yeu_thich.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def dat_san(request, pk):
    san = get_object_or_404(SanBong, pk=pk)
    
    if request.method == 'POST':
        form = DatSanForm(request.POST)
        if form.is_valid():
            don = form.save(commit=False)
            don.san = san
            don.khach_hang = request.user
            
            # Tính tiền sân: (Giá / 60) * Số phút
            # Sử dụng Decimal cho 60 để đảm bảo tính chính xác
            don.tong_tien = (san.gia_tien / Decimal(60)) * Decimal(don.thoi_luong)
            don.save()
            
            # Lưu dịch vụ
            form.save_m2m()
            
            # Cộng tiền dịch vụ
            tien_dich_vu = sum([sp.gia for sp in don.dich_vu_kem.all()])
            don.tong_tien += tien_dich_vu
            
            # --- KHẮC PHỤC LỖI TẠI ĐÂY ---
            # Thay vì nhân với 0.3 (float), ta nhân với Decimal('0.3')
            don.tien_coc = don.tong_tien * Decimal('0.3')
            
            don.save()
            return render(request, 'quanlysan/thanh_cong.html', {'don': don})
    else:
        initial_data = {
            'ho_ten': f"{request.user.last_name} {request.user.first_name}", 
            'sdt': ''
        }
        form = DatSanForm(initial=initial_data)
        
    return render(request, 'quanlysan/dat_san.html', {'form': form, 'san': san})

# --- 5. ADMIN TOOLS ---

@user_passes_test(is_admin)
def them_moi_san(request):
    if request.method == 'POST':
        form = SanBongForm(request.POST, request.FILES)
        if form.is_valid(): form.save(); return redirect('home')
    else: form = SanBongForm()
    return render(request, 'quanlysan/them_san.html', {'form': form})

@user_passes_test(is_admin)
def sua_san(request, pk):
    san = get_object_or_404(SanBong, pk=pk)
    if request.method == 'POST':
        form = SanBongForm(request.POST, request.FILES, instance=san)
        if form.is_valid(): form.save(); return redirect('home')
    else: form = SanBongForm(instance=san)
    return render(request, 'quanlysan/sua_san.html', {'form': form, 'san': san})

@user_passes_test(is_admin)
def xoa_san(request, pk):
    get_object_or_404(SanBong, pk=pk).delete()
    return redirect('home')

@user_passes_test(is_admin)
def ds_san_pham(request):
    san_pham = SanPham.objects.all()
    if request.method == 'POST':
        form = SanPhamForm(request.POST, request.FILES)
        if form.is_valid(): form.save(); return redirect('ds_san_pham')
    else: form = SanPhamForm()
    return render(request, 'quanlysan/ds_san_pham.html', {'san_pham': san_pham, 'form': form})

@user_passes_test(is_admin)
def xoa_san_pham(request, pk):
    get_object_or_404(SanPham, pk=pk).delete()
    return redirect('ds_san_pham')

@user_passes_test(is_admin)
def quan_ly_don(request):
    ds_don = DatSan.objects.all().order_by('-created_at')
    return render(request, 'quanlysan/quan_ly_don.html', {'ds_don': ds_don})

@user_passes_test(is_admin)
def duyet_don(request, pk, trang_thai):
    don = get_object_or_404(DatSan, pk=pk)
    don.trang_thai = trang_thai
    don.save()
    return redirect('quan_ly_don')