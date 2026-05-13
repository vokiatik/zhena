import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import type { ProcessInstance } from "../types/process_instance";
import type { ConfirmDecision, ValidationRequiredResponse } from "../types/file_upload_validation";

type UploadFileResult = { ok: boolean; status?: string } | ValidationRequiredResponse;

export function useProcessInstances() {
    const { get, post, put } = useApi();

    const fetchProcessInstances = useCallback(async () => {
        const response = await get<ProcessInstance[]>("/process-instances/list");
        return response.data;
    }, [get]);

    const fetchProcessStatuses = useCallback(async () => {
        const response = await get<string[]>("/process-instances/statuses");
        return response.data;
    }, [get]);

    const {
        data: processInstances,
        isPending,
        error,
        refetch,
    } = useQuery({
        queryKey: ["process_instances"],
        queryFn: fetchProcessInstances,
    });

    const { data: statusOptions } = useQuery({
        queryKey: ["process_statuses"],
        queryFn: fetchProcessStatuses,
    });

    const createProcess = useCallback(
        async (comment?: string) => {
            const response = await post<{ ok: boolean; process_id: string }>(
                "/process-instances/create",
                { comment }
            );
            refetch();
            return response.data;
        },
        [post, refetch]
    );

    const uploadFile = useCallback(
        async (processId: string, file: File): Promise<UploadFileResult> => {
            const form = new FormData();
            form.append("file", file);
            const response = await post<UploadFileResult>(
                `/process-instances/${processId}/upload-file`,
                form,
                { headers: { "Content-Type": "multipart/form-data" } }
            );
            return response.data;
        },
        [post]
    );

    const confirmDict = useCallback(
        async (processId: string, file: File, decisions: ConfirmDecision[]) => {
            const form = new FormData();
            form.append("file", file);
            form.append("decisions", JSON.stringify(decisions));
            const response = await post<{ ok: boolean }>(
                `/process-instances/${processId}/confirm-dict`,
                form,
                { headers: { "Content-Type": "multipart/form-data" } }
            );
            return response.data;
        },
        [post]
    );

    const provideLink = useCallback(
        async (processId: string, link: string) => {
            const response = await post<{ ok: boolean }>(
                `/process-instances/${processId}/provide-link`,
                { link }
            );
            return response.data;
        },
        [post]
    );

    const analystConfirm = useCallback(
        async (processId: string) => {
            const response = await post<{ ok: boolean }>(
                `/process-instances/${processId}/analyst-confirm`
            );
            return response.data;
        },
        [post]
    );

    const marketingConfirm = useCallback(
        async (processId: string) => {
            const response = await post<{ ok: boolean }>(
                `/process-instances/${processId}/marketing-confirm`
            );
            return response.data;
        },
        [post]
    );

    const cancelProcess = useCallback(
        async (processId: string) => {
            const response = await post<{ ok: boolean }>(
                `/process-instances/${processId}/cancel`
            );
            refetch();
            return response.data;
        },
        [post, refetch]
    );

    const updateProcessInstance = useCallback(
        async (processId: string, data: { status?: string; comment?: string }) => {
            const response = await put<{ ok: boolean }>(
                `/process-instances/update/${processId}`,
                data
            );
            refetch();
            return response.data;
        },
        [put, refetch]
    );

    return {
        processInstances,
        isPending,
        error,
        statusOptions: statusOptions ?? [],
        refetch,
        createProcess,
        uploadFile,
        confirmDict,
        provideLink,
        analystConfirm,
        marketingConfirm,
        cancelProcess,
        updateProcessInstance,
    };
}
