import { useCallback, useEffect, useState } from "react";

export type Theme = "light" | "dark";

const read = (): Theme => {
    if (typeof document === "undefined") return "light";
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
};

/**
 * Theme lives on <html data-theme>, set by the inline script in index.html before
 * first paint. This hook keeps React in sync with it and persists the choice.
 */
const useTheme = () => {
    const [theme, setTheme] = useState<Theme>(read);

    useEffect(() => {
        document.documentElement.setAttribute("data-theme", theme);
        try {
            localStorage.setItem("theme", theme);
        } catch {
            // Private browsing can refuse writes. The theme still applies for this session.
        }
    }, [theme]);

    const toggle = useCallback(() => {
        setTheme((current) => (current === "dark" ? "light" : "dark"));
    }, []);

    return { theme, setTheme, toggle };
};

export default useTheme;
