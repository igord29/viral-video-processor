import { getConfig, getVideos, deleteVideo, openFolder } from '../core/api.js';
import { formatFileSize, formatDate } from '../core/format.js';
import { renderEmptyState, renderErrorState, clearChildren, createElement } from '../core/dom.js';
import { showToast } from '../core/ui.js';
import { withTiming, formatDurationMs } from '../core/metrics.js';
import { storage } from '../core/storage.js';

const state = {
    videos: [],
    isLoading: false,
    error: null,
    lastRefreshMs: null,
    lastRefreshedAt: null,
    currentVideoPath: null
};

const elements = {
    videosList: document.getElementById('videos-list'),
    videoCount: document.getElementById('video-count'),
    downloadsPath: document.getElementById('downloads-path'),
    videosPath: document.getElementById('videos-path'),
    refreshLatency: document.getElementById('refresh-latency')
};

function setState(patch) {
    Object.assign(state, patch);
    render();
}

function render() {
    if (state.isLoading) return;

    if (state.error) {
        renderErrorState(elements.videosList, {
            title: 'Unable to load videos',
            message: state.error,
            onRetry: loadVideos
        });
        return;
    }

    if (!state.videos.length) {
        renderEmptyState(elements.videosList, {
            icon: 'fas fa-video-slash',
            title: 'No videos yet',
            message: 'Download something and it will show up here.',
            actionLabel: 'Download video',
            onAction: () => {
                window.location.href = '/download';
            }
        });
        return;
    }

    clearChildren(elements.videosList);
    state.videos.forEach(video => {
        elements.videosList.appendChild(createVideoCard(video));
    });
}

function createVideoCard(video) {
    const card = createElement('div', { className: 'video-card' });
    card.addEventListener('click', () => previewVideo(video.name, video.path));

    const icon = createElement('div', { className: 'video-icon' });
    icon.appendChild(createElement('i', { className: 'fas fa-play' }));
    card.appendChild(icon);

    const details = createElement('div', { className: 'video-details' });
    details.appendChild(createElement('div', {
        className: 'video-title',
        text: video.name,
        attrs: { title: video.name }
    }));

    const meta = createElement('div', { className: 'video-meta' });
    meta.appendChild(createMetaItem('fas fa-hdd', formatFileSize(video.size)));
    meta.appendChild(createMetaItem('fas fa-clock', formatDate(video.modified)));
    meta.appendChild(createMetaItem('fas fa-folder', video.folder));
    details.appendChild(meta);
    card.appendChild(details);

    const actions = createElement('div', { className: 'video-actions' });
    actions.addEventListener('click', (event) => event.stopPropagation());

    const analyzeButton = createActionButton('btn btn-sm btn-primary', 'Analyze video', 'fas fa-chart-line', () => {
        analyzeVideo(video.path);
    });
    const previewButton = createActionButton('btn btn-sm btn-secondary', 'Preview video', 'fas fa-play', () => {
        previewVideo(video.name, video.path);
    });
    const deleteButton = createActionButton('btn btn-sm btn-danger', 'Delete video', 'fas fa-trash', () => {
        confirmDeleteVideo(video.path, video.name);
    });
    deleteButton.style.background = 'var(--error-color)';

    actions.appendChild(analyzeButton);
    actions.appendChild(previewButton);
    actions.appendChild(deleteButton);
    card.appendChild(actions);

    return card;
}

function createMetaItem(iconClass, text) {
    const wrapper = createElement('span');
    wrapper.appendChild(createElement('i', { className: iconClass }));
    wrapper.appendChild(document.createTextNode(` ${text}`));
    return wrapper;
}

function createActionButton(className, title, iconClass, onClick) {
    const button = createElement('button', { className, attrs: { title } });
    button.appendChild(createElement('i', { className: iconClass }));
    button.addEventListener('click', onClick);
    return button;
}

function previewVideo(name, path) {
    if (!path) return;
    state.currentVideoPath = path;
    const modal = document.getElementById('video-modal');
    const title = document.getElementById('modal-title');
    const player = document.getElementById('video-player');
    if (!modal || !title || !player) return;

    title.textContent = name;
    const filename = path.split(/[\\/]/).pop();
    player.src = `/api/video/${encodeURIComponent(filename)}`;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('video-modal');
    const player = document.getElementById('video-player');
    if (!modal || !player) return;
    modal.style.display = 'none';
    player.pause();
    player.src = '';
    state.currentVideoPath = null;
}

function analyzeCurrentVideo() {
    if (state.currentVideoPath) {
        analyzeVideo(state.currentVideoPath);
    }
}

function analyzeVideo(videoPath) {
    if (!videoPath) return;
    storage.set('videoPath', videoPath);
    window.location.href = '/analyze';
}

async function confirmDeleteVideo(path, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
        return;
    }
    try {
        const data = await deleteVideo(path);
        if (data.success) {
            showToast('Video deleted successfully', 'success');
            loadVideos();
        } else {
            showToast(data.error || 'Failed to delete video', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function openDownloadsFolder() {
    try {
        const data = await openFolder();
        if (data.success) {
            showToast('Folder opened in Explorer', 'success');
        } else {
            showToast(data.error || 'Failed to open folder', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function loadConfig() {
    try {
        const { result } = await withTiming('config', () => getConfig());
        if (elements.downloadsPath) {
            elements.downloadsPath.textContent = result.downloadPath || 'Not set';
        }
        if (elements.videosPath) {
            elements.videosPath.textContent = result.videoPath || 'Not set';
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

async function loadVideos() {
    setState({ isLoading: true, error: null });
    try {
        const { result, durationMs } = await withTiming('videos', () => getVideos());
        setState({
            videos: result.videos,
            isLoading: false,
            lastRefreshMs: durationMs,
            lastRefreshedAt: new Date()
        });

        if (elements.videoCount) {
            const count = result.videos.length;
            elements.videoCount.textContent = `${count} video${count !== 1 ? 's' : ''}`;
        }
        if (elements.refreshLatency) {
            elements.refreshLatency.textContent = formatDurationMs(durationMs);
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        setState({
            error: error.message || 'Please check your connection and try again.',
            isLoading: false
        });
    }
}

function refreshVideos() {
    loadVideos();
    showToast('Videos refreshed', 'success');
}

document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadVideos();
    const analyzeButton = document.getElementById('analyze-btn');
    if (analyzeButton) {
        analyzeButton.addEventListener('click', analyzeCurrentVideo);
    }
    const openButtons = document.querySelectorAll('[data-action="open-folder"], #open-folder-btn');
    openButtons.forEach(button => button.addEventListener('click', openDownloadsFolder));
    const refreshButton = document.getElementById('refresh-btn');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshVideos);
    }
    const closeButtons = document.querySelectorAll('[data-action="close-modal"]');
    closeButtons.forEach(button => button.addEventListener('click', closeModal));
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

const modal = document.getElementById('video-modal');
if (modal) {
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
}
