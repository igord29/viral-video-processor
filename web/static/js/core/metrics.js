export async function withTiming(label, fn) {
    const start = performance.now();
    const result = await fn();
    const durationMs = performance.now() - start;
    return { label, result, durationMs };
}

export function formatDurationMs(durationMs) {
    const safeMs = Number.isFinite(durationMs) ? durationMs : 0;
    if (safeMs < 1000) {
        return `${safeMs.toFixed(0)}ms`;
    }
    return `${(safeMs / 1000).toFixed(2)}s`;
}
