import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # Thay đổi khi deploy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False