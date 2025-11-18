````markdown
# 🧹 AI Dataset Deduplication Tool

Công cụ tự động phát hiện và loại bỏ các ảnh trùng lặp (duplicate) hoặc gần giống nhau (near-duplicate) trong bộ dữ liệu Computer Vision.

Sử dụng thuật toán **CNN (MobileNet)** để trích xuất đặc trưng ảnh, giúp phát hiện được cả những ảnh bị **crop, xoay, thay đổi độ sáng hoặc nhiễu** mà các thuật toán so sánh điểm ảnh thông thường không làm được.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Library](https://img.shields.io/badge/Library-Imagededup-orange)

## 🚀 Tính năng chính

* **Phát hiện thông minh:** Dùng Deep Learning để tìm ảnh có nội dung tương đồng.
* **Tự động chọn lọc:** Trong nhóm ảnh trùng, tự động **giữ lại ảnh có chất lượng tốt nhất** (dựa trên dung lượng file) và loại bỏ các ảnh kém hơn.
* **Đồng bộ Label:** Khi xóa ảnh, tự động tìm và di chuyển file label tương ứng (ví dụ: `.txt` cho YOLO) sang thùng rác.
* **An toàn:** File không bị xóa vĩnh viễn mà được chuyển vào folder `trash_bin` để kiểm tra lại.
* **Báo cáo trực quan:** Tự động sinh file `review_report.html` để người dùng xem lại kết quả so sánh (Giữ vs Xóa) ngay trên trình duyệt.

---

## 📸 Demo Báo Cáo (Visual Report)

Sau khi chạy, công cụ sẽ tạo ra một báo cáo HTML giúp bạn kiểm tra nhanh độ chính xác:

![Giao diện báo cáo](demo_report.png)

*(Cột trái: Ảnh gốc được giữ lại | Cột phải: Ảnh trùng lặp đã bị chuyển vào thùng rác)*

---

## 🛠️ Hướng dẫn Cài đặt

Làm theo các bước sau để thiết lập môi trường chạy sạch sẽ (Sử dụng `.venv`).

### Bước 1: Tạo môi trường ảo (Virtual Environment)

Mở Terminal (MacOS/Linux) hoặc CMD/PowerShell (Windows) tại thư mục dự án:

**MacOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
````

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

*(Khi kích hoạt thành công, bạn sẽ thấy chữ `(.venv)` hiện ở đầu dòng lệnh)*

### Bước 2: Cài đặt thư viện

Chạy lệnh sau để cài đặt các thư viện cần thiết (imagededup, torch, torchvision...):

```bash
pip install -r requirements.txt
```

-----

## ⚙️ Cấu hình

Trước khi chạy, hãy mở file `clean_dataset.py` và chỉnh sửa phần cấu hình ở đầu file cho phù hợp với máy của bạn:

```python
# ================= CẤU HÌNH =================
# 1. Đường dẫn đến thư mục chứa ảnh cần lọc
INPUT_FOLDER = '/path/to/your/dataset/images'

# 2. Đường dẫn đến thư mục chứa label (nếu muốn xóa kèm label)
LABEL_FOLDER = '/path/to/your/dataset/labels'
DELETE_LABELS = True   # Đặt False nếu chỉ muốn xóa ảnh

# 3. Ngưỡng giống nhau (0.0 đến 1.0)
# 0.90: Bắt chặt (ảnh phải rất giống nhau)
# 0.85: Bắt lỏng (chấp nhận ảnh biến đổi nhiều hơn)
THRESHOLD = 0.95               
# ============================================
```

-----

## ▶️ Cách sử dụng

Sau khi cấu hình xong, chạy lệnh:

```bash
python clean_dataset.py
```

**Quá trình xử lý:**

1.  Tải model CNN (chỉ lần đầu tiên).
2.  Quét toàn bộ ảnh và tạo vector đặc trưng.
3.  So sánh và tìm trùng lặp.
4.  Di chuyển file trùng sang thư mục `trash_bin`.
5.  Tạo file báo cáo `review_report.html`.

-----

## ⚠️ Lưu ý

  * **Trên MacOS:** Script đã tích hợp sẵn đoạn mã xử lý lỗi `SSL: CERTIFICATE_VERIFY_FAILED` nên bạn không cần cài đặt thêm chứng chỉ thủ công.
  * **Trash Bin:** Hãy luôn kiểm tra thư mục `trash_bin` và file báo cáo HTML trước khi quyết định xóa vĩnh viễn dữ liệu rác.
