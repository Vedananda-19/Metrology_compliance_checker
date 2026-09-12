import axios from "axios";
import { queryClient } from "../main";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("access_token");
            queryClient.removeQueries({ queryKey: ["user"] });
        }
        return Promise.reject(error);
    },
);

export const errorMessage = (error: unknown, fallback = "Something went wrong") => {
    if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        if (typeof detail === "string") return detail;
    }
    return fallback;
};

export default api;
