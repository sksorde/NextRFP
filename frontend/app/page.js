"use client";

import { useState } from "react";
import { runEnterpriseReview } from "../lib/api";

import BuildRefreshIndexButton from "../components/BuildRefreshIndexButton";
import ExecutiveSummaryCard from "../components/ExecutiveSummaryCard";
import ComplianceMatrix from "../components/ComplianceMatrix";
import RiskHeatmap from "../components/RiskHeatmap";
import ReviewerPanel from "../components/ReviewerPanel";
import KnowledgeEvidencePanel from "../components/KnowledgeEvidencePanel";
import UploadBox from "../components/UploadBox";

export default function Page() {
  const [rfpFile, setRfpFile] = useState(null);
  const [responseFile, setResponseFile] = useState(null);

  const [rfpText, setRfpText] = useState("");
  const [responseText, setResponseText] = useState("");

  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState(null);
  const [guidance, setGuidance] = useState([]);
  const [loading, setLoading] = useState(false);

  const [docsPath, setDocsPath] = useState(
    process.env.NEXT_PUBLIC_DEFAULT_DOCS_PATH || ""
  );

  const runReview = async () => {
    if ((!rfpFile && !rfpText) || (!responseFile && !responseText)) {
      alert("Provide both RFP & Response");
      return;
    }

    setLoading(true);

    try {
      const data = await runEnterpriseReview({
        rfp: rfpFile,
        response: responseFile,
        rfpText,
        responseText,
        chunkSizeTokens: 2500,
        overlapTokens: 500,
        topKChunks: 10,
      });

      setResults(data.results || []);
      setSummary(data.executive_summary || null);
      setGuidance(data.review_guidance || []);
    } catch (err) {
      alert(err.message);
    }

    setLoading(false);
  };

  return (
    <div className="app-wrapper">
      <div className="dashboard">

        {/* SIDEBAR */}
        <aside className="sidebar">
          <h2>Bid Repository</h2>

          <p className="sidebar-text">
            AI-powered RFP compliance, scoring, and proposal intelligence platform.
          </p>

          <div className="input-group">
            <label>Knowledge Base Path</label>
            <input
              type="text"
              value={docsPath}
              onChange={(e) => setDocsPath(e.target.value)}
              placeholder="Enter documents folder path"
            />
          </div>

          <div className="refresh-box">
            <BuildRefreshIndexButton docsPath={docsPath} />
          </div>
        </aside>

        {/* MAIN CONTENT */}
        <main className="main-content">
          <h1>Enterprise RFP Review</h1>

          <p className="subtitle">
            Upload your RFP and response to generate compliance analysis,
            Shipley scoring, and recommendations.
          </p>

          {/* FILE UPLOAD */}
          <div className="content-grid">

            <div>
              <UploadBox
                title="RFP Document"
                file={rfpFile}
                setFile={setRfpFile}
              />

              <textarea
                className="text-area"
                placeholder="Or paste RFP text..."
                value={rfpText}
                onChange={(e) => setRfpText(e.target.value)}
              />
            </div>

            <div>
              <UploadBox
                title="Response Document"
                file={responseFile}
                setFile={setResponseFile}
              />

              <textarea
                className="text-area"
                placeholder="Or paste response text..."
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
              />
            </div>

          </div>

          {/* RUN BUTTON */}
          <div className="run-section">
            <button
              className="run-btn"
              onClick={runReview}
              disabled={loading}
            >
              {loading
                ? "Running AI Review..."
                : "Run Full Analysis"}
            </button>
          </div>

          {/* RESULTS */}
          {summary && <ExecutiveSummaryCard summary={summary} />}
          {results.length > 0 && <ComplianceMatrix results={results} />}
          {results.length > 0 && <RiskHeatmap results={results} />}
          {guidance.length > 0 && <ReviewerPanel recommendations={guidance} />}
          {results.length > 0 && <KnowledgeEvidencePanel results={results} />}
        </main>

      </div>
    </div>
  );
}