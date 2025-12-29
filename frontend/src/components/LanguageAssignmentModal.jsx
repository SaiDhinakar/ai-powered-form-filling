import { useState, useEffect } from 'react';
import Modal from './Modal';
import { LANGUAGES } from '../constants/languages';

export default function LanguageAssignmentModal({ isOpen, onClose, files, onConfirm }) {
    const [assignments, setAssignments] = useState({});

    useEffect(() => {
        if (files.length > 0) {
            // Reset assignments when files change
            const initial = {};
            files.forEach(f => {
                initial[f.name] = ''; // Default to empty or maybe 'en'?
            });
            setAssignments(initial);
        }
    }, [files]);

    const handleChange = (fileName, langCode) => {
        setAssignments(prev => ({
            ...prev,
            [fileName]: langCode
        }));
    };

    const handleConfirm = () => {
        // Return array of mapping: { fileIndex: 0, language: 'en' } or similar
        // The parent likely needs the original File objects coupled with language.
        // So we pass back the map.
        onConfirm(assignments);
    };

    const allSelected = files.every(f => assignments[f.name]);

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Assign Languages">
            <div className="space-y-4">
                <p className="text-sm text-[#64748B]">
                    Please select the language for each uploaded document.
                </p>

                <div className="max-h-60 overflow-y-auto space-y-3 pr-2">
                    {files.map((file) => (
                        <div key={file.name} className="flex items-center justify-between p-3 border border-[#E6E8EB] rounded-lg">
                            <span className="text-sm font-medium text-[#0F172A] truncate max-w-[200px]" title={file.name}>
                                {file.name}
                            </span>
                            <select
                                className="input py-1 px-2 text-sm w-40"
                                value={assignments[file.name] || ''}
                                onChange={(e) => handleChange(file.name, e.target.value)}
                            >
                                <option value="">Select language</option>
                                {LANGUAGES.map(l => (
                                    <option key={l.code} value={l.code}>{l.name}</option>
                                ))}
                            </select>
                        </div>
                    ))}
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-[#E6E8EB]">
                    <button
                        onClick={onClose}
                        className="btn btn-secondary"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleConfirm}
                        disabled={!allSelected}
                        className="btn btn-primary disabled:opacity-50"
                    >
                        Confirm Upload
                    </button>
                </div>
            </div>
        </Modal>
    );
}
