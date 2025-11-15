from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' hoặc 'user'

    # THÊM MỚI
    avatar = db.Column(db.String(256), default='default-avatar.png')  # static/uploads/avatars/
    cover_photo = db.Column(db.String(256), default='default-cover.jpg')  # static/uploads/covers/
    
    full_name = db.Column(db.String(128))  # Họ và tên đầy đủ của người dùng
    birth_date = db.Column(db.Date)  # Ngày sinh của người dùng
    address = db.Column(db.String(256))  # Địa chỉ của người dùng
    hobbies = db.Column(db.Text)  # Sở thích của người dùng
    # Bổ sung cột giới tính
    gender = db.Column(db.String(10))  # Giới tính của người dùng

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    author = db.Column(db.String(64), nullable=False, index=True)
    genre = db.Column(db.String(64), index=True)
    isbn = db.Column(db.String(13), unique=True)
    available_copies = db.Column(db.Integer, default=1)

    # THÊM MỚI
    cover_image = db.Column(db.String(256))  # Đường dẫn file
    description = db.Column(db.Text)        # Mô tả sách

    def __repr__(self):   # Thêm phương thức __repr__ cho Book (ở giai đoạn 2)
        return f'<Book {self.title}>'
    

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    fine_amount = db.Column(db.Float, default=0.0)

    book = db.relationship('Book', backref=db.backref('borrows', cascade='all,delete-orphan'))
    user = db.relationship('User', backref='borrows')

    def is_overdue(self):
        if self.return_date:  # SỬA: return_date
            return False
        return datetime.utcnow() > self.due_date

    def calculate_fine(self):
        """Tính phạt trễ hạn: 5.000 VNĐ/ngày"""
        if self.return_date:
            days_late = max(0, (self.return_date - self.due_date).days)
        else:
            days_late = max(0, (datetime.utcnow() - self.due_date).days)
        return days_late * 5000

    def get_days_overdue(self):
        """Lấy số ngày trễ hạn"""
        if self.return_date:
            return max(0, (self.return_date - self.due_date).days)
        else:
            return max(0, (datetime.utcnow() - self.due_date).days)

# app/models.py → THÊM VÀO CUỐI FILE

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reserve_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, cancelled

    book = db.relationship('Book', backref='reservations')
    user = db.relationship('User', backref='reservations')

    def __repr__(self):
        return f'<Reservation: User {self.user_id} -> Book {self.book_id}>'