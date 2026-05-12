// frontend/src/components/ComplianceMatrix.jsx
"use client";

export default function ComplianceMatrix({ results }) {
  if (!results || results.length === 0) return null;

  const getStatusColor = (status) => {
    if (status === "COMPLIANT") return "#16a34a";
    if (status === "PARTIAL") return "#d97706";
    if (status === "NOT ADDRESSED") return "#dc2626";
    return "#6b7280";
  };

  const getStatusBadge = (status) => {
    if (status === "COMPLIANT") return "✅";
    if (status === "PARTIAL") return "⚠️";
    if (status === "NOT ADDRESSED") return "❌";
    return "•";
  };

  return (
    <div
      style={{
        background: "#ffffff",
        borderRadius: "16px",
        padding: "30px",
        border: "1px solid #e5e7eb",
        marginTop: "30px"
      }}
    >
      <h2 style={{ marginBottom: "24px" }}>
        Compliance Matrix
      </h2>

      <div
        style={{
          overflowX: "auto"
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse"
          }}
        >
          <thead>
            <tr
              style={{
                background: "#f8fafc",
                textAlign: "left"
              }}
            >
              <th style={thStyle}>Requirement</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Shipley Score</th>
              <th style={thStyle}>Proposal Confidence</th>
              <th style={thStyle}>Recommendation</th>
            </tr>
          </thead>

          <tbody>
            {results.map((item, index) => (
              <tr
                key={index}
                style={{
                  borderBottom:
                    "1px solid #e5e7eb"
                }}
              >
                <td style={tdStyle}>
                  <div
                    style={{
                      fontWeight: "600",
                      marginBottom: "8px"
                    }}
                  >
                    {item.requirement}
                  </div>

                  <div
                    style={{
                      fontSize: "13px",
                      color: "#666",
                      lineHeight: "1.6"
                    }}
                  >
                    {item.explanation}
                  </div>
                </td>

                <td style={tdStyle}>
                  <div
                    style={{
                      color: getStatusColor(
                        item.status
                      ),
                      fontWeight: "700"
                    }}
                  >
                    {getStatusBadge(
                      item.status
                    )}{" "}
                    {item.status}
                  </div>
                </td>

                <td style={tdStyle}>
                  <strong>
                    {item.shipley_score || 0}%
                  </strong>
                </td>

                <td style={tdStyle}>
                  <strong>
                    {item.confidence || 0}%
                  </strong>
                </td>

                <td style={tdStyle}>
                  <div
                    style={{
                      fontSize: "14px",
                      lineHeight: "1.7",
                      color: "#444"
                    }}
                  >
                    {item.recommendation}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


/* =========================================
   TABLE STYLES
========================================= */

const thStyle = {
  padding: "16px",
  fontSize: "14px",
  fontWeight: "700",
  borderBottom: "1px solid #e5e7eb"
};

const tdStyle = {
  padding: "18px 16px",
  verticalAlign: "top"
};

ComplianceMatrix;