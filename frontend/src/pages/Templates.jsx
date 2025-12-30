import { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import DocumentPreview from '../components/DocumentPreview';
import LanguageAssignmentModal from '../components/LanguageAssignmentModal';
import api from '../services/api';
import { toast } from 'react-hot-toast';

export default function Templates() {
  const [previewFile, setPreviewFile] = useState(null);
  const [templates, setTemplates] = useState([]);
  const fileInputRef = useRef(null);

  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState(false);
  const [pendingFiles, setPendingFiles] = useState([]);

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/templates/template');
      // response.data.templates based on router code
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
      toast.error('Failed to load templates');
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    setPendingFiles(files);
    setIsLanguageModalOpen(true);
    e.target.value = ''; // Reset input
  };

  const handleLanguageConfirm = async (assignments) => {
    const uploadPromise = Promise.all(pendingFiles.map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      const lang = assignments[file.name] || 'en';
      formData.append('lang', lang);

      return api.post('/templates/template', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    }));

    toast.promise(uploadPromise, {
      loading: 'Uploading templates...',
      success: 'Templates uploaded',
      error: 'Failed to upload templates'
    }).then(() => {
      setPendingFiles([]);
      setIsLanguageModalOpen(false);
      fetchTemplates();
    }).catch(err => console.error(err));
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure you want to delete this template?")) return;
    try {
      await api.delete(`/templates/template?template_id=${id}`);
      toast.success('Template deleted');
      fetchTemplates();
    } catch (error) {
      console.error(error);
      toast.error('Failed to delete template');
    }
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
                      {t.path ? t.path.split('/').pop() : 'Unnamed'}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {t.lang || '-'}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {/* Size might not be in DB response, showing placeholder or calculating if available */}
                      -
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {formatDate(t.created_at)}
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
