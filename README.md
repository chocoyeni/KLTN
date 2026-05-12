# Hướng dẫn cài đặt mã nguồn hệ thống sinh đề tự động

# 1. Yêu cầu hệ thống

Hệ thống được phát triển và kiểm thử trên môi trường:

* Ubuntu / Windows
* Python 3.10+
* R 4.3+
* Moodle 4.x
* MySQL
* JAGS 4.x

# 2. Cài đặt Moodle

Tải Moodle từ trang chính thức:

* https://download.moodle.org/

Sau khi tải và giải nén:

sudo mv moodle /var/www/html/

Phân quyền thư mục:

sudo chown -R www-data:www-data /var/www/html/moodle

sudo chmod -R 755 /var/www/html/moodle

Khởi động Apache và MySQL:

sudo systemctl start apache2

sudo systemctl start mysql

Truy cập:

http://localhost/moodle

để hoàn tất cài đặt Moodle.

# 3. Cài đặt Plugin Moodle

Copy plugin vào thư mục:

moodle/local/ednet_import

Sau đó truy cập:

Site administration -> Notifications

để Moodle tự động cập nhật database.

# 4. Cài đặt Python Environment

Tạo virtual environment:

python -m venv venv

Kích hoạt môi trường:

Windows:

venv\Scripts\activate

Ubuntu:

source venv/bin/activate

Cài đặt thư viện:

pip install fastapi uvicorn pandas numpy scikit-learn


# 5. Chạy FastAPI Server

Di chuyển tới thư mục server:

cd api_server

Khởi động server:

uvicorn main:app --reload

Server chạy tại:

http://127.0.0.1:8000

# 6. Cài đặt R và JAGS

Cài đặt R:

* https://cran.r-project.org/

Cài đặt JAGS:

* https://mcmc-jags.sourceforge.io/

Cài đặt thư viện R:

install.packages("rjags")

install.packages("coda")

install.packages("dplyr")

install.packages("readr")

# 7. Huấn luyện mô hình LNIRT

Chạy file huấn luyện:

source("train.R")

Sau khi huấn luyện hoàn tất, hệ thống sinh ra file:

lnirt_item_clean.csv

File này được sử dụng bởi FastAPI Server để phục vụ quá trình sinh đề kiểm tra.

# 8. Sinh đề kiểm tra

Truy cập giao diện Moodle Plugin.

Người dùng nhập:

* số lượng câu Easy
  
* số lượng câu Medium
  
* số lượng câu Hard

Hệ thống sẽ gửi request tới FastAPI Server và trả kết quả sinh đề.

# 9. Xuất kết quả CSV

Sau khi sinh đề, người dùng có thể export danh sách câu hỏi dưới dạng file CSV trực tiếp trên giao diện Moodle.
