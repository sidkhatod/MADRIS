import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for dev
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface IngestResponse {
    status: string;
    snapshots_created: number;
}

export interface DecisionSupportResponse {
    top_risks: string[];
    recommended_actions: string[];
    explanation: string;
    historical_basis: {
        case_study_id: string;
        inferred_time_window: string;
        excerpt: string;
        similarity_score: number;
    }[];
}

export interface PastDisaster {
    case_study_id: string;
    similarity_score: number;
    decision_context: string;
    risks_perceived: string[];
    action_taken_narrative: string;
    location_context: string;
    [key: string]: any;
}
