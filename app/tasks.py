# app/tasks.py (đang nhân chức năng gửi email nhắc nhở)
from flask_mail import Message
from app import mail, db
from app.models import Borrow, User
from datetime import datetime, timedelta

def send_due_reminders():
    """Gửi email nhắc nhở nếu sách sắp quá hạn (1 ngày trước)"""
    tomorrow = datetime.utcnow() + timedelta(days=1)
    due_books = Borrow.query.filter(
        Borrow.return_date.is_(None),
        Borrow.due_date <= tomorrow,
        Borrow.due_date > datetime.utcnow()
    ).all()

    for borrow in due_books:
        user = User.query.get(borrow.user_id)
        msg = Message(
            subject=f"[Thư viện] Nhắc nhở trả sách: {borrow.book.title}",
            recipients=[user.email],
            body=f"""
Kính gửi {user.username},

Bạn đang mượn sách: **{borrow.book.title}**
Hạn trả: **{borrow.due_date.strftime('%d/%m/%Y')}**

Vui lòng trả sách đúng hạn để tránh phạt 5.000 VNĐ/ngày.

Trân trọng,
Thư viện ABC
            """
        )
        try:
            mail.send(msg)
            print(f"Đã gửi nhắc nhở đến {user.email}")
        except Exception as e:
            print(f"Lỗi gửi email: {e}")