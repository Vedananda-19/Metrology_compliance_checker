import { useQuery } from "@tanstack/react-query";
import api from "../apis/api";
import type { User } from "../types/inspection";

const useUser = () =>
    useQuery({
        queryKey: ["user"],
        queryFn: async () => {
            if (!localStorage.getItem("access_token")) return null;
            return (await api.get<User>("/auth/me")).data;
        },
        retry: false,
        staleTime: 1000 * 60 * 5,
    });

export default useUser;
