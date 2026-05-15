export function CompletedStep() {
    return (
        <div className="dp-step-body dp-completed">
            <div className="dp-completed-icon">✓</div>
            <h3 className="dp-completed-title">Process Completed</h3>
            <p className="dp-completed-desc">
                All data has been reviewed and approved. The results will be uploaded to
                the analytics database.
            </p>
        </div>
    );
}

export function CanceledState() {
    return (
        <div className="dp-step-body dp-canceled">
            <div className="dp-canceled-icon">✕</div>
            <h3 className="dp-canceled-title">Process Canceled</h3>
            <p>This process was canceled and is no longer active.</p>
        </div>
    );
}
