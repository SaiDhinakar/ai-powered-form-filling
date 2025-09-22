import React, { useState } from "react";

export default function FileUpload() {
  const [fileName, setFileName] = useState("");

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFileName(e.target.files[0].name);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <label className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow cursor-pointer hover:bg-blue-700">
        Choose File
        <input
          type="file"
          className="hidden"
          onChange={handleFileChange}
        />
      </label>
      {fileName && (
        <p className="mt-4 text-gray-700 font-medium">Uploaded: {fileName}</p>
      )}
    </div>
  );
}
