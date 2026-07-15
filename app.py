from flask import Flask, render_template, request, redirect, jsonify, session, make_response
import database
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = "khoa_bao_mat_hse_cua_tham_2026" 

database.tao_bang()

def lay_du_lieu_form():
    return {
        "code_mua": request.form.get("code_mua", ""),
        "ten_sap": request.form.get("ten_sap", ""),
        "ten_thuong_goi": request.form.get("ten_thuong_goi", ""),
        "nguon_goc": request.form.get("nguon_goc", ""),
        "nha_may": request.form.get("nha_may", ""),
        "so_cas": request.form.get("so_cas", ""),
        "cong_thuc": request.form.get("cong_thuc", ""),
        "khu_vuc_su_dung": request.form.get("khu_vuc_su_dung", ""),
        "dang_ton_tai": request.form.get("dang_ton_tai", ""),
        "xuat_xu": request.form.get("xuat_xu", ""),
        "so_luong": request.form.get("so_luong", 0),
    }

# ================= ĐĂNG NHẬP VÀ KHAI BÁO =================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":
            session["temp_role"] = "admin"
            return redirect("/khai-bao")
        elif username == "user" and password == "user":
            session["temp_role"] = "user"
            return redirect("/khai-bao")
        else:
            error = "Tài khoản hoặc mật khẩu không chính xác!"
    return render_template("login.html", error=error)

@app.route("/khai-bao", methods=["GET", "POST"])
def khai_bao():
    if "temp_role" not in session:
        return redirect("/login")
        
    role = session["temp_role"]
    
    if request.method == "POST":
        ho_ten = request.form.get("ho_ten", "Ẩn danh")
        session["ho_ten"] = ho_ten
        session["role"] = role
        
        if role == "admin":
            session["bo_phan"] = "Quản trị Hệ thống"
        else:
            session["bo_phan"] = request.form.get("bo_phan", "Không rõ")
            
        session.pop("temp_role", None)
        
        # Ghi log đăng nhập
        database.ghi_log(session["ho_ten"], session["bo_phan"], "Đăng nhập", "Vào hệ thống thành công")
        return redirect("/hoa-chat")
        
    return render_template("khai_bao.html", role=role)

@app.route("/logout")
def logout():
    if "ho_ten" in session:
        database.ghi_log(session["ho_ten"], session.get("bo_phan", ""), "Đăng xuất", "Thoát hệ thống")
    session.clear()
    return redirect("/")

# ================= TRANG CHỦ =================
@app.route("/")
def home():
    thong_ke = database.lay_thong_ke_nha_may()
    return render_template("index.html", tk=thong_ke)

# ================= DANH SÁCH HÓA CHẤT (Yêu cầu đăng nhập) =================
@app.route("/hoa-chat")
def chemicals():
    # YÊU CẦU ĐĂNG NHẬP MỚI ĐƯỢC XEM
    if "role" not in session:
        return redirect("/login")
        
    tu_khoa = request.args.get("tu_khoa", "")
    if tu_khoa:
        danh_sach = database.tim_kiem_hoa_chat(tu_khoa)
    else:
        danh_sach = database.lay_tat_ca_hoa_chat()
    return render_template("chemicals.html", danh_sach=danh_sach, tu_khoa=tu_khoa)

# ================= TRUY XUẤT MSDS (Ghi vết tự động) =================
@app.route("/xem-msds/<int:id>")
def xem_msds(id):
    if "role" not in session:
        return redirect("/login")
        
    hc = database.lay_mot_hoa_chat(id)
    if hc and hc["msds_link"]:
        chi_tiet = f"Xem / Tải MSDS hóa chất: {hc['ten_sap']} (CAS: {hc['so_cas']})"
        database.ghi_log(session["ho_ten"], session["bo_phan"], "Truy xuất MSDS", chi_tiet)
        return redirect(hc["msds_link"])
    return "Không tìm thấy link MSDS!", 404

# ================= LỊCH SỬ HỆ THỐNG (Chỉ Admin) =================
@app.route("/lich-su")
def lich_su():
    if session.get("role") != "admin":
        return redirect("/hoa-chat")
    logs = database.lay_lich_su()
    return render_template("lich_su.html", logs=logs)

