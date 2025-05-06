# Đồ án môn học Khai thác dữ liệu

Repository này là đồ án môn học Khai thác dữ liệu. Triển khai thuật toán **Closet+** từ lý thuyết lên thành code với ngôn ngữ **Python**.

## Cấu trúc dự án

Dự án chia làm 2 phần chính:

- **Backend**: Chạy thuật toán Closet+ và triển khai Flask API.  
- **Frontend**: Nhận dữ liệu từ API của server, vẽ cây FP-Tree và hiển thị kết quả.

---

## Dự án đã triển khai giao diện người dùng lên web

- **URL Website**: [https://closet-algorithm.vercel.app.](https://closet-algorithm.vercel.app/) 

---

## Cách chạy repository

### Chạy server (backend):

1. Cài đặt các gói cần thiết:
    ```bash
    pip install -r requirement.txt
    ```
2. Di chuyển vào thư mục backend:
    ```bash
    cd backend
    ```
3. Chạy server:
    ```bash
    python app.py
    ```

### Chạy client (frontend):

1. Cài đặt các package:
    ```bash
    npm install
    ```
2. Chạy ứng dụng:
    ```bash
    npm run dev
    ```

---

## Cấu trúc thư mục & chức năng:

```plaintext
/backend/
├── /processed/           # Chứa các file CSV đã chuẩn hóa từ thư mục uploads
├── /uploads/             # Chứa file CSV đầu vào được upload từ giao diện người dùng
├── app.py                # File chính triển khai Flask API, chứa các route chính
├── closetPlus.py         # Chứa logic thuật toán Closet+
└── requirement.txt       # Danh sách các package cần thiết cho server

/frontend/ (những phần quan trọng)
├── /components/
│   ├── FileUploader.jsx  # Upload file CSV, nhập tham số, gọi API lấy dữ liệu
│   ├── ResultDisplay.jsx # Nhận dữ liệu và hiển thị kết quả
│   └── Visualizer.jsx    # Vẽ cây FP-Tree từ dữ liệu
└── App.jsx               # Gọi các component trên, truyền dữ liệu giữa chúng
