import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../apis/api";
import type { Decision, Inspection, InspectionDetail, InspectionImage, RuleCatalogue, Stage, User } from "../types/inspection";

export const useInspections = (scope: "mine" | "all" = "mine", officerId?: string, q?: string) =>
    useQuery({
        queryKey: ["inspections", scope, officerId ?? null, q ?? ""],
        queryFn: async () => {
            const params = new URLSearchParams({ scope });
            if (officerId) params.set("officer_id", officerId);
            if (q?.trim()) params.set("q", q.trim());
            return (await api.get<Inspection[]>(`/inspections?${params}`)).data;
        },
    });

export const useOfficers = (enabled = true) =>
    useQuery({
        queryKey: ["officers"],
        enabled,
        queryFn: async () => (await api.get<User[]>("/inspections/officers/list")).data,
    });

export const useRules = () =>
    useQuery({
        queryKey: ["rules"],
        staleTime: Infinity,
        queryFn: async () => (await api.get<RuleCatalogue>("/rules")).data,
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

export const useAssign = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (body: { id: string; officer_id: string | null }) =>
            (await api.patch<Inspection>(`/inspections/${body.id}/assign`, { officer_id: body.officer_id })).data,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inspections"] }),
    });
};

export const useUpdateCard = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (body: { id: string; stage?: Stage; note?: string }) =>
            (await api.patch<Inspection>(`/inspections/${body.id}/card`, { stage: body.stage, note: body.note })).data,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inspections"] }),
    });
};

export const useProcess = (id: string | undefined) =>
    useInspectionMutation(id, async () =>
        (await api.post<InspectionDetail>(`/inspections/${id}/process`)).data,
    );

export const useReviewFinding = (id: string | undefined) =>
    useInspectionMutation(id, async (body: { ruleId: string; decision: Decision | null; note?: string }) =>
        (await api.put<InspectionDetail>(`/inspections/${id}/findings/${body.ruleId}`, {
            decision: body.decision,
            note: body.note,
        })).data,
    );

export const useReviseDeclarations = (id: string | undefined) =>
    useInspectionMutation(id, async (values: Record<string, string | null>) =>
        (await api.put<InspectionDetail>(`/inspections/${id}/declarations`, { values })).data,
    );

export const useFinalize = (id: string | undefined) =>
    useInspectionMutation(id, async () =>
        (await api.patch<InspectionDetail>(`/inspections/${id}/finalize`)).data,
    );

export const downloadReport = async (id: string, format: "pdf" | "docx") => {
    const response = await api.get(`/inspections/${id}/report`, {
        params: { format },
        responseType: "blob",
    });
    const disposition = response.headers["content-disposition"] ?? "";
    const match = /filename="?([^"]+)"?/.exec(disposition);
    const filename = match ? match[1] : `report.${format}`;
    const url = URL.createObjectURL(response.data as Blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
};
