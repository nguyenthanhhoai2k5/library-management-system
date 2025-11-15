from app import create_app, db
from app.models import User
app = create_app()

# Tạo bảng và đảm bảo schema mới có các cột thêm vào (nếu DB cũ thiếu các cột mới)
with app.app_context():
    db.create_all()
    print("Database đã được tạo/được cập nhật!")

    # Kiểm tra schema của bảng `user` và thêm các cột nếu thiếu (không xóa dữ liệu hiện có)
    try:
        from sqlalchemy import text

        conn = db.engine.connect()
        result = conn.execute(text("PRAGMA table_info('user')"))
        existing_cols = [row[1] for row in result.fetchall()]

        # Các cột mới mong muốn (tên: DDL SQL for ALTER)
        to_add = [
            ("avatar", "VARCHAR(256) DEFAULT 'default-avatar.png'"),
            ("cover_photo", "VARCHAR(256) DEFAULT 'default-cover.jpg'"),
            ("full_name", "VARCHAR(128)"),
            ("birth_date", "DATE"),
            ("address", "VARCHAR(256)"),
            ("hobbies", "TEXT")
        ]

        for col_name, col_def in to_add:
            if col_name not in existing_cols:
                try:
                    alter_sql = f"ALTER TABLE user ADD COLUMN {col_name} {col_def};"
                    conn.execute(text(alter_sql))
                    print(f"✅ Added column {col_name} to user table")
                except Exception as e:
                    # Nếu ALTER TABLE thất bại, in lỗi nhưng tiếp tục
                    print(f"⚠️ Could not add column {col_name}: {e}")

        conn.close()
    except Exception as e:
        print(f"⚠️ Lỗi khi kiểm tra/điều chỉnh schema: {e}")

    # Tạo admin nếu chưa tồn tại
    admin_exists = User.query.filter_by(username='admin').first()
    if not admin_exists:
        admin = User(username='admin', email='admin@lib.com', role='admin')
        admin.set_password('123456')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)  


# Để tiến hành chạy chúng ta cần các bước sau:
# Thiết lập môi trường ảo
# venv\Scripts\activate       # Windows

# 2. Cài lại package (đảm bảo)
# pip install -r requirements.txt

# 3. Chạy app
# python run.py

# Chạy dự án chạy khi tải từ file zip trên GitHub nếu tạo môi trường ảo bị lỗi.

# Mở PowerShell với quyền Administrator (Nhấn phím Windows, gõ "PowerShell", chuột phải vào "Windows PowerShell" hoặc "Terminal", chọn Run as administrator).
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser   ==> Chạy lệnh
# Mở Terminal trên Visual Studio Code chạy lệnh sau: ==>  .\venv\Scripts\activate 
# Chạy lệnh ==> venv\Scripts\activate     
# python run.py  
