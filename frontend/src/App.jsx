import React, { useState } from "react";
import FileUploader from "./components/FileUploader";
import ResultDisplay from "./components/ResultDisplay";
import Visualizer from "./components/Visualizer";

function App() {
  const [data, setData] = useState(null);

  return (
    <div style={{paddingLeft: 20}}>
      <h1>Thuật toán CLOSET+</h1>
      <FileUploader onResult={setData} />
      {data && (
        <>
          <ResultDisplay result={data.result} />
          <Visualizer steps={data.steps} />
        </>
      )}
    </div>
  );
}

export default App;
