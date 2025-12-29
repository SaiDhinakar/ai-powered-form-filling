import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Warning } from 'phosphor-react';
import useLocalStorage from '../hooks/useLocalStorage';
import Loader from '../components/Loader';

export default function FormFilling() {
  const [entities] = useLocalStorage('entities', []);
  const [templates] = useLocalStorage('templates', []);
  const [recentForms, setRecentForms] = useLocalStorage('recentForms', []);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Selection State
  const [selectedEntityId, setSelectedEntityId] = useState('');
  const [selectedTemplateId, setSelectedTemplateId] = useState('');

  const [formData, setFormData] = useState({
    field1: '',
    field2: '',
    field3: '',
  });

  const selectedEntity = entities.find(e => e.id === parseInt(selectedEntityId));
  const selectedTemplate = templates.find(t => t.id === parseFloat(selectedTemplateId));

  const handleEntityChange = (e) => {
    setSelectedEntityId(e.target.value);
    setSelectedTemplateId('');
    setFormData({ field1: '', field2: '', field3: '' });
  };

  const handleTemplateChange = (e) => {
    setSelectedTemplateId(e.target.value);
    // Simulate AI extraction simply by template selection as a trigger?
    // Or just clear it.
    setFormData({
      field1: '',
      field2: '',
      field3: ''
    });
  };

  const canSubmit = selectedEntityId && selectedTemplateId && !isSubmitting;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    setIsSubmitting(true);

    setTimeout(() => {
      setRecentForms([
        {
          id: Date.now(),
          entityId: selectedEntityId,
          // documentId is no longer explicitly selected
          templateId: selectedTemplateId,
          templateLanguage: selectedTemplate?.language,
          submittedAt: new Date().toISOString(),
          status: 'Completed',
        },
        ...recentForms,
      ]);

      setFormData({ field1: '', field2: '', field3: '' });
      setIsSubmitting(false);
    }, 1200);
  };

  return (
    <motion.div
      className="min-h-screen bg-[#ECEFF3] px-10 py-10"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.35 }}
    >
      {isSubmitting && <Loader fullScreen />}

      {/* HEADER */}
      <header className="mb-14">
        <h1 className="text-4xl font-semibold text-[#0F172A]">
          Form workspace
        </h1>
        <p className="mt-3 text-lg text-[#475569] max-w-2xl">
          Review source documents, confirm extracted values, and submit with confidence.
        </p>
      </header>

      {/* WORKSPACE */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* LEFT PANEL */}
        <motion.section
          className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-10"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h2 className="text-xl font-semibold text-[#0F172A] mb-8">
            Source document
          </h2>

          <div className="space-y-6">
            {/* 1. Select Entity */}
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Entity
              </label>
              <select
                className="input"
                value={selectedEntityId}
                onChange={handleEntityChange}
              >
                <option value="">Select entity</option>
                {entities.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.name}
                  </option>
                ))}
              </select>
            </div>

            {/* 2. Select Template */}
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Template
              </label>
              <select
                className="input"
                value={selectedTemplateId}
                onChange={handleTemplateChange}
                disabled={!selectedEntityId}
              >
                <option value="">Select template</option>
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.language})
                  </option>
                ))}
              </select>
            </div>

            <div className="pt-4">
              <button
                type="button"
                className="
                  w-full
                  px-6 py-3
                  rounded-xl
                  bg-[#2563EB]
                  text-white
                  font-medium
                  hover:bg-[#1D4ED8]
                  disabled:opacity-40
                  transition
                "
                disabled={!selectedTemplateId || !selectedEntityId}
                onClick={() => {
                  // Logic to 'proceed' - perhaps validating matched documents
                  // For now, it just confirms selection visually
                }}
              >
                Proceed
              </button>
            </div>
          </div>
        </motion.section>

        {/* RIGHT PANEL */}
        <motion.section
          className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-10"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
        >
          <h2 className="text-xl font-semibold text-[#0F172A] mb-8">
            Extracted fields
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {[
              { id: 'field1', label: 'Field 1', ai: true },
              { id: 'field2', label: 'Field 2', ai: true },
              { id: 'field3', label: 'Field 3', ai: false },
            ].map((f) => (
              <div key={f.id}>
                <label className="block text-sm font-medium text-[#0F172A] mb-2">
                  {f.label}
                  {f.ai && (
                    <span className="ml-2 text-xs text-[#64748B]">
                      AI suggested
                    </span>
                  )}
                </label>
                <input
                  className="input"
                  value={formData[f.id]}
                  onChange={(e) =>
                    setFormData({ ...formData, [f.id]: e.target.value })
                  }
                />
              </div>
            ))}

            <div className="pt-8">
              <button
                type="submit"
                disabled={!canSubmit}
                className="
                    w-full
                    px-6 py-3
                    rounded-xl
                    bg-[#2563EB]
                    text-white
                    font-medium
                    hover:bg-[#1D4ED8]
                    disabled:opacity-40
                    transition
                  "
              >
                Submit form
              </button>
            </div>
          </form>
        </motion.section>
      </div>
    </motion.div>
  );
}
