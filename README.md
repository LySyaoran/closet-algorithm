Repository này là đồ án môn học khai thác dữ liệu. Triển khai thuật toán Closet+ từ lý thuyết
lên thành code với ngôn ngữ là python.

Chia làm 2 phần: backend, frontend
- backend: chạy thuật toán Closet+ và triển khai Flask API
- frontend: nhận dữ liệu từ API của server, vẽ ra cây FP Tree và hiển thị kết quả

Cách chạy repo:
- Chạy server:
    + Cài những gói cần thiết cho server tại file requirement.txt -> cd backend -> py app.py
- Chạy client:
    + npm install -> npm run dev

Chi tiết chức năng folder, file:
/backend/
    - /processed/: folder chứa những file csv sau khi được chuẩn hóa từ những file trong folder uploads
    - /uploads/: folder chứa những file csv được input xử lý từ giao diện
    - app.py: đầy là file triển khai Flask API, chứa những route, chạy server là chạy file này
    - closetPlus.py: file này chứa những phương thức logic cần thiết của thuật toán Closet+
    - requirement.txt: trong đây là các gói packages cần cài cho server, những gói nào đã có rồi thì bỏ qua
/frontend/ (Những phần quan trọng)
    - /components/
        + FileUploader.jsx: Chức năng Upload file csv, nhập những input và gọi API để lấy data
        + ResultDisplay.jsx: Nhận data và hiển thị kết quả
        + Visualizer.jsx: Nhận data và vẽ ra cây FP Tree
    - App.jsx: gọi 3 component từ folder components, data lấy được từ FileUploader sẽ gửi qua cho ResultDisplay và Visualizer