# ================= THAO TÁC ADMIN (Ghi vết tự động) =================
@app.route("/them-hoa-chat", methods=["POST"])
def them_hoa_chat():
    if session.get("role") != "admin": return redirect("/hoa-chat")
    d = lay_du_lieu_form()
    database.them_hoa_chat(d)
    database.ghi_log(session["ho_ten"], session["bo_phan"], "Thêm Mới", f"Thêm hóa chất: {d['ten_sap']}")
    return redirect("/hoa-chat")

@app.route("/xoa/<int:id>")
def xoa_hoa_chat(id):
    if session.get("role") != "admin": return redirect("/hoa-chat")
    hc = database.lay_mot_hoa_chat(id)
    database.xoa_hoa_chat(id)
    database.ghi_log(session["ho_ten"], session["bo_phan"], "Xóa", f"Xóa hóa chất: {hc['ten_sap']} (ID: {id})")
    return redirect("/hoa-chat")

@app.route("/cap-nhat/<int:id>", methods=["POST"])
def cap_nhat_hoa_chat(id):
    if session.get("role") != "admin": return redirect("/hoa-chat")
    d = lay_du_lieu_form()
    database.cap_nhat_hoa_chat(id, d)
    database.ghi_log(session["ho_ten"], session["bo_phan"], "Chỉnh sửa", f"Cập nhật thông tin hóa chất: {d['ten_sap']}")
    return redirect("/hoa-chat")

@app.route("/nguon-goc/<int:id>/<loai>")
def cap_nhat_nguon_goc(id, loai):
    if session.get("role") != "admin": return jsonify({"status": "loi_quyen"})
    if loai in ["trong_nuoc", "ngoai_nuoc"]:
        database.cap_nhat_nguon_goc(id, loai)
    return jsonify({"status": "thanh_cong"})

@app.route("/nha-may/<int:id>/<loai>")
def cap_nhat_nha_may(id, loai):
    if session.get("role") != "admin": return jsonify({"status": "loi_quyen"})
    if loai in ["long_hau", "go_vap"]:
        database.cap_nhat_nha_may(id, loai)
    return jsonify({"status": "thanh_cong"})

@app.route("/sua/<int:id>")
def sua_hoa_chat_form(id):
    if session.get("role") != "admin": return redirect("/hoa-chat")
    hoa_chat = database.lay_mot_hoa_chat(id)
    return render_template("sua.html", hc=hoa_chat)

@app.route("/msds/<int:id>")
def cap_nhat_msds(id):
    if session.get("role") != "admin": return redirect("/hoa-chat")
    link = request.args.get("link", "")
    database.cap_nhat_msds(id, link)
    hc = database.lay_mot_hoa_chat(id)
    database.ghi_log(session["ho_ten"], session["bo_phan"], "Cập nhật MSDS", f"Thêm link MSDS cho hóa chất {hc['ten_sap']}")
    return redirect("/hoa-chat")

@app.route("/xuat-bao-cao")
def xuat_bao_cao():
    if session.get("role") != "admin": 
        return redirect("/hoa-chat")
    
    database.ghi_log(session["ho_ten"], session["bo_phan"], "Xuất Dữ Liệu", "Tải xuống file Excel báo cáo hóa chất")
    danh_sach = database.lay_tat_ca_hoa_chat()
    si = StringIO()
    si.write('\ufeff')
    writer = csv.writer(si)
    writer.writerow(["STT", "Code mua", "Tên Hóa chất (SAP)", "Tên thường gọi", "Nguồn gốc", "Nhà máy", "Số CAS", "Công thức", "Khu vực sử dụng", "Dạng tồn tại", "Xuất xứ", "Số lượng"])
    for idx, hc in enumerate(danh_sach, 1):
        nguon = "Trong nước" if hc["nguon_goc"] == "trong_nuoc" else ("Ngoài nước" if hc["nguon_goc"] == "ngoai_nuoc" else "")
        nha_may = "Long Hậu" if hc["nha_may"] == "long_hau" else ("Gò Vấp" if hc["nha_may"] == "go_vap" else "")
        writer.writerow([
            idx, hc["code_mua"], hc["ten_sap"], hc["ten_thuong_goi"],
            nguon, nha_may, hc["so_cas"], hc["cong_thuc"],
            hc["khu_vuc_su_dung"], hc["dang_ton_tai"], hc["xuat_xu"], hc["so_luong"]
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Bao_Cao_Hoa_Chat_HSE.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output

if __name__ == "__main__":
    app.run(debug=True)