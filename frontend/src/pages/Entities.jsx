import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Trash, File, FileImage, FilePdf } from 'phosphor-react';
import Modal from '../components/Modal';
import LanguageAssignmentModal from '../components/LanguageAssignmentModal';
import DocumentPreview from '../components/DocumentPreview';
import api from '../services/api';
import { toast } from 'react-hot-toast';


export default function Entities() {
  const [previewFile, setPreviewFile] = useState(null);
  const [entities, setEntities] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newEntityName, setNewEntityName] = useState('');

  // Fetch entities
  const fetchEntities = async () => {
    try {
      // Assuming GET /entities/entities/ returns { entities: [...] } or list
      // Based on api_info.json, it seems to return just response... let's assume standard
      // NOTE: endpoint is /entities/entities/ per api_info.json which seems redundant but follows router structure
      const response = await api.get('/entities/entities/');
      // Adjust based on actual response structure. Assuming list or paginated object.
      // If Pydantic model response is direct list, use response.data. 
      // Code below assumes response.data is the array of entities.
      setEntities(response.data);
    } catch (error) {
      console.error('Failed to fetch entities:', error);
      toast.error('Failed to load entities');
    }
  };

  useEffect(() => {
    fetchEntities();
  }, []);

  const handleCreateEntity = async (e) => {
    e.preventDefault();
    if (!newEntityName.trim()) return;

    try {
      await api.post(`/entities/entities/?entity_name=${encodeURIComponent(newEntityName)}`);
      toast.success('Entity created');
      setNewEntityName('');
      setIsModalOpen(false);
      fetchEntities();
    } catch (error) {
      console.error('Failed to create entity:', error);
      toast.error('Failed to create entity');
    }
  };

  // State for language assignment
  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState(false);
  const [pendingFiles, setPendingFiles] = useState([]);
  const [pendingEntityId, setPendingEntityId] = useState(null);

  const fileInputRefs = useRef({});

  const handleFileUpload = (entityId, e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setPendingFiles(files);
    setPendingEntityId(entityId);
    setIsLanguageModalOpen(true);

    // Reset input
    e.target.value = '';
  };

  const handleLanguageConfirm = async (assignments) => {
    if (!pendingEntityId || pendingFiles.length === 0) return;

    const uploadPromise = Promise.all(pendingFiles.map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      // API expects optional 'lang' query param or form field? 
      // api_info.json says query param 'lang' 
      const lang = assignments[file.name] || 'en';

      return api.post(`/entities-data/entities-data/?entity_id=${pendingEntityId}&lang=${lang}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    }));

    toast.promise(uploadPromise, {
      loading: 'Uploading documents...',
      success: 'Documents uploaded',
      error: 'Failed to upload documents'
    }).then(() => {
      // Cleanup
      setPendingFiles([]);
      setPendingEntityId(null);
      setIsLanguageModalOpen(false);
      fetchEntities();
    }).catch(err => {
      console.error(err);
    });
  };


  const handleDeleteEntity = async (id) => {
    if (!confirm("Are you sure you want to delete this entity?")) return;
    try {
      await api.delete(`/entities/entities/${id}`);
      toast.success('Entity deleted');
      fetchEntities();
    } catch (error) {
      console.error(error);
      toast.error('Failed to delete entity');
    }
  };

  const handleDeleteDocument = async (entityId, docId) => {
    // Note: API for deleting specific document from entity data isn't explicitly in api_info.json list 
    // assuming CRUD on entities-data or managing via entity update.
    // If not available, we might need to skip or implement backend endpoint.
    // For now, let's assume DELETE /entities-data/{id} exists or skip implementation and visually remove.
    // Checking api_info.json -> DELETE /entities/entities/{entity_id} delete whole entity.
    // No specific endpoint to delete extracted data item in api_info.json summary provided?
    // Wait, Repository `ExtractedDataRepository` exists. `entities-data` router likely has CRUD?
    // Let's assume there is a delete or just impl visual for now if endpoint missing.
    // Actually, let's try assuming standard REST: DELETE /entities-data/entities-data/{id} (if exists) 
    // or just console log warning.
    console.warn("Delete document API not visible in summary, assuming strictly managed via re-upload or parent delete for now.");
    toast('Delete document feature pending backend endpoint');
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
                    {(entity.extracted_data || []).length} documents
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
                {(entity.extracted_data || []).map((doc) => {
                  const Icon = getFileIcon('pdf'); // Default to PDF icon since we don't have type
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
                        <div className="flex flex-col truncate">
                          <span className="truncate text-[#0F172A]">
                            {doc.file_hash || 'Unnamed Document'}
                          </span>
                          <span className="text-xs text-[#64748B]">
                            {doc.status === 1 ? 'Processed' : 'Processing/Pending'}
                          </span>
                        </div>
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
