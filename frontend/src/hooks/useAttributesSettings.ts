import { useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import type { PictureAttributes } from "../types/picture_attributes";

export function useAttributesSettings() {
    const { get, post } = useApi();

    const [processId, setProcessId] = useState<string | null>(null);
    
    const getAttributes = useCallback(
        async () => {
        const response = await get<string[]>(`/process/attributes/list`);
        return response.data;
    }, [get]);

    const getProcessAttributes = useCallback(
        async (processId: string) => {
        const response = await get<PictureAttributes[]>(`/process/attributes/${processId}`);
        return response.data;
    }, [get]);

    const getProcessAttributesReferenceList = useCallback(
        async () => {
        const response = await get<string[]>(`/process/attributes/reference/types_list`);
        return response.data;
    }, [get]);
    
    const AddNewProcessAttribute = useCallback(
        async (processId: string, attribute: PictureAttributes) => {
            await post(`/process/attributes/create`, { process_id: processId, attribute: attribute });
            await getProcessAttributes(processId);
        },
        [post, getProcessAttributes]
    );
    const UpdateProcessAttribute = useCallback(
        async (processId: string, attribute: PictureAttributes) => {
            await post(`/process/attributes/update/${processId}`, { attribute: attribute });
            await getProcessAttributes(processId);
        },
        [post, getProcessAttributes]
    );

    const DeleteProcessAttribute = useCallback(
        async (processId: string, attributeId: string) => {
            await post(`/process/attributes/delete/${processId}/${attributeId}`);
            await getProcessAttributes(processId);
        },
        [post, getProcessAttributes]
    );

    const CreateNewAttributeReferenceType = useCallback(
        async (referenceType: string) => {
            await post(`/process/attributes/reference/create_type`, {
                reference_value_presetting_type: referenceType
            });
            refetchReferenceList();
        },
        [post, getProcessAttributes]
    );
    // const GetListOfPresettingValues = useCallback(
    //     async (referenceType: string) => {
    //         const response = await get<string[]>(`/process/attributes/presetting_values/${referenceType}`);
    //         return response.data;
    //     },
    //     [get]
    // );
    // const AddNewPresettingValue = useCallback(
    //     async (referenceType: string, referenceValue: string) => {
    //         await post(`/process/attributes/create_presetting_value`, {
    //             reference_value_presetting_type: referenceType,
    //             reference_value: referenceValue
    //         });
    //     },
    //     [post, getProcessAttributes]
    // );

    const CreateNewAttributeReference = useCallback(
        async (processId: string, attributeId: string, referenceType: string) => {
            await post(`/process/attributes/create_presetting_value`, {
                process_id: processId,
                picture_attribute_id: attributeId,
                reference_value_presetting_type: referenceType
            });
            await getProcessAttributes(processId);
        },
        [post, getProcessAttributes]
    );


    const { data: attributes, isPending: isAttributesPending, error: attributesError } = useQuery({
        queryKey: ['attributes_list'],
        queryFn: getAttributes,
    })
    const { data: referenceList, isPending: isReferenceListPending, error: referenceListError, refetch: refetchReferenceList } = useQuery({
        queryKey: ['reference_list'],
        queryFn: getProcessAttributesReferenceList,
    })

    const { data: processAttributes, refetch: refetchProcessAttributes, isPending: isProcessAttributesPending, error: processAttributesError } = useQuery({
        queryKey: ['process_attributes_list', processId],
        queryFn: () => {
            if (!processId) throw new Error("processId is null");
            return getProcessAttributes(processId);
        },
        enabled: !!processId,
    })

  return { 
    attributes,
    isAttributesPending,
    attributesError,
    referenceList,
    isReferenceListPending,
    referenceListError,
    processAttributes,
    isProcessAttributesPending,
    processAttributesError,
    CreateNewAttributeReference,
    setProcessId,
    refetchProcessAttributes,
    AddNewProcessAttribute,
    UpdateProcessAttribute,
    DeleteProcessAttribute,
    CreateNewAttributeReferenceType
};
}