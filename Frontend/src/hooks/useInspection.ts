import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../apis/api";
import type {
    ApplicableRule,
    Declaration,
    Finding,
    ImageOcr,
    Inspection,
    InspectionDetail,
    InspectionImage,
    Product,
    ReportPayload,
    AuditEntry,
} from "../types/inspection";

export const useInspections = () =>
    useQuery({
        queryKey: ["inspections"],
        queryFn: async () => (await api.get<Inspection[]>("/inspections")).data,
        staleTime: 1000 * 30,
    });

export const useInspection = (id: string | undefined, refetchInterval?: number) =>
    useQuery({
        queryKey: ["inspection", id],
        enabled: Boolean(id),
        queryFn: async () => (await api.get<InspectionDetail>(`/inspections/${id}`)).data,
        refetchInterval,
    });

export const useOcr = (id: string | undefined, enabled = true) =>
    useQuery({
        queryKey: ["ocr", id],
        enabled: Boolean(id) && enabled,
        queryFn: async () => (await api.get<ImageOcr[]>(`/inspections/${id}/ocr`)).data,
    });

export const useDeclarations = (id: string | undefined, enabled = true) =>
    useQuery({
        queryKey: ["declarations", id],
        enabled: Boolean(id) && enabled,
        queryFn: async () => (await api.get<Declaration[]>(`/inspections/${id}/declarations`)).data,
    });

export const useRules = (id: string | undefined, enabled = true) =>
    useQuery({
        queryKey: ["rules", id],
        enabled: Boolean(id) && enabled,
        queryFn: async () => (await api.get<ApplicableRule[]>(`/inspections/${id}/rules`)).data,
    });

export const useFindings = (id: string | undefined, enabled = true) =>
    useQuery({
        queryKey: ["findings", id],
        enabled: Boolean(id) && enabled,
        queryFn: async () => (await api.get<Finding[]>(`/inspections/${id}/findings`)).data,
    });

export const useAuditTrail = (id: string | undefined, enabled = true) =>
    useQuery({
        queryKey: ["audit", id],
        enabled: Boolean(id) && enabled,
        queryFn: async () => (await api.get<AuditEntry[]>(`/inspections/${id}/audit`)).data,
    });

export const useReport = (id: string | undefined) =>
    useQuery({
        queryKey: ["report", id],
        enabled: Boolean(id),
        queryFn: async () => (await api.get<ReportPayload>(`/inspections/${id}/report`)).data,
    });

const useInspectionMutation = <TVariables, TData>(
    id: string | undefined,
    request: (variables: TVariables) => Promise<TData>,
    keys: string[],
) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: request,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["inspection", id] });
            for (const key of keys) queryClient.invalidateQueries({ queryKey: [key, id] });
        },
    });
};

export const useCreateInspection = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (body: { title?: string; location?: string }) =>
            (await api.post<Inspection>("/inspections", body)).data,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inspections"] }),
    });
};

export const useUploadImages = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (files: File[]) => {
            const form = new FormData();
            for (const file of files) form.append("files", file);
            return (await api.post<InspectionImage[]>(`/inspections/${id}/images`, form)).data;
        },
        ["images"],
    );

export const useDeleteImage = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (imageId: string) => (await api.delete(`/inspections/${id}/images/${imageId}`)).data,
        ["images"],
    );

export const useReorderImages = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (imageIds: string[]) =>
            (await api.patch(`/inspections/${id}/images/order`, { image_ids: imageIds })).data,
        ["images"],
    );

export const useReviewImage = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (body: { imageId: string; usability: string; review_note?: string; panel?: string }) =>
            (
                await api.patch(`/inspections/${id}/images/${body.imageId}`, {
                    usability: body.usability,
                    review_note: body.review_note,
                    panel: body.panel,
                })
            ).data,
        ["images"],
    );

export const useVerifyImages = (id: string | undefined) =>
    useInspectionMutation(id, async () => (await api.post(`/inspections/${id}/verify-images`)).data, []);

export const useStartProcessing = (id: string | undefined) =>
    useInspectionMutation(id, async () => (await api.post(`/inspections/${id}/process`)).data, []);

export const useEditDeclarations = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (edits: { fact_path: string; human_value: unknown; verification_status: string }[]) =>
            (await api.patch<Declaration[]>(`/inspections/${id}/declarations`, { edits })).data,
        ["declarations", "audit"],
    );

export const useConfirmDeclarations = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async () => (await api.post(`/inspections/${id}/declarations/confirm`)).data,
        ["declarations", "rules", "findings", "audit"],
    );

export const useOverrideProduct = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (body: { tags: string[]; category?: string; physical_state?: string }) =>
            (await api.patch<Product>(`/inspections/${id}/product`, body)).data,
        ["rules", "findings", "audit"],
    );

export const useDecideRules = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (decisions: { rule_id: string; rule_version: number; officer_decision: string; officer_note?: string }[]) =>
            (await api.patch<ApplicableRule[]>(`/inspections/${id}/rules`, { decisions })).data,
        ["rules", "audit"],
    );

export const useDecideFinding = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (body: { findingId: string; officer_decision: string; officer_reason?: string }) =>
            (
                await api.patch<Finding[]>(`/inspections/${id}/findings/${body.findingId}`, {
                    officer_decision: body.officer_decision,
                    officer_reason: body.officer_reason,
                })
            ).data,
        ["findings", "rules", "audit"],
    );

export const useFinalize = (id: string | undefined) =>
    useInspectionMutation(
        id,
        async (body: { inspector_observations?: string }) =>
            (await api.post<Inspection>(`/inspections/${id}/finalize`, body)).data,
        ["findings", "report", "audit"],
    );
