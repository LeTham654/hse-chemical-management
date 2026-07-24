from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import database as db

app = Flask(__name__)
app.secret_key = "HSE_Secret_Key_PNJ"

db.tao_bang()

CAU_TRUC_NHA_MAY = {
    "long_hau": {
        "ten": "Nhà máy PNJ Long Hậu",
        "chuyen": [
            "Chuyền Khắc máy - CNC", "Chuyền Xi mạ", "Bộ phận Phân kim", 
            "Chuyền trang sức Sỉ - 24K", "Bộ phận Cơ điện", "Chuyền Bạc - Giả kim", 
            "Chuyền CZ/ECZ", "Chuyền Trang sức Ý", "Chuyền EF26", 
            "Bộ phận LAB", "Xử lý nước thải", "Kho hóa chất"
        ]
    },
    "go_vap": {
        "ten": "Nhà máy PNJP Gò Vấp",
        "chuyen": ["Phòng Kiểm Định", "Khu Xử Lý Nước Thải"]
    }
}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "123456":
            session['role'] = 'admin'
            return redirect(url_for('khai_bao'))
        elif username == "user" and password == "123456":
            session['role'] = 'user'
            return redirect(url_for('khai_bao'))
        else:
            return render_template("login.html", error="Sai tài khoản hoặc mật khẩu!")
    return render_template("login.html")

@app.route("/khai-bao", methods=["GET", "POST"])
def khai_bao():
    role = session.get('role')
    if not role:
        return redirect(url_for('login'))
    if request.method == "POST":
        session['ho_ten'] = request.form.get("ho_ten")
        if role == 'admin':
            session['bo_phan'] = 'Quản trị viên / HSE'
            db.ghi_log(session['ho_ten'], session['bo_phan'], "Đăng nhập", f"Quản trị viên {session['ho_ten']} đăng nhập vào hệ thống")
        else:
            session['bo_phan'] = request.form.get("bo_phan")
            db.ghi_log(session['ho_ten'], session['bo_phan'], "Đăng nhập", f"Nhân viên {session['ho_ten']} truy cập hệ thống")
        return redirect(url_for('index'))
    return render_template("khai_bao.html", role=role)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
def index():
    thong_ke = db.lay_thong_ke_nha_may()
    bao_cao_lh = []
    for chuyen in CAU_TRUC_NHA_MAY['long_hau']['chuyen']:
        tk = db.thong_ke_bo_phan('long_hau', chuyen)
        bao_cao_lh.append({
            "ten_chuyen": chuyen,
            "so_loai": tk['tong_loai'],
            "tong_so_luong": tk['tong_so_luong']
        })
    bao_cao_gv = []
    for chuyen in CAU_TRUC_NHA_MAY['go_vap']['chuyen']:
        tk = db.thong_ke_bo_phan('go_vap', chuyen)
        bao_cao_gv.append({
            "ten_chuyen": chuyen,
            "so_loai": tk['tong_loai'],
            "tong_so_luong": tk['tong_so_luong']
        })
    return render_template("index.html", tk=thong_ke, bao_cao_lh=bao_cao_lh, bao_cao_gv=bao_cao_gv)

@app.route("/hoa-chat")
def danh_sach():
    tu_khoa = request.args.get('tu_khoa', '')
    if tu_khoa:
        ds = db.tim_kiem_hoa_chat(tu_khoa)
    else:
        ds = db.lay_tat_ca_hoa_chat()
    return render_template("chemicals.html", danh_sach=ds, tu_khoa=tu_khoa)

@app.route("/lich-su")
def lich_su():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    logs = db.lay_lich_su()
    return render_template("lich_su.html", logs=logs)

