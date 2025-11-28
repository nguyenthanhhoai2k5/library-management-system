from app import create_app, db
from app.models import User
import os

app = create_app()

# Tạo bảng và đảm bảo schema mới có các cột thêm vào
with app.app_context():
    db.create_all()
    print("Database đã được tạo/được cập nhật!")

    # Kiểm tra schema của bảng `user` và thêm các cột nếu thiếu
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
                    conn.commit() # Thêm commit để chắc chắn lưu thay đổi
                    print(f"✅ Added column {col_name} to user table")
                except Exception as e:
                    print(f"⚠️ Could not add column {col_name}: {e}")

        conn.close()
    except Exception as e:
        print(f"⚠️ Lỗi khi kiểm tra/điều chỉnh schema: {e}")

    # Tạo admin nếu chưa tồn tại
    try:
        admin_exists = User.query.filter_by(username='admin').first()
        if not admin_exists:
            admin = User(username='admin', email='admin@lib.com', role='admin')
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin account created!")
    except Exception as e:
        print(f"⚠️ Lỗi tạo admin (có thể do bảng chưa sẵn sàng): {e}")

if __name__ == '__main__':
    # --- SỬA ĐỔI QUAN TRỌNG CHO DOCKER ---
    # host='0.0.0.0' để Docker mở cổng ra ngoài
    # debug=True giúp reload code khi bạn sửa file mà không cần restart Docker
    app.run(host='0.0.0.0', port=5000, debug=True)
