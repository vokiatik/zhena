import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "../../api";
import { useUser } from "../../contexts";
import TvLoading from "../../components/shared/loading/TvLoading";
import type { ProcessInstance } from "../../types/process_instance";
import DataPrepStepper, { DATA_PREP_STEPS, getStepIndex } from "./DataPrepStepper";
import FileUploadStep from "./FileUploadStep";
import ProvideLinkStep from "./ProvideLinkStep";
import AnalystReviewStep from "./AnalystReviewStep";
import MarketingReviewStep from "./MarketingReviewStep";
import { CompletedStep, CanceledState } from "./DataPrepStates";
import "./DataPrepWorkflow.css";

export default function DataPrepWorkflow() {
    const { processId } = useParams<{ processId: string }>();
    const navigate = useNavigate();
    const { get } = useApi();
    const { hasAnyRole } = useUser();
    const queryClient = useQueryClient();

    const { data: process, isPending, error, refetch } = useQuery<ProcessInstance>({
        queryKey: ["process_instance", processId],
        queryFn: async () => {
            const res = await get<ProcessInstance>(`/process-instances/${processId}`);
            return res.data;
        },
        enabled: !!processId,
    });

    const handleStepDone = () => {
        refetch();
        queryClient.invalidateQueries({ queryKey: ["process_instances"] });
    };

    if (isPending) return <TvLoading />;
    if (error || !process) return (
        <div className="dp-container">
            <p className="dp-error">Process not found.</p>
        </div>
    );

    const isCanceled = process.status_name === "canceled";
    const currentStepIdx = isCanceled ? -1 : getStepIndex(process.status_name);

    const isAdmin = hasAnyRole("admin");
    const isAnalyst = hasAnyRole("analyst");
    const isMarketing = hasAnyRole("marketing_specialist");

    return (
        <div className="dp-container">
            <div className="dp-header">
                <div className="dp-header-left">
                    <button className="dp-back-btn" onClick={() => navigate("/processes")}>
                        ← Processes
                    </button>
                    <div>
                        <h1 className="dp-title">Data Preparation</h1>
                        <span className="dp-process-id">#{process.id.slice(0, 8)}</span>
                    </div>
                </div>
                <span className={`dp-status-badge dp-status--${process.status_name.replace(/ /g, "_")}`}>
                    {process.status_name}
                </span>
            </div>

            {isCanceled ? (
                <CanceledState />
            ) : (
                <>
                    <DataPrepStepper currentStepIdx={currentStepIdx} />


                    <h2 className="dp-card-title">{DATA_PREP_STEPS[currentStepIdx]?.label}</h2>

                    {process.status_name === "initiated" && (
                        <div className="dp-card">
                            <FileUploadStep processId={process.id} onDone={handleStepDone} />
                        </div>
                    )}
                    {process.status_name === "awaiting_link" && (
                        <div className="dp-card">
                            <ProvideLinkStep processId={process.id} onDone={handleStepDone} />
                        </div>
                    )}
                    {process.status_name === "analyst_review" && (
                        <AnalystReviewStep
                            processId={process.id}
                            canAct={isAdmin || isAnalyst}
                            onDone={handleStepDone}
                        />
                    )}
                    {process.status_name === "marketing_review" && (
                        <MarketingReviewStep
                            processId={process.id}
                            canAct={isAdmin || isMarketing}
                            onDone={handleStepDone}
                        />
                    )}
                    {process.status_name === "completed" && <CompletedStep />}
                </>
            )}
        </div>
    );
}
