from app import create_app, db
 
app = create_app()

# Tạo bảng chỉ khi chạy lần đầu
with app.app_context():
    db.create_all()
    print("Database đã được tạo!")

if __name__ == '__main__':
    app.run(debug=True)  