import { motion, AnimatePresence } from 'framer-motion';
import { useEffect } from 'react';

export default function DocumentPreview({ isOpen, onClose, file }) {
  // Cleanup blob URL when component unmounts or file changes
  useEffect(() => {
    return () => {
      if (file?.url && file.url.startsWith('blob:')) {
        URL.revokeObjectURL(file.url);
      }
    };
  }, [file?.url]);

  if (!isOpen || !file) return null;

  const fileType = file.type || '';
  const fileName = file.name.toLowerCase();

  const isImage =
    fileType.startsWith('image/') ||
    /\.(png|jpe?g|gif|webp|bmp|svg)$/i.test(fileName);

  const isPdf =
    fileType === 'application/pdf' ||
    fileName.endsWith('.pdf');

  return (
    <AnimatePresence>
      <motion.div
        className="
          fixed inset-0 z-50
          bg-black/60
          flex items-center justify-center
          px-6
        "
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="
            bg-white
            w-full max-w-5xl
            rounded-2xl
            overflow-hidden
            shadow-2xl
          "
          initial={{ scale: 0.96, y: 10 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.96, y: 10 }}
          transition={{ duration: 0.2 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* HEADER */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <p className="font-medium text-[#0F172A] truncate">
              {file.name}
            </p>
            <button
              onClick={onClose}
              className="text-sm text-[#2563EB] hover:underline"
            >
              Close
            </button>
          </div>

          {/* CONTENT */}
          <div className="h-[70vh] bg-[#F8FAFC] flex items-center justify-center">
            {isImage && (
              <img
                src={file.url}
                alt={file.name}
                loading="lazy"
                className="
                  max-h-full
                  max-w-full
                  object-contain
                  select-none
                "
              />
            )}

            {isPdf && (
              <object
                data={file.url}
                type="application/pdf"
                className="w-full h-full"
              >
                <div className="flex flex-col items-center justify-center h-full gap-4">
                  <p className="text-gray-600 font-medium">
                    PDF preview not supported in this browser
                  </p>
                  <a
                    href={file.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    download={file.name}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    Open PDF
                  </a>
                </div>
              </object>
            )}

            {!isImage && !isPdf && (
              <div className="text-center">
                <p className="text-[#475569] font-medium">
                  Preview not available
                </p>
                <p className="text-sm text-[#94A3B8] mt-1">
                  This file type cannot be previewed
                </p>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
