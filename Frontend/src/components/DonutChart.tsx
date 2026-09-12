export type Segment = {
    label: string;
    value: number;
    /** Any CSS colour — pass a var(--token) so it follows the theme. */
    color: string;
};

type Props = {
    segments: Segment[];
    /** Shown in the middle of the ring. Defaults to the summed total. */
    centerLabel?: string;
    caption?: string;
};

const SIZE = 132;
const STROKE = 17;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
// 2px visual gap between adjacent arcs, expressed in path length.
const GAP = 2;

const DonutChart = ({ segments, centerLabel, caption }: Props) => {
    const shown = segments.filter((segment) => segment.value > 0);
    const total = shown.reduce((sum, segment) => sum + segment.value, 0);

    // Walk the ring once up front so rendering stays a pure map.
    const arcs = shown.reduce<{ segment: Segment; start: number; length: number }[]>((acc, segment) => {
        const previous = acc[acc.length - 1];
        const start = previous ? previous.start + previous.length : 0;
        return [...acc, { segment, start, length: (segment.value / total) * CIRCUMFERENCE }];
    }, []);

    return (
        <div className="donut">
            <div className="donutRing">
                <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} role="img" aria-label={caption}>
                    <circle
                        cx={SIZE / 2}
                        cy={SIZE / 2}
                        r={RADIUS}
                        fill="none"
                        stroke="var(--track)"
                        strokeWidth={STROKE}
                    />
                    {arcs.map(({ segment, start, length: portion }) => {
                        const length = Math.max(portion - GAP, 1);
                        const dash = `${length} ${CIRCUMFERENCE - length}`;
                        const rotation = (start / CIRCUMFERENCE) * 360 - 90;

                        return (
                            <circle
                                key={segment.label}
                                cx={SIZE / 2}
                                cy={SIZE / 2}
                                r={RADIUS}
                                fill="none"
                                stroke={segment.color}
                                strokeWidth={STROKE}
                                strokeDasharray={dash}
                                strokeLinecap="round"
                                transform={`rotate(${rotation} ${SIZE / 2} ${SIZE / 2})`}
                                className="donutArc"
                            />
                        );
                    })}
                </svg>
                <div className="donutCenter">
                    <strong>{centerLabel ?? total}</strong>
                    {caption && <span>{caption}</span>}
                </div>
            </div>

            <ul className="donutLegend">
                {segments.map((segment) => (
                    <li key={segment.label}>
                        <span className="donutDot" style={{ background: segment.color }} />
                        <span className="donutLegendLabel">{segment.label}</span>
                        <span className="donutLegendValue">
                            {total ? Math.round((segment.value / total) * 100) : 0}%
                        </span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DonutChart;
