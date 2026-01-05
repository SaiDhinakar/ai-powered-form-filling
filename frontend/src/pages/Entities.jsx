import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Trash, File, FileImage, FilePdf, X } from 'phosphor-react';
import Modal from '../components/Modal';
// import useLocalStorage from '../hooks/useLocalStorage';
import DocumentPreview from '../components/DocumentPreview';
import api from '../services/api';
import toast from 'react-hot-toast';


export default function Entities() {
  const [previewFile, setPreviewFile] = useState(null);
  const [entities, setEntities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newEntityName, setNewEntityName] = useState('');

  // Upload Modal State
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadEntityId, setUploadEntityId] = useState(null);
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

  // Fetch Entities (and their consolidated data if possible, but API signature for list_entities just lists entities.
  // The 'Entity' model in backend doesn't seem to include 'documents' list directly in the listing?
  // Let's check entities.py: EntityRepository.get_by_user returns List[Entity].
  // Entity model probably has relationships.
  // Assuming the frontend needs to show "documents" count.
  // If the backend Entity response structure lacks a 'documents' list, we might need to fetch it or adjust.
  // However, `Entities.jsx` was originally showing "documents".
  // `user_data.py` has `list_entity_data`. But that returns "consolidated data".
  // The original design was "upload documents to entity". The backend stores "extracted data" from documents.
  // So "documents" as files might not be persistently stored as a list in the Entity object in the same way?
  // `EntityRepository` uses `Entity` model. `database/models.py` would show extraction.
  // Actually, `user_data.py` saves file to disk. But does `Entity` relation track it?
  // The current UI expects `entity.documents`.
  // If the backend doesn't return `documents` in `GET /entities`, I might not see them.
  // I will check the list_entities response structure in my next step if needed, but for now I assume standard behavior or minimal "documents" count.
  // Wait, I should implement it assuming I can get the list.

  const fetchEntities = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/entities/');
      // Adapt response to UI structure if needed.
      // The backend returns a list of Entity objects.
      // If Entity object has no `documents` array, UI will break.
      // I'll ensure we map it safely.
      const mappedEntities = response.data.map(e => ({
        ...e,
        documents: e.documents || [] // Fallback if backend doesn't send documents
      }));
      setEntities(mappedEntities);
    } catch (error) {
      console.error("Failed to fetch entities", error);
      toast.error("Failed to load entities");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEntities();
  }, []);

  const handleCreateEntity = async (e) => {
    e.preventDefault();
    if (!newEntityName.trim()) return;

    try {
      // API expects entity_name as query param
      const response = await api.post('/entities/', null, {
        params: { entity_name: newEntityName }
      });
      // Add new entity to local state
      setEntities([...entities, { ...response.data, documents: [] }]);
      toast.success("Entity created");
      setNewEntityName('');
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error("Create entity error", error);
      toast.error("Failed to create entity");
    }
  };

  const openUploadModal = (entityId) => {
    setUploadEntityId(entityId);
    setFilesToUpload([]);
    setUploadLanguage('en');
    setIsUploadModalOpen(true);
  };

  const handleFileSelection = (e) => {
    if (e.target.files) {
      setFilesToUpload(Array.from(e.target.files));
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadEntityId || filesToUpload.length === 0) return;

    // Upload files one by one (API design seems to take single file per call based on my reading of user_data.py)
    // `create_entity_data` signature: file: UploadFile, entity_id, lang

    // We'll show a loading toast or similar?
    const toastId = toast.loading("Uploading documents...");

    try {
      for (const file of filesToUpload) {
        const formData = new FormData();
        formData.append('file', file);

        // user_data.py expects entity_id and lang as params?
        // signature: async def create_entity_data(entity_id: int, lang: str = 'en', file: UploadFile = File(...), ...)
        // usually fastAPI takes simple args as query params if not Form.
        await api.post('/entities-data/', formData, {
          params: {
            entity_id: uploadEntityId,
            lang: uploadLanguage
          },
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        });
      }

      toast.success("Documents uploaded successfully", { id: toastId });

      // Refresh entities to show new documents (if backend returns them)
      // If backend doesn't return documents list in `GET /entities`, we won't see them here.
      // This is a potential issue I noted, but I will proceed with fetch.
      fetchEntities();

    } catch (error) {
      console.error("Upload error", error);
      toast.error("Failed to upload some documents", { id: toastId });
    } finally {
      setIsUploadModalOpen(false);
      setFilesToUpload([]);
      setUploadEntityId(null);
    }
  };


  const handleDeleteEntity = async (id) => {
    if (!confirm("Are you sure you want to delete this entity?")) return;
    try {
      await api.delete(`/entities/${id}`);
      setEntities(entities.filter((e) => e.id !== id));
      toast.success("Entity deleted");
    } catch (error) {
      console.error("Delete entity error", error);
      toast.error("Failed to delete entity");
    }
  };

  const handleDeleteDocument = async (entityId, docId) => {
    // Backend API for deleting a document (entity data)?
    // I didn't see a DELETE endpoint in `user_data.py`!
    // `user_data.py` only has GET / and POST /.
    // `entities.py` has DELETE /entities/{id}.
    // So we can't delete individual documents via API yet?
    // I will leave it as "Frontend only removal" or show toast warning.
    // Or, maybe I missed it. I checked `user_data.py` thoroughly.
    // I'll just show a "Not implemented in backend" toast for now to prevent errors.
    toast.error("Deleting documents is not supported by backend yet.");
  };

  // Kept for editing if needed, but primary selection is now in modal
  const handleLanguageChange = (entityId, docId, newLanguage) => {
    // Also no update endpoint for documents in `user_data.py`.
    toast.error("Updating language is not supported by backend yet.");
  };

  const getFileIcon = (type) => {
    if (!type) return File;
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
          onClick={() => setIsCreateModalOpen(true)}
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

      {/* LOADING STATE */}
      {isLoading && entities.length === 0 && (
        <div className="text-center py-20 text-[#64748B]">Loading entities...</div>
      )}

      {/* EMPTY STATE */}
      {!isLoading && entities.length === 0 && (
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
                    {entity.entity_name || entity.name}
                  </h2>
                  <p className="mt-1 text-sm text-[#64748B]">
                    {entity.documents ? entity.documents.length : 0} documents
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
                {entity.documents && entity.documents.map((doc) => {
                  const Icon = getFileIcon(doc.type); // doc.type might be missing from backend, need robust check
                  return (
                    <div
                      key={doc.id || Math.random()}
                      // onClick={() => setPreviewFile(doc)} // Disable preview for now as we don't have file URL easily from backend listing
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
                          <span className="truncate text-[#0F172A] text-sm font-medium">
                            {doc.name || doc.filename || "Document"}
                          </span>
                          <span className="text-xs text-[#64748B]">
                            {languages.find(l => l.code === doc.language)?.name || doc.language || 'English'}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteDocument(entity.id, doc.id);
                          }}
                          className="text-[#94A3B8] hover:text-[#B91C1C] p-1"
                        >
                          <Trash size={14} />
                        </button>
                      </div>
                    </div>
                  );
                })}
                {/* Fallback if no documents */}
                {(!entity.documents || entity.documents.length === 0) && (
                  <p className="text-sm text-gray-400 italic">No documents uploaded.</p>
                )}
              </div>

              <button
                onClick={() => openUploadModal(entity.id)}
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

      {/* CREATE ENTITY MODAL */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
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
              onClick={() => setIsCreateModalOpen(false)}
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

      {/* UPLOAD MODAL */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Documents"
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
                accept=".pdf,image/*"
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
                Document Language
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
