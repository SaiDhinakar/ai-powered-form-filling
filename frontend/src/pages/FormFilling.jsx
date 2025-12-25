import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import useLocalStorage from '../hooks/useLocalStorage';
import Loader from '../components/Loader';

export default function FormFilling() {
  const [entities] = useLocalStorage('entities', []);
  const [templates] = useLocalStorage('templates', []);
  const [recentForms, setRecentForms] = useLocalStorage('recentForms', []);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [selectedEntity, setSelectedEntity] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [formData, setFormData] = useState({
    field1: '',
    field2: '',
    field3: '',
  });

  const canSubmit = selectedEntity && selectedTemplate && !isSubmitting;

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      setRecentForms([
        {
          id: Date.now(),
          entityId: selectedEntity,
          templateId: selectedTemplate,
          submittedAt: new Date().toISOString(),
          status: 'Completed',
        },
        ...recentForms,
      ]);

      setSelectedEntity('');
      setSelectedTemplate('');
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
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Entity
              </label>
              <select
                className="input"
                value={selectedEntity}
                onChange={(e) => setSelectedEntity(e.target.value)}
              >
                <option value="">Select entity</option>
                {entities.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Template
              </label>
              <select
                className="input"
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
              >
                <option value="">Select template</option>
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
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
