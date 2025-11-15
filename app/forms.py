from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
# app/forms.py → SỬA BookFor
# app/forms.py → THÊM 2 FORM
from flask_wtf.file import FileField, FileAllowed
from wtforms import DateField, TextAreaField

class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')

class RegisterForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')

# Được bổ sung ở giai đoạn 2
class BookForm(FlaskForm):
    title = StringField('Tên sách', validators=[DataRequired(), Length(max=128)])
    author = StringField('Tác giả', validators=[DataRequired(), Length(max=64)])
    genre = StringField('Thể loại', validators=[Optional(), Length(max=64)])
    isbn = StringField('ISBN', validators=[Optional(), Length(max=13)])
    available_copies = IntegerField('Số bản có sẵn', validators=[DataRequired(), NumberRange(min=0, max=100)], default=1)

    # THÊM MỚI
    cover_image = FileField('Ảnh bìa', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    description = TextAreaField('Mô tả sách', validators=[Optional(), Length(max=1000)])
    
    submit = SubmitField('Lưu sách')

# app/forms.py (THÊM VÀO CUỐI)

class BorrowForm(FlaskForm):
    due_days = IntegerField('Số ngày mượn (mặc định 14)', default=14, validators=[DataRequired(), NumberRange(min=1, max=30)])
    submit = SubmitField('Mượn sách')

class ReturnForm(FlaskForm):
    submit = SubmitField('Xác nhận trả sách')


class BorrowRequestForm(FlaskForm):
    full_name = StringField('Họ và Tên', validators=[DataRequired(), Length(max=128)])
    phone = StringField('Số Điện Thoại', validators=[DataRequired(), Length(max=20)])
    address = StringField('Địa Chỉ', validators=[DataRequired(), Length(max=256)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    # Chấp nhận dd/MM/yyyy nhập tay hoặc sẽ dùng input type=date trên client
    return_date = StringField('Ngày Trả Sách (dd/MM/yyyy)', validators=[Optional()])
    agree = BooleanField('Tôi đã đọc và đồng ý với các quy định', validators=[DataRequired()])
    submit = SubmitField('Xác nhận Mượn')

    def validate_return_date(self, field):
        """Cho phép nhập định dạng dd/MM/yyyy hoặc yyyy-MM-dd (từ input type=date).
        Nếu rỗng, route sẽ dùng giá trị mặc định (14 ngày).
        """
        if not field.data:
            return
        import datetime
        s = field.data.strip()
        for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
            try:
                datetime.datetime.strptime(s, fmt)
                return
            except Exception:
                continue
        raise ValueError('Ngày trả không đúng định dạng (dd/MM/yyyy)')
    
# Thay đổi và cập nhật thông tin cho Profile
class EditProfileForm(FlaskForm):
    full_name = StringField('Họ và Tên', validators=[Optional(), Length(max=128)])
    gender = SelectField('Giới Tính', choices=[('', 'Chọn giới tính'), ('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[Optional()])
    birth_date = DateField('Ngày Sinh', format='%Y-%m-%d', validators=[Optional()])
    address = StringField('Địa Chỉ', validators=[Optional(), Length(max=256)])
    hobbies = TextAreaField('Sở Thích', validators=[Optional(), Length(max=1000)])
    avatar = FileField('Ảnh đại diện', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    cover_photo = FileField('Ảnh bìa', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Cập Nhật')