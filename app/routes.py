from flask import app, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.forms import LoginForm, RegisterForm
from app.forms import BookForm
from sqlalchemy import or_
from wtforms import StringField
from datetime import datetime, timedelta  # Import thời gian 
from app.models import User, Book, Borrow, Reservation  # <-- THÊM Borrow, Reservation
from flask_wtf import FlaskForm
from flask import jsonify
from sqlalchemy import func
# Không import create_app ở đây nữa!
# Import hỗ trợ
import os
from werkzeug.utils import secure_filename
from app import db
from flask import current_app

# Trang Profile 
from app.forms import EditProfileForm

# Đoạn mã up images
def save_cover_image(file):
    try:
        if not file or not file.filename:
            print("No file provided")
            return None
        
        print(f"🔄 Processing file: {file.filename}")
        
        # DEBUG: Kiểm tra UPLOAD_FOLDER
        upload_folder = current_app.config['UPLOAD_FOLDER']
        print(f"📁 UPLOAD_FOLDER: {upload_folder}")
        print(f"📁 UPLOAD_FOLDER exists: {os.path.exists(upload_folder)}")
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(upload_folder, exist_ok=True)
        print(f"📁 UPLOAD_FOLDER created: {os.path.exists(upload_folder)}")
        
        # Tạo tên file
        import uuid
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}"
        
        file_path = os.path.join(upload_folder, unique_filename)
        print(f"💾 File will be saved to: {file_path}")

        # Thử ghi file
        file.save(file_path)
        print(f"✅ File saved successfully!")
        
        # Kiểm tra file thực tế
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ File verified: {file_path} ({file_size} bytes)")
            
            # Trả về đường dẫn đúng
            return f'uploads/{unique_filename}'
        else:
            print(f"❌ File save failed - file not found!")
            return None
            
    except Exception as e:
        print(f"❌ Error saving file: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return None
    
# Lưu ảnh trong tính năng Profile
# app/routes.py → SỬA HÀM save_upload
def save_upload(file, folder):
    if file and file.filename:
        filename = secure_filename(file.filename)
        # LƯU VÀO static/uploads/avatars/
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        # TRẢ VỀ ĐƯỜNG DẪN TỪ static/
        return f'uploads/{folder}/{filename}'  # ĐÚNG: uploads/avatars/xxx.jpg
    return None

@login_manager.user_loader    
def load_user(user_id):
    return User.query.get(int(user_id))

def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('index'))
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash('Tên đăng nhập đã tồn tại.', 'danger')
                return redirect(url_for('register'))
            user = User(username=form.username.data, email=form.email.data, role='user')
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Đăng ký thành công! Hãy đăng nhập.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Đã đăng xuất.', 'success')
        return redirect(url_for('index'))

    # ------------- PHÂN QUYỀN ADMIN -----------------
    def admin_required(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != 'admin':
                flash('Bạn không có quyền truy cập trang này.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function

        # --- QUẢN LÝ SÁCH ---    (---Phân đang sửa chữa---)
        # app/routes.py → SỬA ROUTE /books
    @app.route('/books')
    def books():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '').strip()
        author = request.args.get('author', '').strip()
        genre = request.args.get('genre', '').strip()

        query = Book.query
        if search:
            query = query.filter(Book.title.ilike(f'%{search}%'))
        if author:
            query = query.filter(Book.author.ilike(f'%{author}%'))
        if genre:
            query = query.filter(Book.genre.ilike(f'%{genre}%'))

        books_pagination = query.order_by(Book.title).paginate(
            page=page, per_page=10, error_out=False
        )

        # TẠO FORM TÌM KIẾM - CÁCH NGẮN GỌN
        class SearchForm(FlaskForm):
            search = StringField('Tên sách')
            author = StringField('Tác giả')
            genre = StringField('Thể loại')

        # TRUYỀN GIÁ TRỊ MẶC ĐỊNH KHI TẠO FORM
        search_form = SearchForm(
            search=search,
            author=author, 
            genre=genre
        )

        return render_template(
            'books/list.html',
            books=books_pagination,
            form=search_form,
            current_user=current_user
        )
    # SỬA add_book & edit_book
    @app.route('/books/add', methods=['GET', 'POST'])
    @admin_required
    def add_book():
        form = BookForm()
        if form.validate_on_submit():
            # Validate ISBN uniqueness (if provided)
            if form.isbn.data:
                existing = Book.query.filter_by(isbn=form.isbn.data).first()
                if existing:
                    form.isbn.errors.append('Mã đã tồn tại, Vui lòng chọn mã khác')
                    return render_template('books/form.html', form=form, book=None)
            cover_path = save_cover_image(form.cover_image.data)
            book = Book(
                title=form.title.data,
                author=form.author.data,
                genre=form.genre.data or None,
                isbn=form.isbn.data or None,
                available_copies=form.available_copies.data,
                cover_image=cover_path,
                description=form.description.data or None
            )
            db.session.add(book)
            db.session.commit()
            flash('Thêm sách thành công!', 'success')
            return redirect(url_for('books'))
        return render_template('books/form.html', form=form, book=None)

    @app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
    @admin_required
    def edit_book(id):
        book = Book.query.get_or_404(id)
        form = BookForm(obj=book)
        if form.validate_on_submit():
            if form.cover_image.data:
                book.cover_image = save_cover_image(form.cover_image.data)
            # Validate ISBN uniqueness on edit (ensure not used by other book)
            if form.isbn.data:
                existing = Book.query.filter(Book.isbn == form.isbn.data, Book.id != book.id).first()
                if existing:
                    form.isbn.errors.append('Mã đã tồn tại, Vui lòng chọn mã khác')
                    return render_template('books/form.html', form=form, book=book)
            book.title = form.title.data
            book.author = form.author.data
            book.genre = form.genre.data or None
            book.isbn = form.isbn.data or None
            book.available_copies = form.available_copies.data
            book.description = form.description.data or None
            db.session.commit()
            flash('Cập nhật sách thành công!', 'success')
            return redirect(url_for('books'))
        return render_template('books/form.html', form=form, book=book)

    @app.route('/books/delete/<int:id>', methods=['POST'])
    @admin_required
    def delete_book(id):
        book = Book.query.get_or_404(id)
        
        # Chỉ kiểm tra sách có đang được mượn không
        active_borrows = Borrow.query.filter_by(book_id=id).filter(Borrow.return_date.is_(None)).first()
        if active_borrows:
            flash(f'Không thể xóa sách "{book.title}" vì hiện đang có người mượn!', 'danger')
            return redirect(url_for('books'))

        # Kiểm tra có đơn đặt trước đang chờ không
        pending_res = Reservation.query.filter_by(book_id=id, status='pending').first()
        if pending_res:
            flash(f'Không thể xóa sách "{book.title}" vì có người đang đặt trước!', 'danger')
            return redirect(url_for('books'))

        try:
            # Xóa tất cả lịch sử mượn sách
            Borrow.query.filter_by(book_id=id).delete()
            
            # Xóa tất cả lịch sử đặt trước
            Reservation.query.filter_by(book_id=id).delete()
            
            # Xóa file ảnh bìa nếu có
            if book.cover_image:
                try:
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book.cover_image)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print(f"✅ Đã xóa file ảnh bìa: {image_path}")
                except Exception as e:
                    print(f"❌ Lỗi khi xóa file ảnh bìa: {str(e)}")

            # Xóa sách
            db.session.delete(book)
            db.session.commit()
            flash('Xóa sách thành công!', 'success')
            return redirect(url_for('books'))
        except Exception as e:
            db.session.rollback()
            print(f"❌ Lỗi khi xóa sách: {str(e)}")
            flash('Có lỗi xảy ra khi xóa sách. Vui lòng thử lại!', 'danger')
            return redirect(url_for('books'))

        # Xóa file ảnh bìa trước khi xóa sách
        if book.cover_image:
            try:
                # Lấy đường dẫn đầy đủ đến file ảnh
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book.cover_image)
                # Kiểm tra file có tồn tại không
                if os.path.exists(image_path):
                    # Xóa file
                    os.remove(image_path)
                    print(f"✅ Đã xóa file ảnh bìa: {image_path}")
            except Exception as e:
                print(f"❌ Lỗi khi xóa file ảnh bìa: {str(e)}")
                # Vẫn tiếp tục xóa sách ngay cả khi không xóa được ảnh

        # Xóa sách khỏi database
        db.session.delete(book)
        db.session.commit()
        flash('Xóa sách thành công!', 'success')
        return redirect(url_for('books'))
    

        # --- MƯỢN SÁCH ---
    @app.route('/borrow/<int:book_id>', methods=['POST'])
    @login_required
    def borrow_book(book_id):
        # CHỈ USER ĐƯỢC MƯỢN
        if current_user.role != 'user':
            flash('Chỉ người dùng mới được mượn sách.', 'warning')
            return redirect(url_for('books'))

        book = Book.query.get_or_404(book_id)
        
        # KIỂM TRA KỸ available_copies
        if book.available_copies <= 0:
            flash('Sách đã hết, vui lòng đặt trước.', 'warning')
            return redirect(url_for('books'))

        # SỬA LỖI: Kiểm tra bằng return_date thay vì returned
        existing_borrow = Borrow.query.filter_by(
            book_id=book_id, 
            user_id=current_user.id
        ).filter(Borrow.return_date.is_(None)).first()  # Sách chưa trả
        
        if existing_borrow:
            flash('Bạn đang mượn sách này rồi.', 'warning')
            return redirect(url_for('books'))

        # TẠO LƯỢT MƯỢN
        due_date = datetime.utcnow() + timedelta(days=14)
        borrow = Borrow(
            book_id=book.id,
            user_id=current_user.id,
            due_date=due_date
        )
        book.available_copies -= 1
        db.session.add(borrow)
        db.session.commit()

        flash(f'Đã mượn sách "{book.title}". Hạn trả: {due_date.strftime("%d/%m/%Y")}', 'success')
        return redirect(url_for('my_borrows'))

    @app.route('/borrow/request/<int:book_id>', methods=['POST'])
    @login_required
    def borrow_request(book_id):
        """Xử lý form Quy Định Mượn Sách: thu thông tin người mượn và ngày trả (dd/MM/yyyy hoặc input date).
        Nếu trường return_date hợp lệ thì dùng giá trị đó, nếu không dùng mặc định 14 ngày.
        """
        if current_user.role != 'user':
            flash('Chỉ người dùng mới được mượn sách.', 'warning')
            return redirect(url_for('books'))

        book = Book.query.get_or_404(book_id)
        if book.available_copies <= 0:
            flash('Sách đã hết, vui lòng đặt trước.', 'warning')
            return redirect(url_for('books'))

        # Lấy dữ liệu từ form
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        email = request.form.get('email', '').strip()
        return_date_raw = request.form.get('return_date', '').strip()
        agree = request.form.get('agree')

        # Kiểm tra đồng ý quy định
        if not agree:
            flash('Bạn phải đồng ý với quy định mượn sách để tiếp tục.', 'warning')
            return redirect(request.referrer or url_for('books'))

        # Kiểm tra vài trường cơ bản
        if not full_name or not phone or not address or not email:
            flash('Vui lòng điền đầy đủ thông tin cá nhân.', 'warning')
            return redirect(request.referrer or url_for('books'))

        # Parse return_date: chấp nhận dd/MM/yyyy hoặc yyyy-MM-dd
        due_date = None
        if return_date_raw:
            from datetime import datetime as _dt
            for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
                try:
                    parsed = _dt.strptime(return_date_raw, fmt)
                    # Set to end of day for due date
                    due_date = parsed
                    break
                except Exception:
                    continue

        if due_date is None:
            due_date = datetime.utcnow() + timedelta(days=14)

        # Kiểm tra người đã mượn cùng sách nhưng chưa trả
        existing_borrow = Borrow.query.filter_by(
            book_id=book_id,
            user_id=current_user.id
        ).filter(Borrow.return_date.is_(None)).first()
        if existing_borrow:
            flash('Bạn đang mượn sách này rồi.', 'warning')
            return redirect(url_for('books'))

        # Tạo bản ghi mượn
        borrow = Borrow(
            book_id=book.id,
            user_id=current_user.id,
            due_date=due_date
        )
        book.available_copies -= 1
        db.session.add(borrow)
        db.session.commit()

        flash(f'Đã mượn sách "{book.title}". Hạn trả: {due_date.strftime("%d/%m/%Y")}', 'success')
        return redirect(url_for('my_borrows'))

    # --- TRẢ SÁCH ---
    @app.route('/return/<int:borrow_id>', methods=['POST'])
    @login_required
    def return_book(borrow_id):
        borrow = Borrow.query.get_or_404(borrow_id)
        
        if borrow.user_id != current_user.id and current_user.role != 'admin':
            flash('Bạn không có quyền trả sách này.', 'danger')
            return redirect(url_for('my_borrows'))

        if borrow.return_date:  # SỬA: return_date, không phải returned
            flash('Sách đã được trả trước đó.', 'info')
            return redirect(url_for('my_borrows'))

        borrow.return_date = datetime.utcnow()
        borrow.fine_amount = borrow.calculate_fine()
        borrow.book.available_copies += 1

        # Tự động duyệt đặt trước
        reservation = Reservation.query.filter_by(book_id=borrow.book_id, status='pending').first()
        if reservation:
            reservation.status = 'approved'

        db.session.commit()
        flash(f'Đã trả sách. Phạt: {borrow.fine_amount:,.0f} VNĐ', 'success')
        return redirect(url_for('my_borrows'))

    @app.route('/borrow/delete/<int:borrow_id>', methods=['POST'])
    @login_required
    def delete_borrow(borrow_id):
        """Cho phép người dùng xóa bản ghi mượn khi sách đã được trả.
        Chỉ chủ sở hữu bản ghi hoặc admin mới có quyền xóa.
        """
        borrow = Borrow.query.get_or_404(borrow_id)
        # Quyền: chỉ chủ sở hữu hoặc admin
        if borrow.user_id != current_user.id and current_user.role != 'admin':
            flash('Bạn không có quyền xóa bản ghi này.', 'danger')
            return redirect(url_for('my_borrows'))

        # Chỉ cho xóa khi sách đã trả (tránh xóa bản ghi đang mượn)
        if borrow.return_date is None:
            flash('Không thể xóa bản ghi đang mượn. Vui lòng trả sách trước khi xóa.', 'warning')
            return redirect(url_for('my_borrows'))

        db.session.delete(borrow)
        db.session.commit()
        flash('Bản ghi mượn đã được xóa.', 'success')
        return redirect(url_for('my_borrows'))

    # --- ĐẶT TRƯỚC ---
    # SỬA: Chỉ cho phép POST, không cần GET
    @app.route('/reserve/<int:book_id>', methods=['POST'])  # CHỈ POST
    @login_required
    def reserve_book(book_id):
        if current_user.role != 'user':
            flash('Chỉ người dùng mới được đặt trước.', 'warning')
            return redirect(url_for('books'))

        book = Book.query.get_or_404(book_id)
        if book.available_copies > 0:
            flash('Sách còn bản, bạn có thể mượn ngay.', 'info')
            return redirect(url_for('books'))

        # KIỂM TRA TRÙNG LẶP ĐẶT TRƯỚC
        existing = Reservation.query.filter_by(
            book_id=book_id, 
            user_id=current_user.id, 
            status='pending'
        ).first()
        
        if existing:
            flash('Bạn đã đặt trước sách này rồi.', 'warning')
        else:
            reservation = Reservation(book_id=book_id, user_id=current_user.id)
            db.session.add(reservation)
            db.session.commit()
            flash('Đã đặt trước sách thành công!', 'success')
        
        return redirect(url_for('books'))

    # --- XEM SÁCH ĐANG MƯỢN ---
    @app.route('/my-borrows')
    @login_required
    def my_borrows():
        if current_user.role == 'admin':
            # Admin: Lấy tất cả sách đang mượn của tất cả người dùng
            borrows = Borrow.query.filter_by(return_date=None).order_by(Borrow.borrow_date.desc()).all()
        else:
            # User: Lấy chỉ sách đang mượn của user hiện tại
            borrows = Borrow.query.filter_by(user_id=current_user.id).order_by(Borrow.borrow_date.desc()).all()
        return render_template('borrows/my_borrows.html', borrows=borrows)

    # --- DASHBOARD ADMIN: SÁCH QUÁ HẠN ---
    @app.route('/admin/overdue')
    @admin_required
    def admin_overdue():
        overdue = Borrow.query.filter(
            Borrow.return_date.is_(None),
            Borrow.due_date < datetime.utcnow()
        ).all()
        return render_template('admin/overdue.html', overdue=overdue, datetime=datetime)

    # --- QUẢN LÝ TÀI KHOẢN NGƯỜI DÙNG ---
    @app.route('/admin/manage-users')
    @admin_required
    def manage_users():
        users = User.query.filter_by(role='user').all()
        return render_template('admin/manager_user.html', users=users)

    @app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
    @admin_required
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        
        # Không cho phép xóa admin
        if user.role == 'admin':
            flash('Không thể xóa tài khoản admin!', 'danger')
            return redirect(url_for('manage_users'))
        
        # Kiểm tra xem user có sách chưa trả không
        unreturned_books = Borrow.query.filter_by(user_id=user_id, return_date=None).all()
        if unreturned_books:
            flash(f'Không thể xóa user {user.username}! User còn {len(unreturned_books)} sách chưa được trả.', 'danger')
            return redirect(url_for('manage_users'))
        
        # Xóa tất cả bản ghi mượn của user trước khi xóa user
        Borrow.query.filter_by(user_id=user_id).delete()
        Reservation.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Tài khoản người dùng {user.username} đã được xóa!', 'success')
        return redirect(url_for('manage_users'))
    
    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        # Thống kê tổng quan
        stats = {
            'total_books': Book.query.count(),
            'active_borrows': Borrow.query.filter_by(return_date=None).count(),
            'overdue': Borrow.query.filter(
                Borrow.return_date.is_(None),
                Borrow.due_date < datetime.utcnow()
            ).count(),
            'total_users': User.query.filter_by(role='user').count()
        }

        # Top 5 sách
        # Top 5 sách
        top_books_result = db.session.query(
            Book.title,
            func.count(Borrow.id).label('borrow_count')
        ).join(Borrow).group_by(Book.id, Book.title).order_by(func.count(Borrow.id).desc()).limit(5).all()

        # Chuyển đổi list các Row/Tuple thành List of Dictionaries
        # Mỗi Row có thể được chuyển đổi bằng ._asdict() hoặc duyệt qua cột
        top_books = [{'title': title, 'borrow_count': count} for title, count in top_books_result]


        # Top 5 user
        top_users_result = db.session.query(
            User.username,
            User.full_name,
            func.count(Borrow.id).label('borrow_count')
        ).join(Borrow).filter(User.role == 'user').group_by(User.id, User.username, User.full_name).order_by(func.count(Borrow.id).desc()).limit(5).all()

        # Chuyển đổi list các Row/Tuple thành List of Dictionaries
        top_users = [{'username': username, 'full_name': full_name, 'borrow_count': count} for username, full_name, count in top_users_result]


        # Cần đảm bảo cột `Book.title` và `User.username` cũng có trong GROUP BY (cần thiết nếu bạn dùng Postgres/MySQL/SQL Server, không cần thiết với SQLite)
        # Tôi đã thêm chúng vào truy vấn trên để tăng tính tương thích.

        return render_template(
            'admin/dashboard.html',
            stats=stats,
            top_books=top_books,  # Bây giờ là list of dicts chuẩn
            top_users=top_users   # Bây giờ là list of dicts chuẩn
        )
    
    # Models cho tính năng Profile
    @app.route('/profile')
    @login_required
    def profile():
        borrows = Borrow.query.filter_by(user_id=current_user.id).order_by(Borrow.borrow_date.desc()).all()
        # Tạo form để chỉnh sửa profile
        form = EditProfileForm()
        form.full_name.data = current_user.full_name
        form.birth_date.data = current_user.birth_date
        form.address.data = current_user.address
        form.hobbies.data = current_user.hobbies
        return render_template('profile/profile.html', borrows=borrows, form=form)

    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        form = EditProfileForm()
        if form.validate_on_submit():
            # No longer accept avatar/cover uploads from users; keep default images from models.py
            current_user.full_name = form.full_name.data
            current_user.gender = form.gender.data
            current_user.birth_date = form.birth_date.data
            current_user.address = form.address.data
            current_user.hobbies = form.hobbies.data
            
            db.session.commit()
            flash('Cập nhật hồ sơ thành công!', 'success')
            return redirect(url_for('profile'))
        
        # Load dữ liệu hiện tại
        form.full_name.data = current_user.full_name
        form.gender.data = current_user.gender
        form.birth_date.data = current_user.birth_date
        form.address.data = current_user.address
        form.hobbies.data = current_user.hobbies
        
        return render_template('profile/edit_modal.html', form=form)
    # Models Bootstrap Carousel cho trang index.html, hình ảnh ở libary_app/static/fontend/
    @app.route('/')
    def Carousel():
        images = ['anh1.jpg', 'anh2.jpg', 'anh3.jpg', 'anh4.jpg', 'anh5.jpg', 'anh_06.jpg']
        return render_template('index.html', images=images)   