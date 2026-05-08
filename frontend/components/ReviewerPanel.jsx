// frontend/src/components/ReviewerPanel.jsx

"use client";

export default function ReviewerPanel({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

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
        Reviewer Guidance Panel
      </h2>

      <p
        style={{
          color: "#666",
          marginBottom: "24px",
          lineHeight: "1.7"
        }}
      >
        Enterprise reviewer recommendations generated
        using compliance findings, Shipley scoring,
        evidence traceability, and proposal gap analysis.
      </p>

      <div
        style={{
          display: "grid",
          gap: "18px"
        }}
      >
        {recommendations.map((item, index) => (
          <div
            key={index}
            style={{
              background: "#f8fafc",
              border: "1px solid #e5e7eb",
              borderRadius: "14px",
              padding: "20px"
            }}
          >
            <div
              style={{
                display: "flex",
                gap: "14px",
                alignItems: "flex-start"
              }}
            >
              <div
                style={{
                  fontSize: "22px"
                }}
              >
                {getPriorityIcon(
                  item.priority
                )}
              </div>

              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontWeight: "700",
                    marginBottom: "8px"
                  }}
                >
                  {item.title ||
                    "Recommendation"}
                </div>

                <div
                  style={{
                    color: "#444",
                    lineHeight: "1.8",
                    marginBottom: "10px"
                  }}
                >
                  {item.description ||
                    item.message}
                </div>

                <div
                  style={{
                    display: "flex",
                    gap: "16px",
                    fontSize: "14px",
                    color: "#666"
                  }}
                >
                  <span>
                    Priority:{" "}
                    <strong>
                      {item.priority ||
                        "Medium"}
                    </strong>
                  </span>

                  <span>
                    Impact:{" "}
                    <strong>
                      {item.impact ||
                        "Moderate"}
                    </strong>
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


/* =========================================
   PRIORITY ICON
========================================= */

function getPriorityIcon(priority) {
  if (!priority) return "📌";

  const value =
    priority.toLowerCase();

  if (value.includes("high")) {
    return "🔴";
  }

  if (value.includes("medium")) {
    return "🟠";
  }

  if (value.includes("low")) {
    return "🟢";
  }

  return "📌";
}

ReviewerPanel;