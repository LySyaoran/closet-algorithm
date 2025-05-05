import React from "react";

function ResultDisplay({ result }) {
  if (!result || !Array.isArray(result.patterns)) return null;

  return (
    <div style={{ display: "flex", justifyContent: "center", padding: "20px" }}>
      <div
        style={{
          display: "flex",
          gap: "40px",
          width: "90%",
          alignItems: "stretch",
        }}
      >
        {/* CỘT TRÁI */}
        <div
          style={{
            flex: 1,
            backgroundColor: "#1c1c1c",
            color: "#fff",
            padding: "20px",
            borderRadius: "8px",
            display: "flex",
            flexDirection: "column",
            overflowY: "auto",
            maxHeight: "320px", // Chiều cao cố định hoặc bạn có thể để "100%" nếu cần toàn màn
          }}
        >
          <h4 style={{ borderBottom: "1px solid #444", paddingBottom: "10px" }}>
            Tập phổ biến đóng
          </h4>
          <ul style={{ paddingLeft: "20px", margin: 0 }}>
            {result.patterns.map((item, index) => (
              <li key={index} style={{ marginBottom: "8px" }}>
                {Array.isArray(item.pattern) ? item.pattern.join(", ") : "N/A"}{" "}
                - <strong>Support:</strong> {item.support}
              </li>
            ))}
          </ul>
        </div>

        {/* CỘT PHẢI */}
        <div
          style={{
            flex: 1,
            backgroundColor: "#1c1c1c",
            color: "#fff",
            padding: "20px",
            borderRadius: "8px",
            display: "flex",
            flexDirection: "column",
            overflowY: "auto",
            maxHeight: "320px", // Chiều cao cố định hoặc bạn có thể để "100%" nếu cần toàn màn
          }}
        >
          <h4 style={{ borderBottom: "1px solid #444", paddingBottom: "10px" }}>
            Luật kết hợp
          </h4>
          <ul style={{ paddingLeft: "20px", margin: 0 }}>
            {Array.isArray(result.association_rules) &&
              result.association_rules.map((rule, idx) => {
                const [antecedent, consequent] = rule.Rule
                  ? rule.Rule.split("=>").map((s) => s.trim())
                  : ["N/A", "N/A"];
                return (
                  <li key={idx} style={{ marginBottom: "8px" }}>
                    {antecedent} ⇒ {consequent} (confidence:{" "}
                    {typeof rule.Confidence === "number"
                      ? rule.Confidence.toFixed(2)
                      : "N/A"}
                    , lift:{" "}
                    {typeof rule.Lift === "number"
                      ? rule.Lift.toFixed(2)
                      : "N/A"}
                    , support:{" "}
                    {typeof rule.Support === "number"
                      ? rule.Support.toFixed(2)
                      : "N/A"}
                    )
                  </li>
                );
              })}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ResultDisplay;
