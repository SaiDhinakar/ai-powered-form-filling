import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Trash, File, FileImage, FilePdf } from 'phosphor-react';
import Modal from '../components/Modal';
import useLocalStorage from '../hooks/useLocalStorage';
import DocumentPreview from '../components/DocumentPreview';


export default function Entities() {
  const [previewFile, setPreviewFile] = useState(null);
  const [entities, setEntities] = useLocalStorage('entities', []);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newEntityName, setNewEntityName] = useState('');
  const fileInputRefs = useRef({});

  const handleCreateEntity = (e) => {
    e.preventDefault();
    if (!newEntityName.trim()) return;

    setEntities([
      ...entities,
      {
        id: Date.now(),
        name: newEntityName,
        documents: [],
        createdAt: new Date().toISOString(),
      },
    ]);

    setNewEntityName('');
    setIsModalOpen(false);
  };

  const handleFileUpload = (entityId, e) => {
  const files = Array.from(e.target.files);

  setEntities(
    entities.map((entity) =>
      entity.id === entityId
        ? {
            ...entity,
            documents: [
              ...entity.documents,
              ...files.map((file) => ({
                id: Date.now() + Math.random(),
                name: file.name,
                type: file.type,
                size: file.size,
                url: URL.createObjectURL(file),
              })),
            ],
          }
        : entity
    )
  );
};


  const handleDeleteEntity = (id) => {
    // Revoke all blob URLs in the entity to free memory
    const entityToDelete = entities.find((e) => e.id === id);
    if (entityToDelete?.documents) {
      entityToDelete.documents.forEach((doc) => {
        if (doc.url && doc.url.startsWith('blob:')) {
          URL.revokeObjectURL(doc.url);
        }
      });
    }

    setEntities(entities.filter((e) => e.id !== id));
  };

  const handleDeleteDocument = (entityId, docId) => {
    // Revoke blob URL to free memory
    const docToDelete = entities
      .find((e) => e.id === entityId)
      ?.documents.find((d) => d.id === docId);
    
    if (docToDelete?.url && docToDelete.url.startsWith('blob:')) {
      URL.revokeObjectURL(docToDelete.url);
    }

    setEntities(
      entities.map((entity) =>
        entity.id === entityId
          ? {
              ...entity,
              documents: entity.documents.filter((d) => d.id !== docId),
            }
          : entity
      )
    );
  };

  const getFileIcon = (type) => {
    if (type.includes('pdf')) return FilePdf;
    if (type.includes('image')) return FileImage;
    return File;
  };

  return (
    <motion.div
      className="min-h-screen bg-[#ECEFF3] px-10 py-10"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.35 }}
    >
      {/* HEADER */}
      <header className="mb-14 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-semibold text-[#0F172A]">
            Entities
          </h1>
          <p className="mt-3 text-lg text-[#475569]">
            Structured sources used by your AI system.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="
            px-6 py-3
            rounded-xl
            bg-[#2563EB]
            text-white
            font-medium
            hover:bg-[#1D4ED8]
            transition
          "
        >
          Create entity
        </button>
      </header>

      {/* EMPTY STATE */}
      {entities.length === 0 && (
        <div className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-16 text-center">
          <p className="text-xl font-medium text-[#0F172A]">
            No entities created
          </p>
          <p className="mt-2 text-[#475569]">
            Entities store documents used during form filling.
          </p>
        </div>
      )}

      {/* ENTITIES */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        <AnimatePresence>
          {entities.map((entity) => (
            <motion.div
              key={entity.id}
              className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-3xl p-8"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.25 }}
            >
              {/* ENTITY HEADER */}
              <div className="flex items-start justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-semibold text-[#0F172A]">
                    {entity.name}
                  </h2>
                  <p className="mt-1 text-sm text-[#64748B]">
                    {entity.documents.length} documents
                  </p>
                </div>

                <button
                  onClick={() => handleDeleteEntity(entity.id)}
                  className="text-[#94A3B8] hover:text-[#B91C1C]"
                >
                  <Trash size={18} />
                </button>
              </div>

              {/* DOCUMENTS */}
              <div className="space-y-3 mb-8">
                {entity.documents.map((doc) => {
                  const Icon = getFileIcon(doc.type);
                  return (
                      <div
                        key={doc.id}
                        onClick={() => setPreviewFile(doc)}
                        className="
                          flex items-center justify-between
                          px-4 py-3
                          border border-[#E6E8EB]
                          rounded-xl
                          cursor-pointer
                          hover:bg-[#F8FAFC]
                        "
                      >
                      <div className="flex items-center gap-3 min-w-0">
                        <Icon size={18} className="text-[#475569]" />
                        <span className="truncate text-[#0F172A]">
                          {doc.name}
                        </span>
                      </div>

                      <button
                        onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteDocument(entity.id, doc.id);
                            }}
                            className="text-[#94A3B8] hover:text-[#B91C1C]"
                          >
                        <Trash size={14} />
                      </button>
                    </div>
                  );
                })}
              </div>

              {/* UPLOAD */}
              <input
                type="file"
                multiple
                accept=".pdf,image/*"
                className="hidden"
                ref={(el) => (fileInputRefs.current[entity.id] = el)}
                onChange={(e) => handleFileUpload(entity.id, e)}
              />

              <button
                onClick={() => fileInputRefs.current[entity.id]?.click()}
                className="
                  w-full
                  px-5 py-3
                  rounded-xl
                  border border-[#E6E8EB]
                  text-[#0F172A]
                  font-medium
                  hover:bg-[#F7F8FA]
                  transition
                "
              >
                Upload documents
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* MODAL */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create entity"
      >
        <form onSubmit={handleCreateEntity}>
          <input
            className="input mb-6"
            placeholder="Entity name"
            value={newEntityName}
            onChange={(e) => setNewEntityName(e.target.value)}
            autoFocus
          />

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create
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
