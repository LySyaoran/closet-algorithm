import React from "react";
import { Tree } from "react-d3-tree";
import { ResponsiveContainer } from "recharts";

function Visualizer({ steps }) {
  if (!steps || !Array.isArray(steps)) return null;

  const transformData = (steps) => {
    const root = {
      name: "Root",
      children: [],
    };

    steps.forEach((item, index) => {
      const parentNode = {
        name: Array.isArray(item.pattern)
          ? item.pattern.join(", ")
          : `Pattern ${index + 1}`,
        support: item.support,
        children: item.pattern.map((pattern) => ({
          name: `${pattern} (Support: ${item.support})`,
          support: item.support,
        })),
      };
      root.children.push(parentNode);
    });

    return root;
  };

  const treeData = transformData(steps);

  return (
    <div style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
      <h3 style={{ color: "white", textAlign: "center", marginTop: 20 }}>
        Biểu đồ Cây theo Pattern
      </h3>
      <div style={{ width: "90%", height: 500, backgroundColor: "white" }}>
        <ResponsiveContainer>
          <div style={{ width: "100%", height: "100%" }}>
            <Tree
              data={treeData}
              translate={{ x: 50, y: 250 }}
              pathFunc="step"
              orientation="vertical"
              styles={{
                links: {
                  stroke: "black", // Màu đường liên kết
                  strokeWidth: 2, // Độ dày đường liên kết
                },
                nodes: {
                  node: {
                    circle: {
                      fill: "black", // Màu của node
                      stroke: "black",
                      strokeWidth: 2,
                    },
                  },
                  name: {
                    stroke: "none",
                    fill: "black", // Màu của tên node
                    fontSize: 12,
                  },
                },
              }}
              renderCustomNodeElement={({ nodeDatum, toggleNode }) => (
                <g>
                  {/* Node hình tròn màu trắng */}
                  <circle
                    cx="0"
                    cy="0"
                    r="15"
                    fill="black"
                    onClick={toggleNode}
                  />

                  {/* Tên pattern màu trắng */}
                  <text
                    fill="black"
                    x="20"
                    y="5"
                    fontSize={12}
                    stroke="none"
                    style={{ userSelect: "none" }}
                  >
                    {nodeDatum.name}
                  </text>
                </g>
              )}
            />
          </div>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Visualizer;
