/**
 * Small hand-rolled icon set. One consistent stroke weight (1.6), 24px grid,
 * currentColor throughout, so icons inherit whatever the surface colour is.
 */

const PATHS = {
    gauge: (
        <>
            <path d="M3.6 17a9 9 0 1 1 16.8 0" />
            <path d="m14.2 10.8-2.7 3.4" />
            <circle cx="12" cy="15.2" r="1.4" />
        </>
    ),
    columns: (
        <>
            <rect x="3" y="4" width="5.2" height="16" rx="1.6" />
            <rect x="9.4" y="4" width="5.2" height="11" rx="1.6" />
            <rect x="15.8" y="4" width="5.2" height="14" rx="1.6" />
        </>
    ),
    aperture: (
        <>
            <path d="M4 8.5h3.2l1.4-2.2h6.8L16.8 8.5H20a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-8a1 1 0 0 1 1-1Z" />
            <circle cx="12" cy="13.4" r="3.4" />
        </>
    ),
    upload: (
        <>
            <path d="M12 15.5V4.2" />
            <path d="m7.8 8.4 4.2-4.2 4.2 4.2" />
            <path d="M4 15.2v3.4a1.4 1.4 0 0 0 1.4 1.4h13.2a1.4 1.4 0 0 0 1.4-1.4v-3.4" />
        </>
    ),
    clock: (
        <>
            <circle cx="12" cy="12" r="8.4" />
            <path d="M12 7.2V12l3.2 1.9" />
        </>
    ),
    book: (
        <>
            <path d="M4 5.2A1.6 1.6 0 0 1 5.6 3.6H19a1 1 0 0 1 1 1v13.2" />
            <path d="M4 5.2v13.4A1.8 1.8 0 0 0 5.8 20.4H20" />
            <path d="M7.6 8.2h8.2M7.6 11.6h5.6" />
        </>
    ),
    vault: (
        <>
            <rect x="3" y="4.4" width="18" height="15.2" rx="2" />
            <circle cx="12" cy="12" r="3.6" />
            <path d="M12 8.4v-1.4M12 17v-1.4M15.6 12H17M7 12h1.4" />
        </>
    ),
    stack: (
        <>
            <path d="m12 3.4 8.4 4.2-8.4 4.2L3.6 7.6 12 3.4Z" />
            <path d="m3.6 12 8.4 4.2 8.4-4.2" />
            <path d="m3.6 16.4 8.4 4.2 8.4-4.2" />
        </>
    ),
    bolt: <path d="M12.8 3.2 5.6 13.4h5.2l-.8 7.4 7.4-10.4h-5.4l.8-7.2Z" />,
    check: (
        <>
            <circle cx="12" cy="12" r="8.4" />
            <path d="m8.4 12.2 2.5 2.5 4.7-5" />
        </>
    ),
    flag: (
        <>
            <path d="M5.6 21V3.8" />
            <path d="M5.6 4.6h11.6l-2 3.6 2 3.6H5.6" />
        </>
    ),
    spark: (
        <>
            <path d="M12 3.4l1.9 5.1 5.1 1.9-5.1 1.9L12 17.4l-1.9-5.1L5 10.4l5.1-1.9L12 3.4Z" />
        </>
    ),
    sun: (
        <>
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2.8v2M12 19.2v2M4.6 4.6l1.5 1.5M17.9 17.9l1.5 1.5M2.8 12h2M19.2 12h2M4.6 19.4l1.5-1.5M17.9 6.1l1.5-1.5" />
        </>
    ),
    moon: <path d="M20 14.2A8.2 8.2 0 0 1 9.8 4a8.4 8.4 0 1 0 10.2 10.2Z" />,
    lines: (
        <>
            <path d="M5 7h14M5 12h14M5 17h9" />
        </>
    ),
    alert: (
        <>
            <path d="M12 4.2 3.6 19.2h16.8L12 4.2Z" />
            <path d="M12 10v4.2" />
            <path d="M12 16.8h.01" />
        </>
    ),
    search: (
        <>
            <circle cx="11" cy="11" r="6.2" />
            <path d="m16 16 4 4" />
        </>
    ),
    exit: (
        <>
            <path d="M9.6 20.4H5.4A1.4 1.4 0 0 1 4 19V5a1.4 1.4 0 0 1 1.4-1.4h4.2" />
            <path d="M15.4 16.2 19.6 12l-4.2-4.2" />
            <path d="M19.6 12H9.2" />
        </>
    ),
} as const;

export type IconName = keyof typeof PATHS;

type Props = {
    name: IconName;
    size?: number;
    className?: string;
};

const Icon = ({ name, size = 18, className }: Props) => (
    <svg
        className={className}
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={1.6}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
        focusable="false"
    >
        {PATHS[name]}
    </svg>
);

export default Icon;
