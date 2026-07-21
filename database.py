import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hse.db")

def ket_noi_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def tao_bang():
    conn = ket_noi_db()
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
    
    # 1. Thêm cột phân thân dữ liệu
    try:
        conn.execute("ALTER TABLE chemicals ADD COLUMN is_master INTEGER DEFAULT 1")
    except:
        pass
        
    # 2. LỆNH GIẢI CỨU DỮ LIỆU: Tự động đưa dữ liệu bị ẩn quay về Bảng Tổng
    count_total = conn.execute("SELECT COUNT(id) FROM chemicals").fetchone()[0]
    count_master = conn.execute("SELECT COUNT(id) FROM chemicals WHERE is_master = 1").fetchone()[0]
    if count_total > 0 and count_master == 0:
        conn.execute("UPDATE chemicals SET is_master = 1")
        
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS phu_trach (
            nha_may TEXT,
            ten_chuyen TEXT,
            chuc_danh TEXT,
            ho_ten TEXT,
            msnv TEXT,
            PRIMARY KEY (nha_may, ten_chuyen)
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

# ================= HÀM CHO BẢNG TỔNG =================
def lay_tat_ca_hoa_chat():
    conn = ket_noi_db()
    # Đã sửa DESC thành ASC
    ket_qua = conn.execute("SELECT * FROM chemicals WHERE is_master = 1 ORDER BY id ASC").fetchall()
    conn.close()
    return ket_qua

def tim_kiem_hoa_chat(tu_khoa):
    conn = ket_noi_db()
    tk = '%' + tu_khoa + '%'
    # Đã sửa DESC thành ASC
    ket_qua = conn.execute("""
        SELECT * FROM chemicals
        WHERE is_master = 1
        AND (code_mua LIKE ? OR ten_sap LIKE ? OR ten_thuong_goi LIKE ? 
           OR so_cas LIKE ? OR cong_thuc LIKE ? OR khu_vuc_su_dung LIKE ? OR dang_ton_tai LIKE ? OR xuat_xu LIKE ?)
        ORDER BY id ASC
    """, (tk, tk, tk, tk, tk, tk, tk, tk)).fetchall()
    conn.close()
    return ket_qua

def lay_thong_ke_nha_may():
    conn = ket_noi_db()
    lh = conn.execute("SELECT SUM(so_luong) FROM chemicals WHERE nha_may = 'long_hau' AND is_master = 1").fetchone()[0]
    gv = conn.execute("SELECT SUM(so_luong) FROM chemicals WHERE nha_may = 'go_vap' AND is_master = 1").fetchone()[0]
    tong = conn.execute("SELECT SUM(so_luong) FROM chemicals WHERE is_master = 1").fetchone()[0]
    conn.close()
    return {
        "long_hau": lh if lh else 0,
        "go_vap": gv if gv else 0,
        "tong_cong": tong if tong else 0
    }

# ================= HÀM CHO BẢNG CHUYỀN =================
def lay_hoa_chat_theo_bo_phan(nha_may, bo_phan):
    conn = ket_noi_db()
    # Đã sửa DESC thành ASC
    ket_qua = conn.execute("""
        SELECT * FROM chemicals 
        WHERE nha_may = ? AND khu_vuc_su_dung = ? AND is_master = 0
        ORDER BY id ASC
    """, (nha_may, bo_phan)).fetchall()
    conn.close()
    return ket_qua

def thong_ke_bo_phan(nha_may, bo_phan):
    conn = ket_noi_db()
    tong_loai = conn.execute("SELECT COUNT(id) FROM chemicals WHERE nha_may = ? AND khu_vuc_su_dung = ? AND is_master = 0", (nha_may, bo_phan)).fetchone()[0]
    tong_so_luong = conn.execute("SELECT SUM(so_luong) FROM chemicals WHERE nha_may = ? AND khu_vuc_su_dung = ? AND is_master = 0", (nha_may, bo_phan)).fetchone()[0]
    so_ran = conn.execute("SELECT COUNT(id) FROM chemicals WHERE nha_may = ? AND khu_vuc_su_dung = ? AND dang_ton_tai = 'Rắn' AND is_master = 0", (nha_may, bo_phan)).fetchone()[0]
    so_long = conn.execute("SELECT COUNT(id) FROM chemicals WHERE nha_may = ? AND khu_vuc_su_dung = ? AND dang_ton_tai = 'Lỏng' AND is_master = 0", (nha_may, bo_phan)).fetchone()[0]
    so_khi = conn.execute("SELECT COUNT(id) FROM chemicals WHERE nha_may = ? AND khu_vuc_su_dung = ? AND dang_ton_tai = 'Khí' AND is_master = 0", (nha_may, bo_phan)).fetchone()[0]
    thieu_msds = conn.execute("SELECT COUNT(id) FROM chemicals WHERE nha_may = ? AND khu_vuc_su_dung = ? AND (msds_link IS NULL OR msds_link = '') AND is_master = 0", (nha_may, bo_phan)).fetchone()[0]
    conn.close()
    
    return {
        "tong_loai": tong_loai if tong_loai else 0,
        "tong_so_luong": tong_so_luong if tong_so_luong else 0,
        "so_ran": so_ran if so_ran else 0,
        "so_long": so_long if so_long else 0,
        "so_khi": so_khi if so_khi else 0,
        "thieu_msds": thieu_msds if thieu_msds else 0
    }
# ================= CRUD DÙNG CHUNG =================
def them_hoa_chat(d, is_master=1):
    conn = ket_noi_db()
    conn.execute("""
        INSERT INTO chemicals
        (code_mua, ten_sap, ten_thuong_goi, nguon_goc, nha_may, so_cas, cong_thuc, khu_vuc_su_dung, dang_ton_tai, xuat_xu, so_luong, is_master)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        d.get("code_mua", ""), d["ten_sap"], d.get("ten_thuong_goi", ""), d.get("nguon_goc", ""), 
        d.get("nha_may", ""), d.get("so_cas", ""), d.get("cong_thuc", ""), 
        d.get("khu_vuc_su_dung", ""), d.get("dang_ton_tai", ""), d.get("xuat_xu", ""), d.get("so_luong", 0), is_master
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
        d.get("code_mua", ""), d["ten_sap"], d.get("ten_thuong_goi", ""), d.get("nguon_goc", ""), 
        d.get("nha_may", ""), d.get("so_cas", ""), d.get("cong_thuc", ""), 
        d.get("khu_vuc_su_dung", ""), d.get("dang_ton_tai", ""), d.get("xuat_xu", ""), d.get("so_luong", 0), id
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

def lay_nguoi_phu_trach(nha_may, ten_chuyen):
    conn = ket_noi_db()
    kq = conn.execute("SELECT * FROM phu_trach WHERE nha_may = ? AND ten_chuyen = ?", (nha_may, ten_chuyen)).fetchone()
    conn.close()
    return kq

def cap_nhat_nguoi_phu_trach(nha_may, ten_chuyen, chuc_danh, ho_ten, msnv):
    conn = ket_noi_db()
    conn.execute("""
        INSERT OR REPLACE INTO phu_trach (nha_may, ten_chuyen, chuc_danh, ho_ten, msnv)
        VALUES (?, ?, ?, ?, ?)
    """, (nha_may, ten_chuyen, chuc_danh, ho_ten, msnv))
    conn.commit()
    conn.close()