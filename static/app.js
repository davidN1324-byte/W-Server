function getToken() {
    return sessionStorage.getItem('access_token') || '';
}

function submitToken() {
    const token = document.getElementById('tokenInput').value.trim();
    if (!token) return;
    sessionStorage.setItem('access_token', token);
    verifyToken(token);
}

async function verifyToken(token) {
    const res = await fetch('/files', {
        headers: { 'X-Access-Token': token }
    });
    if (res.ok) {
        document.getElementById('tokenGate').style.display = 'none';
        document.querySelector('header').style.display = '';
        document.querySelector('main').style.display = '';
        resetSessionTimer();
        loadFiles();
        startAutoRefresh();
    } else {
        sessionStorage.removeItem('access_token');
        document.getElementById('tokenInput').value = '';
        document.getElementById('tokenError').style.display = 'block';
    }
}

function toggleTokenVisibility() {
    const input = document.getElementById('tokenInput');
    const btn = document.getElementById('toggleBtn');
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'Hide';
    } else {
        input.type = 'password';
        btn.textContent = 'Show';
    }
}

function updateFileInfo() {
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    if (fileInput.files[0]) {
        fileName.textContent = fileInput.files[0].name;
        fileInfo.style.display = 'block';
    } else {
        fileInfo.style.display = 'none';
    }
}

function uploadFile(event) {
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file to upload.');
        return false;
    }

    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    progressContainer.style.display = 'flex';
    progressBar.value = 0;
    progressText.textContent = '0%';

    xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
            const pct = Math.round((e.loaded / e.total) * 100);
            progressBar.value = pct;
            progressText.textContent = pct + '%';
        }
    };

    xhr.onload = () => {
        progressContainer.style.display = 'none';
        const result = JSON.parse(xhr.responseText);
        if (xhr.status === 200) {
            loadFiles();
            fileInput.value = '';
            document.getElementById('fileInfo').style.display = 'none';
            showMessage('File uploaded successfully!', '#0f0');
        } else if (xhr.status === 403) {
            sessionStorage.removeItem('access_token');
            location.reload();
        } else {
            showMessage('Upload error: ' + result.detail, 'red');
        }
    };

    xhr.onerror = () => {
        progressContainer.style.display = 'none';
        showMessage('Network error.', 'red');
    };

    xhr.open('POST', '/upload');
    xhr.setRequestHeader('X-Access-Token', getToken());
    xhr.send(formData);
    return false;
}

function showMessage(text, color) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.style.color = color;
    msg.style.display = 'block';
    setTimeout(() => { msg.style.display = 'none'; }, 4000);
}

let previousFileCount = null;

async function loadFiles() {
    try {
        const response = await fetch('/files', {
            headers: { 'X-Access-Token': getToken() }
        });

        if (response.status === 403) {
            sessionStorage.removeItem('access_token');
            location.reload();
            return;
        }

        const result = await response.json();
        const files = result.files;
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';

        files.forEach(file => {
            const row = document.createElement('tr');

            const nameCell = document.createElement('td');
            nameCell.textContent = file.original;
            row.appendChild(nameCell);

            const sizeCell = document.createElement('td');
            sizeCell.textContent = file.size || '—';
            row.appendChild(sizeCell);

            const downloadCell = document.createElement('td');
            const downloadLink = document.createElement('a');
            downloadLink.href = '/download/' + file.stored;
            downloadLink.textContent = 'Download';
            downloadCell.appendChild(downloadLink);
            row.appendChild(downloadCell);

            const deleteCell = document.createElement('td');
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.onclick = () => deleteFile(file.stored);
            deleteCell.appendChild(deleteButton);
            row.appendChild(deleteCell);

            fileList.appendChild(row);
        });

        updateStats(files);

        if (previousFileCount !== null) {
            if (files.length > previousFileCount) {
                showToast('🟢 New file available');
                flashTitle('🔔 New file!');
            } else if (files.length < previousFileCount) {
                showToast('🔴 File deleted');
                flashTitle('🗑 File deleted');
            }
        }
        previousFileCount = files.length;

    } catch (error) {
        console.error('Error loading file list:', error.message);
    }
}

function updateStats(files) {
    const stats = document.getElementById('fileStats');
    if (!stats) return;
    if (files.length === 0) {
        stats.textContent = '';
        return;
    }
    stats.textContent = `${files.length} file${files.length !== 1 ? 's' : ''}`;
}

function showToast(text) {
    const existing = document.getElementById('toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.textContent = text;
    document.body.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => toast.classList.add('toast-visible'));
    setTimeout(() => {
        toast.classList.remove('toast-visible');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

let flashInterval = null;
const originalTitle = document.title;

function flashTitle(message) {
    if (flashInterval) return;
    let alt = true;
    flashInterval = setInterval(() => {
        document.title = alt ? message : originalTitle;
        alt = !alt;
    }, 800);
    setTimeout(() => {
        clearInterval(flashInterval);
        flashInterval = null;
        document.title = originalTitle;
    }, 5000);
}

async function deleteFile(filename) {
    if (!confirm('Delete this file?')) return;
    try {
        const response = await fetch(`/delete/${filename}`, {
            method: 'DELETE',
            headers: { 'X-Access-Token': getToken() }
        });
        const result = await response.json();
        if (response.ok) {
            loadFiles();
            showMessage('File deleted.', '#0f0');
        } else if (response.status === 403) {
            sessionStorage.removeItem('access_token');
            location.reload();
        } else {
            showMessage('Delete error: ' + result.detail, 'red');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'red');
    }
}

function startAutoRefresh() {
    setInterval(() => {
        if (getToken()) loadFiles();
    }, 5000);
}

let sessionTimer;

function resetSessionTimer() {
    clearTimeout(sessionTimer);
    sessionTimer = setTimeout(() => {
        sessionStorage.removeItem('access_token');
        location.reload();
    }, 30 * 60 * 1000);
}

document.addEventListener('click', resetSessionTimer);
document.addEventListener('keypress', resetSessionTimer);

window.onload = () => {
    const token = getToken();
    if (token) {
        verifyToken(token);
    } else {
        document.getElementById('tokenGate').style.display = 'flex';
        document.querySelector('header').style.display = 'none';
        document.querySelector('main').style.display = 'none';
    }
};