@app.route("/them-hoa-chat", methods=["POST"])
def them():
    if session.get('role') == 'admin':
        d = request.form
        # Lấy nhãn dán từ HTML gửi lên (1 là Bảng tổng, 0 là Bảng chuyền)
        is_master = int(d.get("is_master", 1))
        db.them_hoa_chat(d, is_master)
        nguoi_thao_tac = session.get('ho_ten', 'Quản trị viên')
        db.ghi_log(nguoi_thao_tac, "Hệ thống", "Thêm Mới", f"Thêm hóa chất: {d['ten_sap']}")
    return redirect(request.referrer or url_for('danh_sach'))

@app.route("/sua/<int:id>")
def sua(id):
    if session.get('role') != 'admin':
        return redirect(url_for('danh_sach'))
    hc = db.lay_mot_hoa_chat(id)
    ref = request.referrer or url_for('danh_sach')
    return render_template("sua.html", hc=hc, referrer=ref)

@app.route("/cap-nhat/<int:id>", methods=["POST"])
def cap_nhat(id):
    if session.get('role') == 'admin':
        d = request.form
        db.cap_nhat_hoa_chat(id, d)
        nguoi_thao_tac = session.get('ho_ten', 'Quản trị viên')
        db.ghi_log(nguoi_thao_tac, "Hệ thống", "Chỉnh sửa", f"Cập nhật hóa chất ID {id}")
    ref = request.form.get('referrer')
    return redirect(ref if ref else url_for('danh_sach'))

@app.route("/xoa/<int:id>")
def xoa(id):
    if session.get('role') == 'admin':
        hc = db.lay_mot_hoa_chat(id)
        db.xoa_hoa_chat(id)
        nguoi_thao_tac = session.get('ho_ten', 'Quản trị viên')
        db.ghi_log(nguoi_thao_tac, "Hệ thống", "Xóa", f"Xóa hóa chất: {hc['ten_sap']}")
    return redirect(request.referrer or url_for('danh_sach'))

@app.route("/nguon-goc/<int:id>/<loai>")
def cap_nhat_nguon(id, loai):
    if session.get('role') == 'admin':
        db.cap_nhat_nguon_goc(id, loai)
        return jsonify({"status": "thanh_cong"})
    return jsonify({"status": "loi"}), 403

@app.route("/nha-may/<int:id>/<loai>")
def cap_nhat_nhamay(id, loai):
    if session.get('role') == 'admin':
        db.cap_nhat_nha_may(id, loai)
        return jsonify({"status": "thanh_cong"})
    return jsonify({"status": "loi"}), 403

@app.route("/msds/<int:id>")
def them_msds(id):
    if session.get('role') == 'admin':
        link = request.args.get('link', '')
        db.cap_nhat_msds(id, link)
        nguoi_thao_tac = session.get('ho_ten', 'Quản trị viên')
        db.ghi_log(nguoi_thao_tac, "Hệ thống", "Cập nhật MSDS", f"Thêm link MSDS cho hóa chất ID {id}")
    return redirect(request.referrer or url_for('danh_sach'))

@app.route("/xem-msds/<int:id>")
def xem_msds(id):
    hc = db.lay_mot_hoa_chat(id)
    nguoi_xem = session.get('ho_ten', 'Khách ẩn danh')
    bo_phan = session.get('bo_phan', 'Chưa rõ')
    db.ghi_log(nguoi_xem, bo_phan, "Truy xuất MSDS", f"Xem MSDS hóa chất: {hc['ten_sap']}")
    return redirect(hc['msds_link'])

@app.route("/cap-nhat-phu-trach", methods=["POST"])
def cap_nhat_phu_trach():
    if session.get('role') == 'admin':
        nha_may = request.form.get("nha_may")
        ten_chuyen = request.form.get("ten_chuyen")
        chuc_danh = request.form.get("chuc_danh")
        ho_ten = request.form.get("ho_ten")
        msnv = request.form.get("msnv")
        db.cap_nhat_nguoi_phu_trach(nha_may, ten_chuyen, chuc_danh, ho_ten, msnv)
        nguoi_thao_tac = session.get('ho_ten', 'Quản trị viên')
        db.ghi_log(nguoi_thao_tac, ten_chuyen, "Cập nhật", f"Cập nhật thông tin người phụ trách: {ho_ten} ({msnv})")
        return redirect(url_for('bo_phan', nha_may_code=nha_may, ten_chuyen=ten_chuyen))
    return redirect(url_for('index'))

