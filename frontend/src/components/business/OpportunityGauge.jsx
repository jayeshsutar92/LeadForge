export default function OpportunityGauge({ score = 0, tier = "LOW", size = 120 }) {
    const radius = 45;
    const circ = 2 * Math.PI * radius;
    const pct = Math.min(100, Math.max(0, score));
    const offset = circ - (pct / 100) * circ;

    const color =
        tier === "HIGH" ? "hsl(76 100% 54%)" :
            tier === "MEDIUM" ? "hsl(186 100% 50%)" :
                "hsl(215 20% 65%)";

    return (
        <div className="score-ring inline-flex items-center justify-center relative" style={{ width: size, height: size }}>
            <svg width={size} height={size} viewBox="0 0 100 100" className="-rotate-90">
                <circle cx="50" cy="50" r={radius} stroke="hsl(231 20% 22%)" strokeWidth="6" fill="none" />
                <circle
                    cx="50" cy="50" r={radius}
                    className="progress"
                    stroke={color}
                    strokeWidth="6"
                    strokeLinecap="round"
                    fill="none"
                    strokeDasharray={circ}
                    strokeDashoffset={offset}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="font-display text-2xl font-medium leading-none" data-testid="score-value">{pct}</div>
                <div className="text-[9px] tracking-[0.2em] uppercase text-muted-foreground mt-1">{tier}</div>
            </div>
        </div>
    );
}
