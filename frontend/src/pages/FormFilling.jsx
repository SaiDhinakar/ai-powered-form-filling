import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, CaretDown, CaretUp, X, Download, FileHtml, Eye } from 'phosphor-react';
import toast from 'react-hot-toast';
import api from '../services/api';

export default function FormFilling() {
  const [entities, setEntities] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [recentForms, setRecentForms] = useState([]);

  const [selectedEntityId, setSelectedEntityId] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [filledResult, setFilledResult] = useState(null);

  // Load selections from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [entRes, tmplRes] = await Promise.all([
          api.get('/entities/'),
          api.get('/templates')
        ]);
        setEntities(entRes.data);
        setTemplates(tmplRes.data.templates || []);
      } catch (error) {
        console.error("Failed to load form filling data", error);
        toast.error("Failed to load options");
      }
    };
    fetchData();
  }, []);

  const canSubmit =
    selectedEntityId &&
    selectedTemplate &&
    !isSubmitting;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    setIsSubmitting(true);
    const toastId = toast.loading("AI Agent is filling the form... This might take a minute.");

    try {
      // API signature: POST /form-fill/ params: template_id, entity_id.
      // Returns { filled_html_path, filled_data, validation_warnings }
      const response = await api.post('/form-fill/', null, {
        params: {
          template_id: selectedTemplate,
          entity_id: selectedEntityId
        }
      });

      const result = response.data;
      setFilledResult(result);
      setShowResult(true);
      toast.success("Form filled successfully!", { id: toastId });

      if (result.validation_warnings && result.validation_warnings.length > 0) {
        toast.error(`Warning: ${result.validation_warnings.length} fields might have issues.`);
      }

      setRecentForms([
        {
          id: Date.now(),
          entityId: selectedEntityId,
          templateId: selectedTemplate,
          submittedAt: new Date().toISOString(),
          status: 'Completed',
          result: result // Store result locally for "recent" access if we want
        },
        ...recentForms,
      ]);

    } catch (error) {
      console.error("Form filling error", error);
      const msg = error.response?.data?.detail || "Failed to fill form";
      toast.error(msg, { id: toastId });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownload = async () => {
    if (!filledResult || !filledResult.filled_html_path) return;

    const pathParts = filledResult.filled_html_path.split('/');
    const filename = pathParts[pathParts.length - 1];

    try {
      const userRes = await api.get('/auth/me');
      const userId = userRes.data.id;

      const response = await api.get(`/form-fill/${userId}/${filename}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

    } catch (error) {
      console.error("Download failed", error);
      toast.error("Failed to download file");
    }
  };

  const handlePreviewHTML = async () => {
    if (!filledResult) return;

    try {
      const pathParts = filledResult.filled_html_path.split('/');
      const filename = pathParts[pathParts.length - 1];
      const userRes = await api.get('/auth/me');
      const userId = userRes.data.id;

      const response = await api.get(`/form-fill/${userId}/${filename}`, {
        responseType: 'text' // We want HTML text
      });

      const newWindow = window.open();
      newWindow.document.write(response.data);
      newWindow.document.close();
    } catch (error) {
      toast.error("Failed to open preview");
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
      <header className="mb-14">
        <h1 className="text-4xl font-semibold text-[#0F172A]">
          Form Filling
        </h1>
        <p className="mt-3 text-lg text-[#475569]">
          Select a source entity and a template to generate filled forms.
        </p>
      </header>


      <div className="grid grid-cols-1 xl:grid-cols-2 gap-10 items-start">
        {/* LEFT COLUMN: SELECTION FORM */}
        <div className="space-y-8">

          <div className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-8 shadow-sm">
            <h2 className="text-xl font-semibold text-[#0F172A] mb-6">
              Configuration
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* ENTITY SELECT */}
              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-2">
                  Select Entity
                </label>
                <div className="relative">
                  <select
                    className="
                      w-full h-12 px-4 pr-10 rounded-xl
                      border border-[#E2E8F0] bg-white
                      text-[#0F172A] text-base
                      focus:outline-none focus:border-[#2563EB]
                      appearance-none
                    "
                    value={selectedEntityId}
                    onChange={(e) => setSelectedEntityId(e.target.value)}
                  >
                    <option value="">-- Choose an entity --</option>
                    {entities.map((ent) => (
                      <option key={ent.id} value={ent.id}>
                        {ent.entity_name || ent.name}
                      </option>
                    ))}
                  </select>
                  <CaretDown
                    size={20}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-[#94A3B8] pointer-events-none"
                  />
                </div>
              </div>

              {/* TEMPLATE SELECT */}
              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-2">
                  Select Template
                </label>
                <div className="relative">
                  <select
                    className="
                      w-full h-12 px-4 pr-10 rounded-xl
                      border border-[#E2E8F0] bg-white
                      text-[#0F172A] text-base
                      focus:outline-none focus:border-[#2563EB]
                      appearance-none
                    "
                    value={selectedTemplate}
                    onChange={(e) => setSelectedTemplate(e.target.value)}
                  >
                    <option value="">-- Choose a template --</option>
                    {templates.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name || t.filename} ({t.lang || 'en'})
                      </option>
                    ))}
                  </select>
                  <CaretDown
                    size={20}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-[#94A3B8] pointer-events-none"
                  />
                </div>
              </div>

              {/* ACTION BUTTON */}
              <div className="pt-4">
                <button
                  type="submit"
                  disabled={!canSubmit}
                  className={`
                    w-full h-14 rounded-xl
                    text-white text-base font-medium
                    transition
                    ${canSubmit ? 'bg-[#2563EB] hover:bg-[#1D4ED8]' : 'bg-[#94A3B8] cursor-not-allowed'}
                  `}
                >
                  {isSubmitting ? 'AI Processing...' : 'Proceed'}
                </button>
              </div>
            </form>
          </div>

          {/* RECENT FORMS (Local history only for now) */}
          {recentForms.length > 0 && (
            <div className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-8 shadow-sm">
              <h3 className="text-lg font-semibold text-[#0F172A] mb-4">
                Recent Activity
              </h3>
              <ul className="space-y-4">
                {recentForms.map((form) => {
                  const entName = entities.find(e => e.id == form.entityId)?.entity_name || "Entity";
                  const tmplName = templates.find(t => t.id == form.templateId)?.name || "Template";
                  return (
                    <li key={form.id} className="text-sm flex justify-between items-center text-[#475569] border-b border-[#F1F5F9] pb-2 last:border-0">
                      <span>Filled <b>{tmplName}</b> for <b>{entName}</b></span>
                      <span className="text-xs">{new Date(form.submittedAt).toLocaleTimeString()}</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

        </div>

        {/* RIGHT COLUMN: RESULTS */}
        <AnimatePresence>
          {showResult && filledResult && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-8 shadow-sm sticky top-10"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#D1FAE5] flex items-center justify-center text-[#059669]">
                    <Check size={20} weight="bold" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-[#0F172A]">Success!</h2>
                    <p className="text-xs text-[#64748B]">Form filled successfully</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowResult(false)}
                  className="text-[#94A3B8] hover:text-[#0F172A]"
                >
                  <X size={20} />
                </button>
              </div>

              <div className="mb-6 space-y-3">
                <button
                  onClick={handlePreviewHTML}
                  className="w-full h-12 rounded-xl border border-[#E2E8F0] flex items-center justify-center gap-2 text-[#0F172A] font-medium hover:bg-[#F8FAFC] transition"
                >
                  <Eye size={20} />
                  Preview HTML
                </button>
                <button
                  onClick={handleDownload}
                  className="w-full h-12 rounded-xl bg-[#2563EB] text-white flex items-center justify-center gap-2 font-medium hover:bg-[#1D4ED8] transition"
                >
                  <Download size={20} />
                  Download HTML
                </button>
              </div>

              <div className="border-t border-[#F1F5F9] pt-6">
                <h3 className="text-sm font-semibold text-[#475569] mb-4">Extracted & Filled Fields</h3>
                <div className="max-h-[400px] overflow-y-auto space-y-3 pr-2 scrollbar-thin">
                  {Object.entries(filledResult.filled_data || {}).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <span className="block text-[#64748B] text-xs uppercase tracking-wide font-semibold mb-1">{key}</span>
                      <div className="p-3 bg-[#F8FAFC] rounded-lg text-[#0F172A] border border-[#E2E8F0] break-words">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
