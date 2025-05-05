import React from "react";
import { Tree } from "react-d3-tree";
import { ResponsiveContainer } from "recharts";

function Visualizer({ data }) {
  console.log("Data received in Visualizer:", data);
  if (!data || !data.tree) return null;

  // Chuyển đổi node thành dạng phù hợp với react-d3-tree
  const transformTreeData = (node) => {
    return {
      name: node.item === null ? "Root" : node.item,
      attributes: {
        count: node.count,
      },
      children: node.children?.map(transformTreeData) || [],
    };
  };

  const treeData = transformTreeData(data.tree);

  return (
    <div
      style={{
        width: "90%",
        height: "100vh",
        backgroundColor: "white",
        position: "relative",
        margin: "0 auto",
      }}
    >
      <h3
        style={{
          color: "black",
          textAlign: "center",
          padding: "20px",
          margin: 0,
        }}
      >
        FP-Tree Visualization
      </h3>

      <div
        style={{
          width: "100%",
          height: "calc(100% - 80px)",
          padding: "20px",
        }}
      >
        <ResponsiveContainer>
          <Tree
            data={treeData}
            orientation="vertical"
            translate={{ x: 600, y: 50 }}
            pathFunc="step"
            separation={{ siblings: 1.5, nonSiblings: 2 }}
            styles={{
              links: {
                stroke: "#ccc",
                strokeWidth: 1,
              },
            }}
            renderCustomNodeElement={({ nodeDatum }) => (
              <g>
                <circle
                  r={nodeDatum.name === "Root" ? 10 : 15}
                  fill={nodeDatum.name === "Root" ? "transparent" : "black"}
                  stroke="black"
                  strokeWidth={2}
                />
                <text fill="black" x={20} y={5} fontSize={20} strokeWidth={0}>
                  {nodeDatum.name}
                  {nodeDatum.attributes?.count !== undefined &&
                    ` (${nodeDatum.attributes.count})`}
                </text>
              </g>
            )}
          />
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Visualizer;