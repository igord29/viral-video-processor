export class ApiError extends Error {
    constructor(message, { status = 0, endpoint = '', details = null } = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.endpoint = endpoint;
        this.details = details;
    }
}

const DEFAULT_TIMEOUT_MS = 15000;

function withTimeout(promise, timeoutMs, endpoint) {
    let timeoutId;
    const timeoutPromise = new Promise((_, reject) => {
        timeoutId = setTimeout(() => {
            reject(new ApiError('Request timed out', { status: 408, endpoint }));
        }, timeoutMs);
    });

    return Promise.race([promise, timeoutPromise]).finally(() => clearTimeout(timeoutId));
}

async function parseJson(response, endpoint) {
    try {
        return await response.json();
    } catch {
        throw new ApiError('Invalid JSON response', { status: response.status, endpoint });
    }
}

export async function fetchJson(endpoint, options = {}) {
    const { timeoutMs = DEFAULT_TIMEOUT_MS, ...fetchOptions } = options;
    const response = await withTimeout(
        fetch(endpoint, {
            ...fetchOptions,
            headers: {
                'Content-Type': 'application/json',
                ...fetchOptions.headers
            }
        }),
        timeoutMs,
        endpoint
    );

    if (!response.ok) {
        const body = await parseJson(response, endpoint).catch(() => null);
        throw new ApiError(body?.error || `HTTP ${response.status}`, {
            status: response.status,
            endpoint,
            details: body
        });
    }

    return parseJson(response, endpoint);
}

function ensureString(value, fallback = '') {
    return typeof value === 'string' ? value : fallback;
}

function ensureNumber(value, fallback = 0) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : fallback;
}

function ensureBoolean(value, fallback = false) {
    return typeof value === 'boolean' ? value : fallback;
}

function normalizeVideo(item) {
    const safeItem = item && typeof item === 'object' ? item : {};
    return {
        name: ensureString(safeItem.name, 'Untitled'),
        path: ensureString(safeItem.path, ''),
        size: ensureNumber(safeItem.size, 0),
        modified: ensureNumber(safeItem.modified, 0),
        folder: ensureString(safeItem.folder, 'Unknown')
    };
}

export async function getConfig() {
    const data = await fetchJson('/api/config');
    return {
        downloadPath: ensureString(data.download_path),
        videoPath: ensureString(data.video_path),
        clipsPath: ensureString(data.clips_path),
        maxClipDuration: ensureNumber(data.max_clip_duration, 0),
        minClipDuration: ensureNumber(data.min_clip_duration, 0),
        topClips: ensureNumber(data.top_n_clips, 0),
        hasAnthropicKey: ensureBoolean(data.has_anthropic_key, false),
        audioSpikeThreshold: ensureNumber(data.audio_spike_threshold, 0),
        sceneChangeThreshold: ensureNumber(data.scene_change_threshold, 0)
    };
}

export async function getVideos() {
    const data = await fetchJson('/api/videos');
    const videos = Array.isArray(data.videos) ? data.videos.map(normalizeVideo) : [];
    return { videos };
}

export async function deleteVideo(path) {
    if (!path) {
        throw new ApiError('Missing video path', { status: 400, endpoint: '/api/delete-video' });
    }
    return fetchJson('/api/delete-video', {
        method: 'POST',
        body: JSON.stringify({ path })
    });
}

export async function openFolder() {
    return fetchJson('/api/open-folder', {
        method: 'POST',
        body: JSON.stringify({})
    });
}
