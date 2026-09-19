import { createContext, useCallback, useContext, useState, type ReactNode } from "react";

type Variant = "success" | "error" | "info";
type Toast = { id: number; message: string; variant: Variant };

type ToastApi = {
    notify: (message: string, variant?: Variant) => void;
    success: (message: string) => void;
    error: (message: string) => void;
};

const ToastContext = createContext<ToastApi | null>(null);

let nextId = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const dismiss = useCallback((id: number) => {
        setToasts((current) => current.filter((toast) => toast.id !== id));
    }, []);

    const notify = useCallback(
        (message: string, variant: Variant = "info") => {
            const id = nextId++;
            setToasts((current) => [...current, { id, message, variant }]);
            window.setTimeout(() => dismiss(id), 4500);
        },
        [dismiss],
    );

    const api: ToastApi = {
        notify,
        success: (message) => notify(message, "success"),
        error: (message) => notify(message, "error"),
    };

    return (
        <ToastContext.Provider value={api}>
            {children}
            <div className="toastStack" role="status" aria-live="polite">
                {toasts.map((toast) => (
                    <div key={toast.id} className={`toast toast--${toast.variant}`} onClick={() => dismiss(toast.id)}>
                        <span>{toast.message}</span>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}

export function useToast(): ToastApi {
    const context = useContext(ToastContext);
    if (!context) throw new Error("useToast must be used inside a ToastProvider");
    return context;
}
