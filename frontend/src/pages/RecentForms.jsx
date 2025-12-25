import { motion, AnimatePresence } from 'framer-motion';
import useLocalStorage from '../hooks/useLocalStorage';

export default function RecentForms() {
  const [recentForms] = useLocalStorage('recentForms', []);

  const formatDate = (dateString) =>
    new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

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
          Recent Forms
        </h1>
        <p className="mt-3 text-lg text-[#475569] max-w-2xl">
          History of submitted forms and generated documents.
        </p>
      </header>

      {/* CONTENT */}
      {recentForms.length === 0 ? (
        <div className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-16 text-center">
          <p className="text-lg font-medium text-[#0F172A]">
            No activity recorded
          </p>
          <p className="mt-3 text-[#64748B] max-w-md mx-auto">
            Submitted forms will appear here once processing begins.
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
                  Entity
                </th>
                <th className="text-left px-8 py-4 text-sm font-medium text-[#475569]">
                  Template
                </th>
                <th className="text-left px-8 py-4 text-sm font-medium text-[#475569]">
                  Submitted
                </th>
                <th className="text-left px-8 py-4 text-sm font-medium text-[#475569]">
                  Status
                </th>
                <th className="px-8 py-4"></th>
              </tr>
            </thead>

            <tbody>
              <AnimatePresence>
                {recentForms.map((form) => (
                  <motion.tr
                    key={form.id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="border-b border-[#F1F5F9]"
                  >
                    <td className="px-8 py-5 text-sm font-medium text-[#0F172A]">
                      {form.entityName}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {form.templateName}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#475569]">
                      {formatDate(form.submittedAt)}
                    </td>
                    <td className="px-8 py-5 text-sm text-[#0F172A]">
                      {form.status}
                    </td>
                    <td className="px-8 py-5 text-right">
                      <button className="text-sm text-[#2563EB] hover:underline">
                        View
                      </button>
                      <button className="ml-6 text-sm text-[#2563EB] hover:underline">
                        Export
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </motion.div>
      )}
    </motion.div>
  );
}
