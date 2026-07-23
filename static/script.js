// HÀM CẬP NHẬT THỐNG KÊ NGẦM (KHÔNG CẦN TẢI LẠI TRANG)
function capNhatThongKe() {
    let tongTrong = document.querySelectorAll('.chon-trong-nuoc.da-chon').length;
    let tongNgoai = document.querySelectorAll('.chon-ngoai-nuoc.da-chon').length;
    let tongLH = document.querySelectorAll('.chon-long-hau.da-chon').length;
    let tongGV = document.querySelectorAll('.chon-go-vap.da-chon').length;
    
    if(document.getElementById('thongke_trong')) document.getElementById('thongke_trong').innerText = tongTrong;
    if(document.getElementById('thongke_ngoai')) document.getElementById('thongke_ngoai').innerText = tongNgoai;
    if(document.getElementById('thongke_lh')) document.getElementById('thongke_lh').innerText = tongLH;
    if(document.getElementById('thongke_gv')) document.getElementById('thongke_gv').innerText = tongGV;
}

// ================= LOGIC ĐỔI NGUỒN GỐC (MƯỢT 100%) =================
function doiNguonGoc(id, loai) {
    fetch(`/nguon-goc/${id}/${loai}`)
        .then(response => response.json())
        .then(data => { 
            if(data.status === "thanh_cong") {
                // Tắt màu cả 2 ô
                document.getElementById(`nguon_trong_${id}`).classList.remove('da-chon');
                document.getElementById(`nguon_ngoai_${id}`).classList.remove('da-chon');
                // Bật màu ô được chọn
                if (loai === 'trong_nuoc') {
                    document.getElementById(`nguon_trong_${id}`).classList.add('da-chon');
                } else {
                    document.getElementById(`nguon_ngoai_${id}`).classList.add('da-chon');
                }
                capNhatThongKe(); // Cho số dưới Footer nhảy tự động
            } 
        })
        .catch(error => console.error("Lỗi:", error));
}

// ================= LOGIC ĐỔI NHÀ MÁY (MƯỢT 100%) =================
function doiNhaMay(id, loai) {
    fetch(`/nha-may/${id}/${loai}`)
        .then(response => response.json())
        .then(data => { 
            if(data.status === "thanh_cong") {
                // Tắt màu cả 2 ô
                document.getElementById(`nhamay_lh_${id}`).classList.remove('da-chon');
                document.getElementById(`nhamay_gv_${id}`).classList.remove('da-chon');
                // Bật màu ô được chọn
                if (loai === 'long_hau') {
                    document.getElementById(`nhamay_lh_${id}`).classList.add('da-chon');
                } else {
                    document.getElementById(`nhamay_gv_${id}`).classList.add('da-chon');
                }
                capNhatThongKe(); // Cho số dưới Footer nhảy tự động
            } 
        })
        .catch(error => console.error("Lỗi:", error));
}

// ================= XÁC NHẬN XÓA =================
function xacNhanXoa(id) { 
    Swal.fire({
        title: 'Bạn có chắc chắn?',
        text: "Dữ liệu hóa chất này sẽ bị xóa khỏi hệ thống và không thể khôi phục!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444', 
        cancelButtonColor: '#64748b',  
        confirmButtonText: 'Đồng ý xóa',
        cancelButtonText: 'Hủy bỏ',
        borderRadius: '12px'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/xoa/" + id;
        }
    });
}

// ================= SỬA MSDS =================
function suaMSDS(id) {
    Swal.fire({
        title: 'Cập nhật link MSDS',
        input: 'url',
        inputLabel: 'Dán đường link Google Drive hoặc trang PDF online vào đây',
        inputPlaceholder: 'https://...',
        icon: 'info',
        showCancelButton: true,
        confirmButtonText: 'Lưu thay đổi',
        cancelButtonText: 'Hủy',
        confirmButtonColor: '#2563eb',
    }).then((result) => {
        if (result.isConfirmed && result.value) {
            window.location.href = "/msds/" + id + "?link=" + encodeURIComponent(result.value.trim());
        }
    });
}

// ================= NÚT CUỘN LÊN ĐẦU TRANG =================
window.addEventListener('scroll', function() {
    let nutCuon = document.getElementById("nut-cuon-len");
    if (nutCuon) {
        if (window.scrollY > 200) { 
            nutCuon.style.display = "block"; 
        } else { 
            nutCuon.style.display = "none"; 
        }
    }
});

function cuonLenDauTrang() { 
    window.scrollTo({ top: 0, behavior: 'smooth' }); 
}
// ========================================================
// HỆ THỐNG SỬA/XÓA MƯỢT MÀ (KHÔNG RELOAD TRANG)
// ========================================================

// Kỹ thuật tải lại bảng & thống kê ngầm không chớp màn hình
function lamMoiDuLieuNgam() {
    fetch(window.location.href)
    .then(res => res.text())
    .then(html => {
        let parser = new DOMParser();
        let doc = parser.parseFromString(html, 'text/html');
        
        // 1. Cập nhật ngầm Bảng hóa chất
        let bangMoi = doc.querySelector('.khung-bang');
        if (bangMoi && document.querySelector('.khung-bang')) {
            document.querySelector('.khung-bang').innerHTML = bangMoi.innerHTML;
        }
        
        // 2. Cập nhật ngầm các con số Thống kê (5 ô màu trên cùng)
        let thongKeMoi = doc.querySelector('.mini-dashboard');
        if (thongKeMoi && document.querySelector('.mini-dashboard')) {
            document.querySelector('.mini-dashboard').innerHTML = thongKeMoi.innerHTML;
        }
    });
}

