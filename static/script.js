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
        inputLabel: 'Dán đường link Google Drive hoặc trang PDF vào đây',
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