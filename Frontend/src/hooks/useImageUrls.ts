import { useEffect, useState } from "react";
import api from "../apis/api";
import type { InspectionImage } from "../types/inspection";

const useImageUrls = (inspectionId: string | undefined, images: InspectionImage[] | undefined) => {
    const [urls, setUrls] = useState<Record<string, string>>({});

    const signature = (images ?? []).map((image) => image.id).join(",");

    useEffect(() => {
        if (!inspectionId || !images?.length) return;
        let cancelled = false;
        const created: string[] = [];

        const load = async () => {
            const entries: Record<string, string> = {};
            for (const image of images) {
                try {
                    const response = await api.get(`/inspections/${inspectionId}/images/${image.id}/file`, {
                        responseType: "blob",
                    });
                    const objectUrl = URL.createObjectURL(response.data);
                    created.push(objectUrl);
                    entries[image.id] = objectUrl;
                } catch {
                    entries[image.id] = "";
                }
            }
            if (!cancelled) setUrls(entries);
        };

        load();
        return () => {
            cancelled = true;
            for (const url of created) URL.revokeObjectURL(url);
        };
    }, [inspectionId, signature]);

    return urls;
};

export default useImageUrls;
