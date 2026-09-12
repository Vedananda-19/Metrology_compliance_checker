export type Bar = {
    label: string;
    value: number;
};

type Props = {
    bars: Bar[];
    /** Bars at or above this count are tinted as the "attention" colour. */
    emphasise?: (bar: Bar) => boolean;
};

/** Round the axis up to a value that halves cleanly, so the mid tick is a whole number. */
const niceCeiling = (max: number) => {
    if (max <= 4) return 4;
    if (max <= 20) return Math.ceil(max / 2) * 2;
    const magnitude = 10 ** Math.floor(Math.log10(max));
    return Math.ceil(max / (magnitude / 2)) * (magnitude / 2);
};

const BarChart = ({ bars, emphasise }: Props) => {
    const peak = Math.max(...bars.map((bar) => bar.value), 0);
    const ceiling = niceCeiling(peak);
    const ticks = [ceiling, Math.round(ceiling * 0.5), 0];

    return (
        <div className="barChart">
            <div className="barAxis" aria-hidden="true">
                {ticks.map((tick) => (
                    <span key={tick}>{tick}</span>
                ))}
            </div>

            <div className="barPlot">
                <div className="barGrid" aria-hidden="true">
                    <span />
                    <span />
                    <span />
                </div>

                {bars.map((bar) => {
                    const height = ceiling ? (bar.value / ceiling) * 100 : 0;
                    return (
                        <div className="barSlot" key={bar.label}>
                            <div className="barTrack">
                                <div
                                    className={`barFill${emphasise?.(bar) ? " barFillAlert" : ""}`}
                                    style={{ height: `${Math.max(height, bar.value ? 4 : 0)}%` }}
                                >
                                    <span className="barValue">{bar.value}</span>
                                </div>
                            </div>
                            <span className="barLabel">{bar.label}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default BarChart;
