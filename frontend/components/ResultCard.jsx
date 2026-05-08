"use client";

import React from "react";
import ExecutiveSummaryCard from "./ExecutiveSummaryCard";
import RiskHeatmap from "./RiskHeatmap";
import ComplianceMatrix from "./ComplianceMatrix";
import ReviewerPanel from "./ReviewerPanel";
import KnowledgeEvidencePanel from "./KnowledgeEvidencePanel";

export default function ResultCard({ data }) {
  // Guard clause if no valid data is passed
  if (!data || (!data.results && !data.executive_summary)) return null;

  const results = data.results || [];
  const summary = data.executive_summary || null;

  // We map the backend requirement results into reviewer recommendations
  // targeting anything that is not fully compliant.
  const derivedRecommendations = results
    .filter(r => r.status !== "COMPLIANT" && r.recommendation)
    .map((r) => ({
      title: `Gap Identified: ${r.requirement.slice(0, 40)}...`,
      description: r.recommendation,
      priority: r.status === "NOT ADDRESSED" ? "High" : "Medium",
      impact: (r.shipley_score || 0) < 50 ? "High" : "Moderate"
    }));

  return (
    <div className="dashboard-container" style={{ marginTop: "40px" }}>
      {/* 1. Top Level Metrics */}
      <ExecutiveSummaryCard summary={summary} />

      {/* 2. Visual Risk Assessment */}
      <RiskHeatmap results={results} />

      {/* 3. Actionable Reviewer Panel (Only shows if gaps exist) */}
      <ReviewerPanel recommendations={derivedRecommendations} />

      {/* 4. The Core Checklist / Matrix */}
      <ComplianceMatrix results={results} />

      {/* 5. Traceability & Source Evidence */}
      <KnowledgeEvidencePanel results={results} />
    </div>
  );
}

ResultCard;