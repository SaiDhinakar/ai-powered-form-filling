import { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useLocalStorage from '../hooks/useLocalStorage';
import DocumentPreview from '../components/DocumentPreview';
import LanguageAssignmentModal from '../components/LanguageAssignmentModal';

export default function Templates() {
  const [previewFile, setPreviewFile] = useState(null);
  const [templates, setTemplates] = useLocalStorage('templates', []);
  const fileInputRef = useRef(null);

  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState(false);
  const [pendingFiles, setPendingFiles] = useState([]);

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    setPendingFiles(files);
    setIsLanguageModalOpen(true);
    e.target.value = ''; // Reset input
  };

  const handleLanguageConfirm = (assignments) => {
    const newTemplates = pendingFiles.map((file) => ({
      id: Date.now() + Math.random(),
      name: file.name,
      type: file.type,
      size: file.size,
      language: assignments[file.name],
      uploadedAt: new Date().toISOString(),
      url: URL.createObjectURL(file), // Note: In a real app this would be an S3 URL or similar
    }));
    setTemplates([...templates, ...newTemplates]);
    setPendingFiles([]);
    setIsLanguageModalOpen(false);
  };

  const handleDelete = (id) => {
    // Revoke blob URL to free memory
    const templateToDelete = templates.find((t) => t.id === id);
    if (templateToDelete?.url && templateToDelete.url.startsWith('blob:')) {
      URL.revokeObjectURL(templateToDelete.url);
    }

    setTemplates(templates.filter((t) => t.id !== id));
  };

  const formatSize = (bytes) =>
    bytes < 1024 * 1024
      ? `${Math.round(bytes / 1024)} KB`
      : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

  const formatDate = (d) =>
    new Date(d).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });

  return (
    <motion.div
      className="min-h-screen bg-[#ECEFF3] px-10 py-10"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.35 }}
    >
      {/* HEADER */}
      <header className="flex items-start justify-between mb-14">
        <div>
          <h1 className="text-4xl font-semibold text-[#0F172A]">
            Templates
          </h1>
          <p className="mt-3 text-lg text-[#475569] max-w-2xl">
            Upload and manage PDF templates used for automated form extraction.
          </p>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={handleFileUpload}
          className="hidden"
        />

        <button
          onClick={() => fileInputRef.current?.click()}
          className="
            px-5 py-3
            rounded-xl
            bg-[#2563EB]
            text-white
            font-medium
            hover:bg-[#1D4ED8]
            transition
          "
        >
          Upload template
        </button>
      </header>

      {/* CONTENT */}
      {templates.length === 0 ? (
        <div className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-16 text-center">
          <p className="text-lg font-medium text-[#0F172A]">
            No templates uploaded
          </p>
          <p className="mt-3 text-[#64748B] max-w-md mx-auto">
            Upload PDF templates to define how documents are parsed and fields are extracted.
          </p>
        </div>
      ) : (
        <motion.div
          className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl overflow-hidden"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <table className="w-full">
            <thead className="border-b border-[#E6E8EB]">
              <tr>
                <th className="text-left px-8 py-4 text-sm font-medium text-[#475569]">
                  Name
                </th>
                <th className="text-left px-8 py-4 text-sm font-medium text-[#475569]">
                  Language
                </th>
                <th className="text-left px-8 py-4 text-sm font-medium text-[#475569]">
                  Size
                </th>
                <th className="text-left px-8 py-4 text-sm font-medium text-[#475569]">
                  Uploaded
                </th>
                <th className="px-8 py-4"></th>
              </tr>
            </thead>

            <tbody>
              <AnimatePresence>
                {templates.map((t) => (
                  <motion.tr
                    key={t.id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="border-b border-[#F1F5F9] hover:bg-[#F8FAFC] transition"
                  >
                    <td
                      className="px-8 py-5 text-sm font-medium text-[#0F172A]"
                    >
                      {t.name}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {t.language || '-'}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {formatSize(t.size)}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {formatDate(t.uploadedAt)}
                    </td>
                    <td className="px-8 py-5 text-right">
                      <button
                        onClick={() => handleDelete(t.id)}
                        className="
                          text-sm
                          text-[#64748B]
                          hover:text-[#B91C1C]
                          transition
                        "
                      >
                        Remove
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </motion.div>
      )}

      <LanguageAssignmentModal
        isOpen={isLanguageModalOpen}
        onClose={() => setIsLanguageModalOpen(false)}
        files={pendingFiles}
        onConfirm={handleLanguageConfirm}
      />

      <DocumentPreview
        isOpen={!!previewFile}
        file={previewFile}
        onClose={() => setPreviewFile(null)}
      />
    </motion.div>
  );
}
