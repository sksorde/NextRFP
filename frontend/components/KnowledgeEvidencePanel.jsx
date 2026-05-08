// frontend/src/components/KnowledgeEvidencePanel.jsx

"use client";

export default function KnowledgeEvidencePanel({ results }) {
  if (!results || results.length === 0) {
    return null;
  }

  const flattenedEvidence = [];

  results.forEach((item) => {
    (item.evidence || []).forEach((ev) => {
      flattenedEvidence.push({
        requirement: item.requirement,
        source: ev.source || "Unknown Source",
        category: ev.category || "General",
        content: ev.content || ""
      });
    });
  });

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
        Knowledge Evidence Traceability
      </h2>

      <p
        style={{
          color: "#666",
          marginBottom: "24px",
          lineHeight: "1.7"
        }}
      >
        This section shows which knowledge base files,
        chunks, and evidence were used during compliance
        evaluation and Shipley scoring decisions.
      </p>

      <div
        style={{
          display: "grid",
          gap: "18px"
        }}
      >
        {flattenedEvidence.length === 0 ? (
          <div
            style={{
              background: "#f8fafc",
              padding: "20px",
              borderRadius: "12px",
              border: "1px solid #e5e7eb"
            }}
          >
            No evidence retrieved from knowledge base.
          </div>
        ) : (
          flattenedEvidence.map((item, index) => (
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
                  fontWeight: "700",
                  marginBottom: "10px"
                }}
              >
                Requirement:
              </div>

              <div
                style={{
                  marginBottom: "16px",
                  lineHeight: "1.7",
                  color: "#333"
                }}
              >
                {item.requirement}
              </div>

              <div
                style={{
                  display: "flex",
                  gap: "24px",
                  marginBottom: "14px",
                  fontSize: "14px",
                  color: "#555"
                }}
              >
                <div>
                  <strong>Source File:</strong>{" "}
                  {item.source}
                </div>

                <div>
                  <strong>Category:</strong>{" "}
                  {item.category}
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  padding: "16px",
                  borderRadius: "10px",
                  border: "1px solid #dbeafe",
                  fontSize: "14px",
                  lineHeight: "1.8",
                  color: "#444"
                }}
              >
                {item.content.slice(0, 600)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

KnowledgeEvidencePanel;