export type InspectionStatus = "DRAFT" | "PROCESSING" | "COMPLETED" | "FAILED";

export type FindingStatus = "COMPLIANT" | "NON_COMPLIANT" | "NOT_VERIFIABLE" | "EXEMPT" | "OBSERVATION";

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
    rule_id: string;
    rule_ref: string;
    requirement: string;
    status: FindingStatus;
    severity: string;
    verification_mode: string;
    threshold_source: string;
    observed: string | null;
    explanation: string;
}

export interface Evaluation {
    verdict: string | null;
    result: {
        verdict?: string;
        summary?: string;
        rule_set_version?: string;
        rules_evaluated?: number;
        counts?: Record<string, number>;
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
    "product.name": "Product name",
    "product.brand": "Brand name",
    "product.common_name": "Common or generic name",
    "manufacturer.name": "Manufacturer name",
    "manufacturer.address.text": "Manufacturer address",
    "manufacturer.role_qualified": "Declared with a 'Manufactured by' qualifier",
    "packer.name": "Packer name",
    "packer.address.text": "Packer address",
    "importer.name": "Importer name",
    "importer.address.text": "Importer address",
    "product.country_of_manufacture": "Country of origin",
    "net_quantity.text": "Net quantity declaration",
    "net_quantity.value": "Net quantity value",
    "net_quantity.unit": "Net quantity unit",
    "mrp.text": "Retail sale price declaration",
    "mrp.value": "Retail sale price value",
    "date_of_manufacture.month": "Month of manufacture",
    "date_of_manufacture.year": "Year of manufacture",
    "consumer_care.name": "Consumer care name",
    "consumer_care.address": "Consumer care address",
    "consumer_care.phone": "Consumer care telephone",
    "consumer_care.email": "Consumer care email",
    "dimensions.text": "Dimensions declaration",
    "sheets.count": "Number of sheets",
};
