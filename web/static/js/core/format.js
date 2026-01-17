export function formatDuration(seconds) {
    const totalSeconds = Number.isFinite(seconds) ? seconds : 0;
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const secs = Math.floor(totalSeconds % 60);

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

export function formatNumber(num) {
    const safeNum = Number.isFinite(num) ? num : 0;
    if (safeNum >= 1000000) return (safeNum / 1000000).toFixed(1) + 'M';
    if (safeNum >= 1000) return (safeNum / 1000).toFixed(1) + 'K';
    return safeNum.toString();
}

export function formatFileSize(bytes) {
    const safeBytes = Number.isFinite(bytes) ? bytes : 0;
    if (safeBytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(safeBytes) / Math.log(k));
    return parseFloat((safeBytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    if (Number.isNaN(date.getTime())) {
        return 'Unknown';
    }
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
}

export function formatShortTime(date) {
    if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
        return 'Unknown';
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
