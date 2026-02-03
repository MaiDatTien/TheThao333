from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from .models import SanBong, DatSan, SanPham
from .forms import SanBongForm, DatSanForm, LoginForm, SignUpForm, SanPhamForm
import folium

# --- 1. AUTHENTICATION (Đăng nhập - Đăng ký - Đăng xuất) ---

def dang_nhap(request):
    """Xử lý đăng nhập"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Nếu có tham số 'next' trên URL thì chuyển hướng đến đó, ngược lại về home
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
            login(request, user) # Đăng ký xong tự động đăng nhập luôn
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'quanlysan/signup.html', {'form': form})

def dang_xuat(request):
    """Đăng xuất"""
    logout(request)
    return redirect('home')

def is_admin(user):
    """Kiểm tra quyền Admin"""
    return user.is_authenticated and user.is_staff

# --- 2. TRANG CHỦ & CHI TIẾT SÂN ---

def trang_chu(request):
    """Hiển thị danh sách sân và tìm kiếm"""
    query = request.GET.get('q', '')
    if query:
        # Tìm theo tên sân HOẶC địa chỉ
        danh_sach_san = SanBong.objects.filter(Q(ten_san__icontains=query) | Q(dia_chi__icontains=query))
    else:
        danh_sach_san = SanBong.objects.all()
    
    return render(request, 'quanlysan/index.html', {
        'cac_san': danh_sach_san, 
        'query': query
    })

def chi_tiet_san(request, pk):
    """Trang chi tiết: Hiển thị bản đồ, tính khoảng cách"""
    san = get_object_or_404(SanBong, pk=pk)
    # Không cần tạo bản đồ Folium ở đây nữa vì ta đã dùng Leaflet JS ở template
    return render(request, 'quanlysan/chi_tiet_san.html', {'san': san})

# --- 3. CÁC TRANG PHỤ (Bản đồ lớn, Lịch sử, Hồ sơ) ---

def ban_do_lon(request):
    """Bản đồ toàn màn hình hiển thị tất cả các sân"""
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
    """Xem lịch sử các đơn đã đặt"""
    ds_don = DatSan.objects.filter(khach_hang=request.user).order_by('-created_at')
    return render(request, 'quanlysan/lich_su.html', {'ds_don': ds_don})

@login_required(login_url='login')
def ho_so_ca_nhan(request):
    """Trang thông tin tài khoản"""
    return render(request, 'quanlysan/ho_so.html')

# --- 4. CHỨC NĂNG (Thả tim, Đặt sân) ---

@login_required(login_url='login')
def toggle_yeu_thich(request, pk):
    """Xử lý nút Thả tim / Bỏ tim"""
    san = get_object_or_404(SanBong, pk=pk)
    if san.nguoi_yeu_thich.filter(id=request.user.id).exists():
        san.nguoi_yeu_thich.remove(request.user)
    else:
        san.nguoi_yeu_thich.add(request.user)
    # Load lại đúng trang vừa đứng
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def dat_san(request, pk):
    """Form đặt sân"""
    san = get_object_or_404(SanBong, pk=pk)
    
    if request.method == 'POST':
        form = DatSanForm(request.POST)
        if form.is_valid():
            don = form.save(commit=False)
            don.san = san
            don.khach_hang = request.user
            
            # Tính tiền sân: (Giá / 60) * Số phút
            don.tong_tien = (san.gia_tien / 60) * don.thoi_luong
            don.save() # Lưu lần 1 để có ID
            
            # Lưu dịch vụ đi kèm (Many-to-Many)
            form.save_m2m()
            
            # Cộng thêm tiền dịch vụ
            tien_dich_vu = sum([sp.gia for sp in don.dich_vu_kem.all()])
            don.tong_tien += tien_dich_vu
            
            # Tính cọc 30%
            don.tien_coc = don.tong_tien * 0.3
            don.save() # Lưu lần 2
            
            return render(request, 'quanlysan/thanh_cong.html', {'don': don})
    else:
        # Tự điền tên người dùng vào form
        initial_data = {
            'ho_ten': f"{request.user.last_name} {request.user.first_name}", 
            'sdt': ''
        }
        form = DatSanForm(initial=initial_data)
        
    return render(request, 'quanlysan/dat_san.html', {'form': form, 'san': san})

# --- 5. ADMIN TOOLS (Thêm, Sửa, Xóa) ---

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