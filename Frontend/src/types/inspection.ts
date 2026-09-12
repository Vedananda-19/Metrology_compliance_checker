export type InspectionStatus = "DRAFT" | "PROCESSING" | "COMPLETED" | "FAILED";

export type FindingStatus = "COMPLIANT" | "NON_COMPLIANT" | "NOT_VERIFIABLE";

export interface User {
    id: string;
    username: string;
    full_name: string | null;
}

export interface InspectionImage {
    id: string;
    display_order: number;
    original_filename: string | null;
}

export interface OcrText {
    id: string;
    image_id: string | null;
    display_order: number;
    text: string;
}

export interface Declaration {
    field: string;
    value: string | null;
    confidence: number | null;
}

export interface Finding {
    rule_ref: string;
    requirement: string;
    status: FindingStatus;
    severity: string;
    observed: string | null;
    explanation: string;
    confidence: number;
}

export interface Evaluation {
    verdict: string | null;
    result: {
        verdict?: string;
        summary?: string;
        findings?: Finding[];
    };
}

export interface Inspection {
    id: string;
    reference: string;
    title: string | null;
    status: InspectionStatus;
    error: string | null;
    created_at: string | null;
}

export interface InspectionDetail extends Inspection {
    images: InspectionImage[];
    ocr_texts: OcrText[];
    declarations: Declaration[];
    evaluation: Evaluation | null;
}

export const FIELD_LABELS: Record<string, string> = {
    product_name: "Product name",
    brand_name: "Brand name",
    common_or_generic_name: "Common or generic name",
    manufacturer_name: "Manufacturer name",
    manufacturer_address: "Manufacturer address",
    packer_name: "Packer name",
    importer_name: "Importer name",
    country_of_origin: "Country of origin",
    net_quantity: "Net quantity",
    mrp: "Retail sale price",
    manufacturing_date: "Month and year of manufacture",
    consumer_care_name: "Consumer care name",
    consumer_care_address: "Consumer care address",
    consumer_care_phone: "Consumer care telephone",
    consumer_care_email: "Consumer care email",
    dimensions: "Dimensions",
};
