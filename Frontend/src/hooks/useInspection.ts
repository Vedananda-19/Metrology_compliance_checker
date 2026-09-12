import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../apis/api";
import type { Inspection, InspectionDetail, InspectionImage } from "../types/inspection";

export const useInspections = () =>
    useQuery({
        queryKey: ["inspections"],
        queryFn: async () => (await api.get<Inspection[]>("/inspections")).data,
    });

export const useInspection = (id: string | undefined) =>
    useQuery({
        queryKey: ["inspection", id],
        enabled: Boolean(id),
        queryFn: async () => (await api.get<InspectionDetail>(`/inspections/${id}`)).data,
    });

const useInspectionMutation = <TVariables, TData>(
    id: string | undefined,
    request: (variables: TVariables) => Promise<TData>,
) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: request,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inspection", id] }),
    });
};

export const useCreateInspection = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (body: { title?: string }) =>
            (await api.post<Inspection>("/inspections", body)).data,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inspections"] }),
    });
};

export const useUploadImages = (id: string | undefined) =>
    useInspectionMutation(id, async (files: File[]) => {
        const form = new FormData();
        for (const file of files) form.append("files", file);
        return (await api.post<InspectionImage[]>(`/inspections/${id}/images`, form)).data;
    });

export const useDeleteImage = (id: string | undefined) =>
    useInspectionMutation(id, async (imageId: string) =>
        (await api.delete(`/inspections/${id}/images/${imageId}`)).data,
    );

export const useProcess = (id: string | undefined) =>
    useInspectionMutation(id, async () =>
        (await api.post<InspectionDetail>(`/inspections/${id}/process`)).data,
    );
