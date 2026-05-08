const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

/* ================================
   REFRESH KB
================================ */
export async function buildRefreshIndex({
  docsPath,
  chunkSizeTokens = 2500,
  overlapTokens = 500,
}) {
  const formData = new FormData();

  formData.append("docs_path", docsPath);
  formData.append("chunk_size_tokens", chunkSizeTokens);
  formData.append("overlap_tokens", overlapTokens);

  const res = await fetch(`${BASE_URL}/build-refresh-index`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function refreshKnowledgeBase({
  docsPath,
  chunkSizeTokens = 1000,
  overlapTokens = 200,
}) {
  const formData = new FormData();

  formData.append("docs_path", docsPath);
  formData.append("chunk_size_tokens", chunkSizeTokens);
  formData.append("overlap_tokens", overlapTokens);

  const res = await fetch(`${BASE_URL}/build-refresh-index`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.error || "KB refresh failed");
  }

  console.log("KB Response:", data);
  return data;
}

/* ================================
   ENTERPRISE REVIEW
================================ */
export async function runEnterpriseReview(payload) {
  const formData = new FormData();

  const {
    rfp,
    response,
    rfpText,
    responseText,
    chunkSizeTokens,
    overlapTokens,
    topKChunks,
  } = payload;

  if (rfp) formData.append("rfp", rfp);
  else if (rfpText) formData.append("rfp_text", rfpText);

  if (response) formData.append("response", response);
  else if (responseText) formData.append("response_text", responseText);

  formData.append("chunk_size_tokens", chunkSizeTokens);
  formData.append("overlap_tokens", overlapTokens);
  formData.append("top_k_chunks", topKChunks);

  const res = await fetch(`${BASE_URL}/review`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}