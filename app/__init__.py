from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from config import Config
from flask import Flask, render_template, request

db = SQLAlchemy()
login_manager = LoginManager() # <-- Instance này được export
bootstrap = Bootstrap5()

def create_app():
    app = Flask(__name__)  # Mai kiểm tra lại ?
    app.config.from_object(Config)

    # Khởi tạo extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    bootstrap.init_app(app)

    # Import và đăng ký routes
    from app.routes import init_routes
    init_routes(app)  # Đăng ký tất cả routes vào app

    return app