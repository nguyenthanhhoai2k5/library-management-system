
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from config import Config
from flask import Flask, render_template, request
import os
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager() # <-- Instance này được export
login_manager.login_view = 'login'  
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
login_manager.login_message_category = 'warning'
bootstrap = Bootstrap5()
mail = Mail()  # THÊM email  
scheduler = BackgroundScheduler()  # THÊM
migrate = Migrate()

def create_app():
    app = Flask(__name__,
                template_folder='../templates', # Chỉ định vị trí template_folder
                static_folder='../static')   # <- THÊM DÒNG NÀY)   
                
    app.config.from_object(Config)

    # TẠO THƯ MỤC UPLOAD NẾU CHƯA CÓ
        # TẠO THƯ MỤC UPLOAD - THÊM DEBUG
    upload_path = app.config['UPLOAD_FOLDER']
    print(f"🚀 Creating upload folder: {upload_path}")
    os.makedirs(upload_path, exist_ok=True)
    print(f"✅ Upload folder ready: {os.path.exists(upload_path)}")

    # Khởi tạo extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)  # THÊM email
    login_manager.login_view = 'login'
    bootstrap.init_app(app)
    migrate.init_app(app, db)  # ĐẢM BẢO CÓ DÒNG NÀY

    # Import và đăng ký routes
    from app.routes import init_routes
    init_routes(app)  # Đăng ký tất cả routes vào app

    with app.app_context():
        db.create_all()
        print("✅ Database đã được cập nhật!")
        from app.tasks import send_due_reminders
        scheduler.add_job(
            func=send_due_reminders,
            trigger="interval",
            hours=24,
            id='daily_reminder',
            replace_existing=True
        )
        if not scheduler.running:
            scheduler.start()

    return app