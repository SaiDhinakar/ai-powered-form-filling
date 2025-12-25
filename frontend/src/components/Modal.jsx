import { X } from 'phosphor-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useId } from 'react';

export default function Modal({ isOpen, onClose, title, children }) {
  const titleId = useId();

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose?.();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby={titleId}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          />

          {/* Modal */}
          <motion.div
            className="relative bg-white rounded-2xl border border-[#E6E8EB] w-full max-w-md mx-4 shadow-2xl"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-[#E6E8EB] bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-2xl">
              <h2 id={titleId} className="text-lg font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                {title}
              </h2>
              <motion.button
                onClick={onClose}
                className="p-1 rounded-lg hover:bg-white text-[#94A3B8] hover:text-[#0F172A] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB] focus-visible:ring-offset-2"
                aria-label="Close"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <X size={20} />
              </motion.button>
            </div>

            {/* Content */}
            <motion.div
              className="p-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              {children}
            </motion.div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
