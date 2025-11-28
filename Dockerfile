# Chọn Python version (nên khớp với version bạn đang dev)
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Flask mặc định chạy port 5000
EXPOSE 5000

# Biến môi trường để Python in log trực tiếp ra terminal
ENV PYTHONUNBUFFERED=1

# Lệnh chạy: Dùng python chạy file run.py
CMD ["python", "run.py"]