@app.route("/so-do")
def so_do_nha_may():
    return render_template("so_do.html", cau_truc=CAU_TRUC_NHA_MAY)

@app.route("/bo-phan/<nha_may_code>/<path:ten_chuyen>")
def bo_phan(nha_may_code, ten_chuyen):
    nha_may_info = CAU_TRUC_NHA_MAY.get(nha_may_code)
    if not nha_may_info:
        return "Không tìm thấy nhà máy!", 404
    ds_hoa_chat = db.lay_hoa_chat_theo_bo_phan(nha_may_code, ten_chuyen)
    thong_ke = db.thong_ke_bo_phan(nha_may_code, ten_chuyen)
    phu_trach = db.lay_nguoi_phu_trach(nha_may_code, ten_chuyen)
    return render_template("bo_phan.html", 
                           nha_may_code=nha_may_code,
                           ten_nha_may=nha_may_info['ten'], 
                           ten_chuyen=ten_chuyen, 
                           danh_sach=ds_hoa_chat, 
                           thong_ke=thong_ke,
                           phu_trach=phu_trach)
# ================= CÁC HÀM XỬ LÝ NGẦM (AJAX) KHÔNG RELOAD TRANG =================
@app.route("/api/xoa/<int:id>", methods=["POST"])
def api_xoa(id):
    if session.get('role') == 'admin':
        hc = db.lay_mot_hoa_chat(id)
        if hc:
            db.xoa_hoa_chat(id)
            nguoi_thao_tac = session.get('ho_ten', 'Quản trị viên')
            db.ghi_log(nguoi_thao_tac, "Hệ thống", "Xóa", f"Xóa hóa chất: {hc['ten_sap']}")
            return jsonify({"status": "thanh_cong"})
    return jsonify({"status": "loi"}), 403

@app.route("/api/chi-tiet/<int:id>")
def api_chi_tiet(id):
    hc = db.lay_mot_hoa_chat(id)
    return jsonify(dict(hc)) if hc else jsonify({"status": "loi"})

@app.route("/api/cap-nhat/<int:id>", methods=["POST"])
def api_cap_nhat(id):
    if session.get('role') == 'admin':
        d = request.json
        hc_cu = dict(db.lay_mot_hoa_chat(id))
        
        # Chỉ cập nhật những nội dung mới vào dữ liệu cũ
        for key in d:
            hc_cu[key] = d[key]
            
        db.cap_nhat_hoa_chat(id, hc_cu)
        nguoi_thao_tac = session.get('ho_ten', 'Quản trị viên')
        db.ghi_log(nguoi_thao_tac, "Hệ thống", "Chỉnh sửa", f"Cập nhật ngầm hóa chất ID {id}")
        return jsonify({"status": "thanh_cong"})
    return jsonify({"status": "loi"}), 403
@app.route("/api/them", methods=["POST"])
def api_them():
    if session.get('role') == 'admin':
        d = request.form
        # Lấy nhãn dán từ HTML gửi lên (1 là Bảng tổng, 0 là Bảng chuyền)
        is_master = int(d.get("is_master", 1))
        
        db.them_hoa_chat(d, is_master)
        
        nguoi_thao_tac = session.get('ho_ten', 'Quản trị viên')
        db.ghi_log(nguoi_thao_tac, "Hệ thống", "Thêm Mới", f"Thêm hóa chất ngầm: {d.get('ten_sap')}")
        
        return jsonify({"status": "thanh_cong"})
    return jsonify({"status": "loi"}), 403
if __name__ == "__main__":
    app.run(debug=True)