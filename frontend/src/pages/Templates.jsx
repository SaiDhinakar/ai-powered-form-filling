import { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import useLocalStorage from '../hooks/useLocalStorage';
import DocumentPreview from '../components/DocumentPreview';
import Modal from '../components/Modal';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function Templates() {
  const [previewFile, setPreviewFile] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Upload Modal State
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [filesToUpload, setFilesToUpload] = useState([]);
  const [uploadLanguage, setUploadLanguage] = useState('en');

  const fileInputRef = useRef(null);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
  ];

  const fetchTemplates = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/templates/template');
      // Backend returns { templates: [...] }
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error("Failed to fetch templates", error);
      toast.error("Failed to load templates");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleFileSelection = (e) => {
    if (e.target.files) {
      setFilesToUpload(Array.from(e.target.files));
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (filesToUpload.length === 0) return;

    const toastId = toast.loading("Uploading templates...");
    try {
      for (const file of filesToUpload) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('lang', uploadLanguage); // Signature: create_template(file: UploadFile, lang: str = Form(None))

        await api.post('/templates/template', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        });
      }
      toast.success("Templates uploaded", { id: toastId });
      fetchTemplates();
    } catch (error) {
      console.error("Upload template error", error);
      toast.error("Failed to upload some templates", { id: toastId });
    } finally {
      setIsUploadModalOpen(false);
      setFilesToUpload([]);
      setUploadLanguage('en');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this template?")) return;
    try {
      // Signature: delete_template(template_id: int)
      // Standard DELETE usually passes params in query if simple arg
      await api.delete('/templates/template', {
        params: { template_id: id }
      });
      setTemplates(templates.filter((t) => t.id !== id));
      toast.success("Template deleted");
    } catch (error) {
      console.error("Delete template error", error);
      toast.error("Failed to delete template");
    }
  };

  // Kept for potential future editing
  const handleLanguageChange = (id, newLanguage) => {
    // api.put('/templates/template') exists but takes form data.
    // It's complicated to just update lang without re-uploading file logic in current backend logic (it expects File(None)).
    // I'll skip implementing this inline update for now to avoid complexity unless requested.
    toast.error("Updating language is not supported by backend yet.");
  };

  const formatSize = (bytes) => {
    if (!bytes) return 'N/A';
    return bytes < 1024 * 1024
      ? `${Math.round(bytes / 1024)} KB`
      : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (d) => {
    if (!d) return 'N/A';
    return new Date(d).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const handlePreview = async (templateId) => {
    // Calling preview_template endpoint which returns JSON { html, fields }
    try {
      const response = await api.get(`/templates/template/${templateId}/preview`);
      // We can't use the same DocumentPreview component easily because it expects a Blob/File object with type.
      // But we can construct a fake file object or adapt.
      // For now, let's just create a blob from the HTML content and show it.
      const htmlContent = response.data.html;
      const blob = new Blob([htmlContent], { type: 'text/html' });
      const fileUrl = URL.createObjectURL(blob);

      setPreviewFile({
        name: 'Preview.html',
        type: 'text/html',
        url: fileUrl
      });
    } catch (error) {
      toast.error("Failed to preview template");
    }
  };

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
            Upload and manage PDF or HTML templates used for automated form extraction.
          </p>
        </div>

        <button
          onClick={() => setIsUploadModalOpen(true)}
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

      {/* LOADING */}
      {isLoading && templates.length === 0 && (
        <div className="text-center py-20 text-[#64748B]">Loading templates...</div>
      )}

      {/* CONTENT */}
      {!isLoading && templates.length === 0 ? (
        <div className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-16 text-center">
          <p className="text-lg font-medium text-[#0F172A]">
            No templates uploaded
          </p>
          <p className="mt-3 text-[#64748B] max-w-md mx-auto">
            Upload PDF or HTML templates to define how documents are parsed and fields are extracted.
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
                    className="border-b border-[#F1F5F9] hover:bg-[#F8FAFC] transition cursor-pointer"
                    onClick={() => handlePreview(t.id)}
                  >
                    <td
                      className="px-8 py-5 text-sm font-medium text-[#0F172A]"
                    >
                      {t.name || t.filename || 'Template'}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {languages.find(l => l.code === t.lang)?.name || t.lang || 'English'}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {formatSize(t.size)}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {formatDate(t.created_at || t.uploadedAt)}
                    </td>
                    <td className="px-8 py-5 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(t.id);
                        }}
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

      {/* UPLOAD MODAL */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Template"
      >
        <form onSubmit={handleUploadSubmit}>
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Select Files
              </label>
              <input
                type="file"
                multiple
                accept=".pdf,.html"
                onChange={handleFileSelection}
                className="block w-full text-sm text-slate-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-[#EFF6FF] file:text-[#2563EB]
                  hover:file:bg-[#DBEAFE]
                "
              />
              {filesToUpload.length > 0 && (
                <div className="mt-2 text-sm text-[#475569]">
                  {filesToUpload.length} file(s) selected
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Template Language
              </label>
              <select
                className="input"
                value={uploadLanguage}
                onChange={(e) => setUploadLanguage(e.target.value)}
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={() => setIsUploadModalOpen(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={filesToUpload.length === 0}
            >
              Upload
            </button>
          </div>
        </form>
      </Modal>

      <DocumentPreview
        isOpen={!!previewFile}
        file={previewFile}
        onClose={() => setPreviewFile(null)}
      />
    </motion.div>
  );
}
