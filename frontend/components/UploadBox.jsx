"use client";

export default function UploadBox({
  title,
  file,
  setFile,
}) {
  return (
    <div className="upload-box">
      <label>{title} (optional)</label>

      <div className="upload-inner">
        <div>
          <p className="upload-title">
            Drag and drop file here
          </p>

          <p className="upload-subtitle">
            Limit 200MB per file • DOCX, PDF, XLSX, TXT
          </p>
        </div>

        <input
          type="file"
          id={title}
          className="hidden-input"
          onChange={(e) =>
            setFile(e.target.files?.[0] || null)
          }
        />

        <label
          htmlFor={title}
          className="browse-btn"
        >
          Browse Files
        </label>
      </div>

      {file && (
        <p className="selected-file">
          Selected: {file.name}
        </p>
      )}
    </div>
  );
}
