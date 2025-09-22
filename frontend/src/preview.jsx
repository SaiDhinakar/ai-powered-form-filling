import React, { useState } from "react";
import "./preview.css";

export default function Preview() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [showPreview, setShowPreview] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setShowPreview(false);
  };

  const handlePreview = () => {
    if (!file) {
      alert("Please upload a file first!");
      return;
    }

    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setShowPreview(true);
  };

  const hidePreview = () => {
    setShowPreview(false);
  };

  return (
    <div className="preview-container">
      <input type="file" accept="image/*,.pdf" onChange={handleFileChange} />

      <button onClick={handlePreview}>Preview</button>

      {showPreview && previewUrl && (
        <>
          <div className="preview-toggle">
            <span onClick={hidePreview} className="toggle-btn">
              ▲ Hide Preview
            </span>
          </div>

          <div className="preview-box">
            {file.type === "application/pdf" ? (
              <iframe
                src={previewUrl}
                title="PDF Preview"
                className="pdf-preview"
              />
            ) : (
              <img src={previewUrl} alt="Preview" className="img-preview" />
            )}
          </div>
        </>
      )}
    </div>
  );
}
