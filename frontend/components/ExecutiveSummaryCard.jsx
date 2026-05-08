// frontend/src/components/ExecutiveSummaryCard.jsx

"use client";

export default function ExecutiveSummaryCard({ summary }) {
  if (!summary) return null;

  const {
    total_requirements = 0,
    compliant = 0,
    partial = 0,
    not_addressed = 0,
    average_shipley_score = 0,
    win_probability = 0,
    proposal_strength = "Unknown",
    overall_risk = "Medium",
    executive_recommendation = "No recommendation available"
  } = summary;

  const getRiskColor = (risk) => {
    if (risk === "Low") return "#16a34a";
    if (risk === "Medium") return "#d97706";
    return "#dc2626";
  };

  const getStrengthColor = (strength) => {
    if (strength === "Strong") return "#16a34a";
    if (strength === "Moderate") return "#d97706";
    return "#dc2626";
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
        Executive Summary Dashboard
      </h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "20px",
          marginBottom: "30px"
        }}
      >
        <MetricCard
          title="Shipley Score"
          value={`${average_shipley_score}%`}
        />

        <MetricCard
          title="Win Probability"
          value={`${win_probability}%`}
        />

        <MetricCard
          title="Total Requirements"
          value={total_requirements}
        />

        <MetricCard
          title="Coverage"
          value={`${(
            ((compliant + partial) /
              (total_requirements || 1)) *
            100
          ).toFixed(1)}%`}
        />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "30px"
        }}
      >
        {/* LEFT PANEL */}
        <div>
          <h3 style={{ marginBottom: "14px" }}>
            Proposal Health
          </h3>

          <div
            style={{
              lineHeight: "2",
              color: "#444"
            }}
          >
            <div>
              ✅ Compliant: <strong>{compliant}</strong>
            </div>

            <div>
              ⚠️ Partial: <strong>{partial}</strong>
            </div>

            <div>
              ❌ Not Addressed: <strong>{not_addressed}</strong>
            </div>

            <div>
              Proposal Strength:{" "}
              <strong
                style={{
                  color: getStrengthColor(
                    proposal_strength
                  )
                }}
              >
                {proposal_strength}
              </strong>
            </div>

            <div>
              Overall Risk:{" "}
              <strong
                style={{
                  color: getRiskColor(
                    overall_risk
                  )
                }}
              >
                {overall_risk}
              </strong>
            </div>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div>
          <h3 style={{ marginBottom: "14px" }}>
            Executive Recommendation
          </h3>

          <div
            style={{
              background: "#f8fafc",
              padding: "18px",
              borderRadius: "12px",
              border: "1px solid #e5e7eb",
              lineHeight: "1.8",
              color: "#444"
            }}
          >
            {executive_recommendation}
          </div>
        </div>
      </div>
    </div>
  );
}


/* =========================================
   REUSABLE METRIC CARD
========================================= */

function MetricCard({ title, value }) {
  return (
    <div
      style={{
        background: "#f8fafc",
        border: "1px solid #e5e7eb",
        borderRadius: "14px",
        padding: "20px"
      }}
    >
      <div
        style={{
          fontSize: "14px",
          color: "#666",
          marginBottom: "8px"
        }}
      >
        {title}
      </div>

      <div
        style={{
          fontSize: "30px",
          fontWeight: "700"
        }}
      >
        {value}
      </div>
    </div>
  );
}

ExecutiveSummaryCard;