# Đồ án môn học Khai thác dữ liệu

Repository này là đồ án môn học Khai thác dữ liệu. Triển khai thuật toán **Closet+** từ lý thuyết lên thành code với ngôn ngữ là **Python**.

## Cấu trúc dự án

Chia làm 2 phần: **backend**, **frontend**

- **backend**: chạy thuật toán Closet+ và triển khai Flask API  
- **frontend**: nhận dữ liệu từ API của server, vẽ ra cây FP Tree và hiển thị kết quả

## Cách chạy repo

- **Chạy server**:
    + Cài những gói cần thiết cho server từ file `requirement.txt`
    + Vào thư mục backend: `cd backend`
    + Chạy server: `python app.py`
    
- **Chạy client**:
    + Cài đặt thư viện: `npm install`
    + Chạy dev server: `npm run dev`

## Chi tiết chức năng folder, file:

/backend/
├── /processed/ # Chứa các file CSV sau khi chuẩn hóa từ uploads
├── /uploads/ # Chứa file CSV upload từ frontend
├── app.py # Flask API, chứa các route, file chạy chính của server
├── closetPlus.py # Chứa logic thuật toán Closet+
└── requirement.txt # Danh sách các package Python cần cài

/frontend/ (Những phần quan trọng)
├── /components/
│ ├── FileUploader.jsx # Upload file CSV, nhập input, gọi API để lấy dữ liệu
│ ├── ResultDisplay.jsx # Hiển thị kết quả sau xử lý
│ └── Visualizer.jsx # Vẽ cây FP Tree từ dữ liệu
└── App.jsx # Gọi các component trên, truyền dữ liệu giữa chúng