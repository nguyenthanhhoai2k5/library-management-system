import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # Thay đổi khi deploy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # THÊM MỚI
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

    # DEBUG: In ra đường dẫn để kiểm tra
    print(f"🔧 UPLOAD_FOLDER configured: {UPLOAD_FOLDER}")

    # EMAIL CONFIG
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'nhoai2640@gmail.com'  # THAY BẰNG EMAIL CỦA BẠN
    MAIL_PASSWORD = 'suqo arsl picr aqbe'     # DÙNG APP PASSWORD (xem hướng dẫn)
    MAIL_DEFAULT_SENDER = 'nhoai2640@gmail.com'