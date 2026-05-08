// frontend/src/components/RiskHeatmap.jsx

"use client";

export default function RiskHeatmap({ results }) {
  if (!results || results.length === 0) return null;

  const compliant = results.filter(
    (r) => r.status === "COMPLIANT"
  ).length;

  const partial = results.filter(
    (r) => r.status === "PARTIAL"
  ).length;

  const notAddressed = results.filter(
    (r) => r.status === "NOT ADDRESSED"
  ).length;

  const total = results.length || 1;

  const compliantPercent = (
    (compliant / total) * 100
  ).toFixed(1);

  const partialPercent = (
    (partial / total) * 100
  ).toFixed(1);

  const riskPercent = (
    (notAddressed / total) * 100
  ).toFixed(1);

  const overallRisk =
    riskPercent >= 40
      ? "HIGH RISK"
      : riskPercent >= 20
      ? "MEDIUM RISK"
      : "LOW RISK";

  const overallRiskColor =
    overallRisk === "HIGH RISK"
      ? "#dc2626"
      : overallRisk === "MEDIUM RISK"
      ? "#d97706"
      : "#16a34a";

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
        Risk Heatmap
      </h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "30px"
        }}
      >
        {/* LEFT PANEL */}
        <div>
          <RiskBar
            label="Green Zone (Compliant)"
            value={compliantPercent}
            color="#16a34a"
          />

          <RiskBar
            label="Amber Zone (Partial)"
            value={partialPercent}
            color="#d97706"
          />

          <RiskBar
            label="Red Zone (Not Addressed)"
            value={riskPercent}
            color="#dc2626"
          />
        </div>

        {/* RIGHT PANEL */}
        <div
          style={{
            background: "#f8fafc",
            border: "1px solid #e5e7eb",
            borderRadius: "14px",
            padding: "24px"
          }}
        >
          <div
            style={{
              fontSize: "14px",
              color: "#666",
              marginBottom: "10px"
            }}
          >
            Overall Proposal Risk
          </div>

          <div
            style={{
              fontSize: "28px",
              fontWeight: "700",
              color: overallRiskColor,
              marginBottom: "20px"
            }}
          >
            {overallRisk}
          </div>

          <div
            style={{
              lineHeight: "1.8",
              color: "#444",
              fontSize: "14px"
            }}
          >
            <div>
              High compliance reduces bid risk
              and improves evaluator confidence.
            </div>

            <div style={{ marginTop: "12px" }}>
              Red-zone requirements should be
              fixed before submission.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


/* =========================================
   RISK BAR
========================================= */

function RiskBar({
  label,
  value,
  color
}) {
  return (
    <div
      style={{
        marginBottom: "24px"
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: "8px",
          fontWeight: "600"
        }}
      >
        <span>{label}</span>
        <span>{value}%</span>
      </div>

      <div
        style={{
          width: "100%",
          height: "14px",
          background: "#f1f5f9",
          borderRadius: "999px",
          overflow: "hidden"
        }}
      >
        <div
          style={{
            width: `${value}%`,
            height: "100%",
            background: color,
            borderRadius: "999px"
          }}
        />
      </div>
    </div>
  );
}

RiskHeatmap;