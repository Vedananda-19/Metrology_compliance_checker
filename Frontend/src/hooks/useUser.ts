import { useQuery } from "@tanstack/react-query";
import api from "../apis/api";
import type { User } from "../types/inspection";

const useUser = () => {
    const token = localStorage.getItem("access_token");
    return useQuery({
        queryKey: ["user"],
        enabled: Boolean(token),
        queryFn: async () => (await api.get<User>("/auth/me")).data,
        retry: false,
        staleTime: 1000 * 60 * 5,
    });
};

export default useUser;
