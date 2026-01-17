import { getConfig, getVideos } from '../core/api.js';
import { formatFileSize, formatDate, formatShortTime } from '../core/format.js';
import { renderEmptyState, renderErrorState, clearChildren, createElement } from '../core/dom.js';
import { showToast } from '../core/ui.js';
import { withTiming, formatDurationMs } from '../core/metrics.js';
import { storage } from '../core/storage.js';

const state = {
    videos: [],
    isLoading: false,
    lastRefreshMs: null,
    lastRefreshedAt: null,
    topClips: 0,
    totalCount: 0,
    error: null
};

const elements = {
    recentContainer: document.getElementById('recent-videos'),
    videoCount: document.getElementById('video-count'),
    topClips: document.getElementById('top-clips'),
    refreshLatency: document.getElementById('refresh-latency'),
    refreshTime: document.getElementById('refresh-time')
};

function setState(patch) {
    Object.assign(state, patch);
    render();
}

function render() {
    if (state.isLoading) {
        return;
    }

    if (elements.videoCount) {
        elements.videoCount.textContent = state.totalCount;
    }

    if (state.error) {
        renderErrorState(elements.recentContainer, {
            title: 'Unable to load recent videos',
            message: state.error,
            onRetry: loadRecentVideos
        });
        return;
    }

    if (!state.videos.length) {
        renderEmptyState(elements.recentContainer, {
            icon: 'fas fa-inbox',
            title: 'No videos yet',
            message: 'Start with a download and your library will show up here.',
            actionLabel: 'Download a video',
            onAction: () => {
                window.location.href = '/download';
            }
        });
        return;
    }

    clearChildren(elements.recentContainer);
    const list = createElement('div', { className: 'recent-video-list' });
    state.videos.forEach(video => {
        list.appendChild(createRecentVideoItem(video));
    });
    elements.recentContainer.appendChild(list);
}

function createRecentVideoItem(video) {
    const wrapper = createElement('div', { className: 'video-item' });
    wrapper.appendChild(createElement('i', { className: 'fas fa-file-video' }));

    const info = createElement('div', { className: 'video-info' });
    info.appendChild(createElement('div', { className: 'video-name', text: video.name }));
    info.appendChild(createElement('div', {
        className: 'video-meta',
        text: `${formatFileSize(video.size)} • ${formatDate(video.modified)}`
    }));
    wrapper.appendChild(info);

    const button = createElement('button', { className: 'btn-analyze' });
    const icon = createElement('i', { className: 'fas fa-chart-line' });
    button.appendChild(icon);
    button.appendChild(document.createTextNode(' Analyze'));
    button.addEventListener('click', () => analyzeVideo(video.path));
    wrapper.appendChild(button);

    return wrapper;
}

function analyzeVideo(videoPath) {
    if (!videoPath) {
        showToast('Missing video path', 'error');
        return;
    }
    storage.set('videoPath', videoPath);
    window.location.href = '/analyze';
}

async function loadConfig() {
    try {
        const { result } = await withTiming('config', () => getConfig());
        elements.topClips.textContent = result.topClips;
        setState({ topClips: result.topClips });
    } catch (error) {
        console.error('Error loading config:', error);
        showToast('Could not load settings', 'error');
    }
}

async function loadRecentVideos() {
    setState({ isLoading: true, error: null });
    try {
        const { result, durationMs } = await withTiming('videos', () => getVideos());
        const recentVideos = result.videos.slice(0, 5);
        setState({
            videos: recentVideos,
            totalCount: result.videos.length,
            lastRefreshMs: durationMs,
            lastRefreshedAt: new Date(),
            isLoading: false
        });

        if (elements.refreshLatency) {
            elements.refreshLatency.textContent = formatDurationMs(durationMs);
        }
        if (elements.refreshTime) {
            elements.refreshTime.textContent = formatShortTime(state.lastRefreshedAt);
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        setState({
            error: error.message || 'Please check your connection and try again.',
            isLoading: false
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadRecentVideos();
});
