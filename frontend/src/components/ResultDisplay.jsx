import React from "react";

function ResultDisplay({ result }) {
  return (
    <div>
      <h3>Kết quả</h3>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
}

export default ResultDisplay;
