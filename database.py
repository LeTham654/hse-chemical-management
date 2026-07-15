import sqlite3
import os
from datetime import datetime

# Lấy đường dẫn thư mục hiện tại để PythonAnywhere nhận diện đúng file db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hse.db")

def ket_noi_db():
    # Sử dụng DB_PATH thay vì chỉ ghi "hse.db"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def tao_bang():
    conn = ket_noi_db()
    # Bảng Hóa Chất
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chemicals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_mua TEXT,
            ten_sap TEXT NOT NULL,
            ten_thuong_goi TEXT,
            nguon_goc TEXT DEFAULT '',
            nha_may TEXT DEFAULT '',
            so_cas TEXT,
            cong_thuc TEXT,
            khu_vuc_su_dung TEXT,
            dang_ton_tai TEXT,
            msds_link TEXT,
            xuat_xu TEXT,
            so_luong INTEGER
        )
    """)
    # Bảng Lịch sử hệ thống (Lưu vết)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nguoi_thuc_hien TEXT,
            bo_phan TEXT,
            hanh_dong TEXT,
            chi_tiet TEXT,
            thoi_gian TEXT
        )
    """)
    conn.commit()
    conn.close()

def ghi_log(nguoi_thuc_hien, bo_phan, hanh_dong, chi_tiet):
    conn = ket_noi_db()
    thoi_gian_hien_tai = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    conn.execute("""
        INSERT INTO logs (nguoi_thuc_hien, bo_phan, hanh_dong, chi_tiet, thoi_gian)
        VALUES (?, ?, ?, ?, ?)
    """, (nguoi_thuc_hien, bo_phan, hanh_dong, chi_tiet, thoi_gian_hien_tai))
    conn.commit()
    conn.close()

def lay_lich_su():
    conn = ket_noi_db()
    ket_qua = conn.execute("SELECT * FROM logs ORDER BY id DESC").fetchall()
    conn.close()
    return ket_qua

def lay_tat_ca_hoa_chat():
    conn = ket_noi_db()
    ket_qua = conn.execute("SELECT * FROM chemicals ORDER BY id").fetchall()
    conn.close()
    return ket_qua

def them_hoa_chat(d):
    conn = ket_noi_db()
    conn.execute("""
        INSERT INTO chemicals
        (code_mua, ten_sap, ten_thuong_goi, nguon_goc, nha_may, so_cas, cong_thuc, khu_vuc_su_dung, dang_ton_tai, xuat_xu, so_luong)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        d["code_mua"], d["ten_sap"], d["ten_thuong_goi"], d["nguon_goc"], d["nha_may"], d["so_cas"],
        d["cong_thuc"], d["khu_vuc_su_dung"], d["dang_ton_tai"], d["xuat_xu"], d["so_luong"]
    ))
    conn.commit()
    conn.close()

def xoa_hoa_chat(id):
    conn = ket_noi_db()
    conn.execute("DELETE FROM chemicals WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def lay_mot_hoa_chat(id):
    conn = ket_noi_db()
    ket_qua = conn.execute("SELECT * FROM chemicals WHERE id = ?", (id,)).fetchone()
    conn.close()
    return ket_qua

def cap_nhat_hoa_chat(id, d):
    conn = ket_noi_db()
    conn.execute("""
        UPDATE chemicals SET
            code_mua = ?, ten_sap = ?, ten_thuong_goi = ?, nguon_goc = ?, nha_may = ?, so_cas = ?,
            cong_thuc = ?, khu_vuc_su_dung = ?, dang_ton_tai = ?, xuat_xu = ?, so_luong = ?
        WHERE id = ?
    """, (
        d["code_mua"], d["ten_sap"], d["ten_thuong_goi"], d["nguon_goc"], d["nha_may"], d["so_cas"],
        d["cong_thuc"], d["khu_vuc_su_dung"], d["dang_ton_tai"], d["xuat_xu"], d["so_luong"], id
    ))
    conn.commit()
    conn.close()

def cap_nhat_nguon_goc(id, loai):
    conn = ket_noi_db()
    conn.execute("UPDATE chemicals SET nguon_goc = ? WHERE id = ?", (loai, id))
    conn.commit()
    conn.close()

def cap_nhat_nha_may(id, loai):
    conn = ket_noi_db()
    conn.execute("UPDATE chemicals SET nha_may = ? WHERE id = ?", (loai, id))
    conn.commit()
    conn.close()

def cap_nhat_msds(id, link):
    conn = ket_noi_db()
    conn.execute("UPDATE chemicals SET msds_link = ? WHERE id = ?", (link, id))
    conn.commit()
    conn.close()

def tim_kiem_hoa_chat(tu_khoa):
    conn = ket_noi_db()
    tk = '%' + tu_khoa + '%'
    ket_qua = conn.execute("""
        SELECT * FROM chemicals
        WHERE code_mua LIKE ? OR ten_sap LIKE ? OR ten_thuong_goi LIKE ? 
           OR so_cas LIKE ? OR cong_thuc LIKE ? OR khu_vuc_su_dung LIKE ?
           OR dang_ton_tai LIKE ? OR xuat_xu LIKE ?
        ORDER BY id
    """, (tk, tk, tk, tk, tk, tk, tk, tk)).fetchall()
    conn.close()
    return ket_qua

def lay_thong_ke_nha_may():
    conn = ket_noi_db()
    lh = conn.execute("SELECT SUM(so_luong) FROM chemicals WHERE nha_may = 'long_hau'").fetchone()[0]
    gv = conn.execute("SELECT SUM(so_luong) FROM chemicals WHERE nha_may = 'go_vap'").fetchone()[0]
    tong = conn.execute("SELECT SUM(so_luong) FROM chemicals").fetchone()[0]
    conn.close()
    return {
        "long_hau": lh if lh else 0,
        "go_vap": gv if gv else 0,
        "tong_cong": tong if tong else 0
    }