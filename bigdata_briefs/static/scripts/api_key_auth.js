const API_KEY_STORAGE = 'bigdata_api_key';
const API_KEY_CHANGED_EVENT = 'bigdata-api-key-changed';

let apiKeyGateActive = false;

function getUserApiKey() {
    return localStorage.getItem(API_KEY_STORAGE) || '';
}

function setUserApiKey(key) {
    const trimmed = (key || '').trim();
    if (trimmed) {
        localStorage.setItem(API_KEY_STORAGE, trimmed);
    } else {
        localStorage.removeItem(API_KEY_STORAGE);
    }
    window.dispatchEvent(new CustomEvent(API_KEY_CHANGED_EVENT));
}

function hasUserApiKey() {
    return Boolean(getUserApiKey());
}

async function isApiKeyAvailable() {
    if (hasUserApiKey()) {
        return true;
    }
    try {
        const response = await fetch('/api/config');
        if (response.ok) {
            const data = await response.json();
            return data.bigdata_api_key_configured === true;
        }
    } catch (_) {
        // Fall through to gate
    }
    return false;
}

async function apiRequest(url, options = {}) {
    const apiKey = getUserApiKey();
    const headers = { ...(options.headers || {}) };
    if (apiKey) {
        headers['X-API-KEY'] = apiKey;
    }
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        openApiKeySettings(true);
        let message = 'API key required';
        try {
            const data = await response.json();
            message = data.detail?.message || data.message || message;
        } catch (_) {
            // Keep default message
        }
        throw new Error(message);
    }
    return response;
}

function updateApiKeyStatus() {
    const status = document.getElementById('apiKeyStatus');
    if (!status) {
        return;
    }
    if (hasUserApiKey()) {
        status.textContent = '✓ API key saved in this browser';
        status.className = 'text-sm text-green-400 mt-2';
    } else {
        status.textContent = 'Enter your Bigdata.com API key below.';
        status.className = 'text-sm text-gray-400 mt-2';
    }
}

function openApiKeySettings(isGate = false) {
    apiKeyGateActive = isGate;
    const overlay = document.getElementById('settingsOverlay');
    const description = document.getElementById('settingsApiKeyDescription');
    const cancelBtn = document.querySelector('.btn-close-settings');
    const input = document.getElementById('settingsApiKey');

    if (description) {
        description.textContent = isGate
            ? 'Enter your Bigdata.com API key to continue. The brief UI will be available after you save.'
            : 'Enter your Bigdata.com API key to authenticate requests to Bigdata.com.';
    }
    if (cancelBtn) {
        cancelBtn.style.display = isGate ? 'none' : 'inline-flex';
    }
    if (input) {
        input.value = getUserApiKey();
    }
    updateApiKeyStatus();
    if (overlay) {
        overlay.classList.add('visible');
    }
}

function closeApiKeySettings() {
    if (apiKeyGateActive) {
        return;
    }
    const overlay = document.getElementById('settingsOverlay');
    if (overlay) {
        overlay.classList.remove('visible');
    }
}

function revealAppContent() {
    const appContent = document.getElementById('appContent');
    if (appContent) {
        appContent.style.display = 'block';
    }
}

function saveApiKey() {
    const input = document.getElementById('settingsApiKey');
    const key = input ? input.value : '';
    if (!key.trim()) {
        updateApiKeyStatus();
        return;
    }
    setUserApiKey(key);
    updateApiKeyStatus();
    const wasGate = apiKeyGateActive;
    apiKeyGateActive = false;
    const overlay = document.getElementById('settingsOverlay');
    if (overlay) {
        overlay.classList.remove('visible');
    }
    const cancelBtn = document.querySelector('.btn-close-settings');
    if (cancelBtn) {
        cancelBtn.style.display = 'inline-flex';
    }
    if (wasGate) {
        revealAppContent();
    }
}

function clearApiKey() {
    const input = document.getElementById('settingsApiKey');
    if (input) {
        input.value = '';
    }
    setUserApiKey('');
    updateApiKeyStatus();
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('settingsApiKey');
    const button = document.getElementById('toggleApiKeyVisibility');
    if (!input || !button) {
        return;
    }
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    button.textContent = show ? 'Hide' : 'Show';
}

document.addEventListener('DOMContentLoaded', async function () {
    const overlay = document.getElementById('settingsOverlay');
    if (overlay) {
        overlay.addEventListener('click', function (event) {
            if (event.target === overlay && !apiKeyGateActive) {
                closeApiKeySettings();
            }
        });
    }

    const saveBtn = document.querySelector('.btn-save-key');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveApiKey);
    }
    const clearBtn = document.querySelector('.btn-clear-key');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearApiKey);
    }
    const closeBtn = document.querySelector('.btn-close-settings');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeApiKeySettings);
    }
    const toggleBtn = document.getElementById('toggleApiKeyVisibility');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleApiKeyVisibility);
    }
    const navApiKeyBtn = document.getElementById('navApiKeyBtn');
    if (navApiKeyBtn) {
        navApiKeyBtn.addEventListener('click', function () {
            openApiKeySettings(false);
        });
    }

    const available = await isApiKeyAvailable();
    if (available) {
        revealAppContent();
    } else {
        openApiKeySettings(true);
    }
});
