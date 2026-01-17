export function clearChildren(element) {
    if (!element) return;
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

export function createElement(tag, { className, text, attrs, dataset } = {}) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    if (attrs) {
        Object.entries(attrs).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                element.setAttribute(key, value);
            }
        });
    }
    if (dataset) {
        Object.entries(dataset).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                element.dataset[key] = value;
            }
        });
    }
    return element;
}

export function renderEmptyState(container, { icon, title, message, actionLabel, onAction }) {
    if (!container) return;
    clearChildren(container);
    const wrapper = createElement('div', { className: 'empty-state' });
    if (icon) {
        const iconEl = createElement('i', { className: icon });
        wrapper.appendChild(iconEl);
    }
    if (title) {
        wrapper.appendChild(createElement('h3', { text: title }));
    }
    if (message) {
        wrapper.appendChild(createElement('p', { text: message }));
    }
    if (actionLabel && typeof onAction === 'function') {
        const actionButton = createElement('button', {
            className: 'btn btn-primary',
            text: actionLabel
        });
        actionButton.addEventListener('click', onAction);
        const actions = createElement('div', { className: 'state-actions' });
        actions.appendChild(actionButton);
        wrapper.appendChild(actions);
    }
    container.appendChild(wrapper);
}

export function renderErrorState(container, { title, message, onRetry }) {
    renderEmptyState(container, {
        icon: 'fas fa-exclamation-circle',
        title: title || 'Something went wrong',
        message: message || 'Please try again.',
        actionLabel: 'Retry',
        onAction: onRetry
    });
}