// Hàm Xóa Ngầm
function xacNhanXoaAJAX(id) {
    Swal.fire({
        title: 'Xóa hóa chất này?',
        text: "Dữ liệu sẽ bốc hơi vĩnh viễn khỏi hệ thống!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#9ca3af',
        confirmButtonText: 'Xóa ngay',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/api/xoa/' + id, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'thanh_cong') {
                    Swal.fire({ icon: 'success', title: 'Đã xóa!', timer: 1000, showConfirmButton: false });
                    lamMoiDuLieuNgam(); // Tự động làm mới UI
                }
            });
        }
    });
}

// Hàm Sửa Ngầm bằng Popup
function suaHoaChatAJAX(id) {
    // Hiện loading chờ lấy dữ liệu
    Swal.fire({ title: 'Đang tải dữ liệu...', allowOutsideClick: false, didOpen: () => { Swal.showLoading(); }});

    fetch('/api/chi-tiet/' + id)
    .then(res => res.json())
    .then(hc => {
        Swal.fire({
            title: 'Chỉnh sửa Hóa chất',
            width: '700px', // Cho khung rộng ra để dễ nhìn
            html: `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; text-align: left; font-size: 14px;">
                    <div><label style="font-weight:bold; color:#374151;">Code mua</label><input id="e_code" class="swal2-input" style="width:100%; margin: 5px 0;" value="${hc.code_mua || ''}"></div>
                    <div><label style="font-weight:bold; color:#374151;">Tên SAP</label><input id="e_ten" class="swal2-input" style="width:100%; margin: 5px 0;" value="${hc.ten_sap || ''}"></div>
                    <div><label style="font-weight:bold; color:#374151;">Tên thường gọi</label><input id="e_thuong" class="swal2-input" style="width:100%; margin: 5px 0;" value="${hc.ten_thuong_goi || ''}"></div>
                    <div><label style="font-weight:bold; color:#374151;">Số lượng</label><input id="e_sl" type="number" class="swal2-input" style="width:100%; margin: 5px 0;" value="${hc.so_luong || 0}"></div>
                    <div><label style="font-weight:bold; color:#374151;">Số CAS</label><input id="e_cas" class="swal2-input" style="width:100%; margin: 5px 0;" value="${hc.so_cas || ''}"></div>
                    <div><label style="font-weight:bold; color:#374151;">Công thức</label><input id="e_ct" class="swal2-input" style="width:100%; margin: 5px 0;" value="${hc.cong_thuc || ''}"></div>
                    <div><label style="font-weight:bold; color:#374151;">Dạng tồn tại</label><input id="e_dang" class="swal2-input" style="width:100%; margin: 5px 0;" placeholder="Rắn/Lỏng/Khí..." value="${hc.dang_ton_tai || ''}"></div>
                    <div><label style="font-weight:bold; color:#374151;">Xuất xứ</label><input id="e_xx" class="swal2-input" style="width:100%; margin: 5px 0;" value="${hc.xuat_xu || ''}"></div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Lưu thay đổi',
            cancelButtonText: 'Hủy',
            confirmButtonColor: '#10b981',
            preConfirm: () => {
                return {
                    code_mua: document.getElementById('e_code').value,
                    ten_sap: document.getElementById('e_ten').value,
                    ten_thuong_goi: document.getElementById('e_thuong').value,
                    so_luong: document.getElementById('e_sl').value,
                    so_cas: document.getElementById('e_cas').value,
                    cong_thuc: document.getElementById('e_ct').value,
                    dang_ton_tai: document.getElementById('e_dang').value,
                    xuat_xu: document.getElementById('e_xx').value
                }
            }
        }).then((result) => {
            if (result.isConfirmed) {
                fetch('/api/cap-nhat/' + id, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(result.value)
                })
                .then(res => res.json())
                .then(data => {
                    if(data.status === 'thanh_cong') {
                        Swal.fire({ icon: 'success', title: 'Đã lưu thành công!', timer: 1200, showConfirmButton: false });
                        lamMoiDuLieuNgam(); // Tự động làm mới UI
                    }
                });
            }
        });
    });
}
// Bắt sự kiện Thêm mới hóa chất không reload trang
document.addEventListener('DOMContentLoaded', function() {
    let formThem = document.getElementById('form-them-ngam');
    if (formThem) {
        formThem.addEventListener('submit', function(e) {
            e.preventDefault(); // Tuyệt đối không cho trình duyệt tải lại trang
            
            // Hiện vòng xoay chờ
            Swal.fire({ title: 'Đang lưu hóa chất...', allowOutsideClick: false, didOpen: () => { Swal.showLoading(); }});

            // Gom toàn bộ dữ liệu người dùng đã gõ trong form
            let formData = new FormData(formThem);
            
            fetch('/api/them', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'thanh_cong') {
                    Swal.fire({ icon: 'success', title: 'Đã thêm thành công!', timer: 1200, showConfirmButton: false });
                    formThem.reset(); // Dọn dẹp trắng form để nhập tiếp
                    lamMoiDuLieuNgam(); // Gọi hàm làm mới bảng & thống kê
                } else {
                    Swal.fire({ icon: 'error', title: 'Lỗi', text: 'Bạn không có quyền hoặc phiên đăng nhập đã hết hạn.' });
                }
            })
            .catch(error => {
                Swal.fire({ icon: 'error', title: 'Lỗi máy chủ', text: 'Vui lòng kiểm tra lại kết nối!' });
            });
        });
    }
});
