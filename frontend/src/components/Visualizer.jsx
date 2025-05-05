import React from "react";

function Visualizer({ steps }) {
  return (
    <div>
      <h3>Visualization các bước</h3>
      {steps.map((step, i) => (
        <div key={i}>
          <strong>Bước {i + 1}:</strong>
          <pre>{JSON.stringify(step, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}

export default Visualizer;
