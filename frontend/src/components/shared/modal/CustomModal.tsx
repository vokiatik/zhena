import "./CustomModal.css"

interface NewProcessModalProps {
    modalTitle?: string;
    SaveButtonName?: string;
    children: React.ReactNode;
    handleSave: () => void;
    handleClose: () => void;
}

export default function CustomModal({
    modalTitle,
    SaveButtonName,
    children,
    handleSave,
    handleClose
}: NewProcessModalProps) {
    return (
        <div className="modal-overlay">
            <div className="modal">
                <div className="modal-header">
                    <h2 className="modal-title">{modalTitle || "Parameters"}</h2>
                    <button className="modal-close" onClick={handleClose}>X</button>
                </div>

                <div className="modal-body">
                    {children}
                </div>

                <div className="modal-footer">
                    <button className="button-primary" onClick={handleSave}>{SaveButtonName || "Ok"}</button>
                    <button className="button-secondary" onClick={handleClose}>Cancel</button>
                </div>
            </div>
        </div>
    );
}