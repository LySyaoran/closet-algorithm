import React, { useEffect, useState } from "react";
import FileUploader from "./components/FileUploader";
import ResultDisplay from "./components/ResultDisplay";
import Visualizer from "./components/Visualizer";
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    if (data) {
      setAnimate(true);
    }
  }, [data]);

  return (
    <div>
      {/* Tiêu đề */}
      <div style={{ display: "flex", justifyContent: "center", marginTop: 20 }}>
        <h1>Thuật toán CLOSET+</h1>
      </div>

      {/* Bố cục động */}
      <div className={`main-container ${animate ? "with-data" : "no-data"}`}>
        {/* Cột trái */}
        <div className={`left-panel ${animate ? "left-3" : "full-width"}`}>
          <FileUploader onResult={setData} />
        </div>

        {/* Cột phải */}
        {data && (
          <div className="right-panel slide-in">
            <ResultDisplay result={data} />
            {/* <Visualizer steps={data.patterns} /> */}
          </div>
        )}
      </div>

      {data && <Visualizer steps={data.patterns} />}
    </div>
  );
}

export default App;
