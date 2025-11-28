## Lệnh của docker để chạy
## buid lại đồ án : 
docker-compose up --build

1. Cách bật lại (Hàng ngày): Khi bạn mở máy tính lên và muốn chạy dự án, chỉ cần gõ:
docker-compose up

(Không cần thêm --build nữa. Lệnh này sẽ chạy ngay lập tức, rất nhanh).
Nếu bạn muốn nó chạy ngầm (để tắt terminal mà web vẫn chạy), hãy thêm -d:
docker-compose up -d

docker Hub: 
docker run -p 5000:5000 thanhhoai123/library-app:latest