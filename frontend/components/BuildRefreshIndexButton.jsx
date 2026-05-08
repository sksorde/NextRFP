"use client";

import { useState } from "react";
import { refreshKnowledgeBase } from "../lib/api";

export default function BuildRefreshIndexButton({ docsPath }) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const handleRefresh = async () => {
    if (!docsPath) {
      alert("Please provide knowledge base path");
      return;
    }

    setLoading(true);
    setStatus("Building knowledge base...");

    try {
      const res = await refreshKnowledgeBase({
        docsPath,
        chunkSizeTokens: 500,
        overlapTokens: 200,
      });

      console.log("KB REFRESH RESPONSE:", res);

      if (res.error) {
        alert("❌ Failed: " + res.error);
      } else {
        console.log("STDOUT:", res.stdout);
        console.log("STDERR (info logs):", res.stderr);

        alert("✅ Knowledge Base refreshed successfully");
      }

      setStatus(
        res?.status === "success"
          ? "Knowledge base built successfully ✅"
          : "Completed with warnings ⚠️"
      );
    } catch (err) {
      console.error(err);
      setStatus("Failed ❌" + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="refresh-box">
      <button
        className="refresh-btn"
        onClick={handleRefresh}
        disabled={loading}
      >
        {loading ? "Building..." : "Build / Refresh KB"}
      </button>

      {status && <p style={{ marginTop: "10px" }}>{status}</p>}
    </div>
  );
}