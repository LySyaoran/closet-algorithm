import React, { useState } from "react";
import axios from "axios";

function FileUploader({ onResult }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [decimalInput, setDecimalInput] = useState("");

  const handleDecimalInput = (e) => {
    const value = e.target.value;
    const decimalRegex = /^0+(\.[0-9]+)?$/;
    setDecimalInput(value);

    if (!decimalRegex.test(value)) {
      setError("Vui lòng nhập số thập phân hợp lệ.");
    } else {
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("minsup", decimalInput);

    try {
      const res = await axios.post("http://127.0.0.1:5000/upload", formData);
      onResult(res.data);
      console.log("Upload successful:", res.data);
    } catch (err) {
      console.error("Upload failed:", err);
    }
  };

  return (
    <div
      style={{
        maxWidth: "500px",
        margin: "20px auto",
        padding: "20px",
      }}
    >
      <h2 style={{ textAlign: "center" }}>Upload dữ liệu</h2>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        style={{
          display: "block",
          width: "100%",
          padding: "10px",
          margin: "10px 0",
          border: "1px solid #ccc",
          borderRadius: "4px",
          boxSizing: "border-box",
        }}
      />
      <hr
        style={{
          margin: "20px 0",
          border: "none",
          borderTop: "1px solid #ddd",
        }}
      />
      <input
        required
        type="text"
        placeholder="Nhập vào min sup VD: 0.3, 0.4, 0.5"
        title="Vui lòng nhập số thập phân."
        value={decimalInput}
        onChange={handleDecimalInput}
        style={{
          display: "block",
          width: "100%",
          padding: "10px",
          margin: "10px 0",
          border: "1px solid #ccc",
          borderRadius: "4px",
          boxSizing: "border-box",
        }}
      />
      {error && (
        <p style={{ color: "red", margin: "5px 0", fontSize: "14px" }}>
          {error}
        </p>
      )}
      <hr
        style={{
          margin: "20px 0",
          border: "none",
          borderTop: "1px solid #ddd",
        }}
      />
      <button
        onClick={handleUpload}
        disabled={!file || error || !decimalInput}
        style={{
          width: "100%",
          padding: "10px",
          backgroundColor: !file || error || !decimalInput ? "#ccc" : "#007bff",
          color: !file || error || !decimalInput ? "#666" : "white",
          border: "none",
          borderRadius: "4px",
          cursor: !file || error || !decimalInput ? "not-allowed" : "pointer",
          fontSize: "16px",
        }}
      >
        Chạy thuật toán
      </button>
    </div>
  );
}

export default FileUploader;
