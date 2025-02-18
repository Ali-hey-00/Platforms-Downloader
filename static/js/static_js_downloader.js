class DownloadManager {
    constructor() {
        this.form = document.getElementById('downloadForm');
        this.urlInput = document.getElementById('instagramUrl');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.progressBar = document.getElementById('progressBar');
        this.progressBarFill = document.getElementById('progressBarFill');
        this.urlError = document.getElementById('urlError');
        this.downloadResult = document.getElementById('downloadResult');
        
        this.isDownloading = false;
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.urlInput.addEventListener('input', () => this.validateUrl());
    }

    validateUrl() {
        const url = this.urlInput.value.trim();
        const isValid = /^https?:\/\/(?:www\.)?instagram\.com\/(?:p|reel)\/[\w-]+\/?$/.test(url);
        
        this.urlError.style.display = isValid ? 'none' : 'block';
        this.urlError.textContent = isValid ? '' : 'Please enter a valid Instagram post or reel URL';
        this.downloadBtn.disabled = !isValid;
        
        return isValid;
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isDownloading || !this.validateUrl()) {
            return;
        }

        this.isDownloading = true;
        this.updateUI('downloading');

        try {
            const response = await this.downloadMedia();
            this.handleDownloadResponse(response);
        } catch (error) {
            this.handleError(error);
        } finally {
            this.isDownloading = false;
            this.updateUI('idle');
        }
    }

    async downloadMedia() {
        const formData = new FormData(this.form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch(this.form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
            },
            body: formData,
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    handleDownloadResponse(response) {
        if (response.status === 'success') {
            this.showDownloadLink(response.data);
        } else {
            this.showError(response.message || 'Download failed');
        }
    }

    handleError(error) {
        console.error('Download error:', error);
        this.showError('An error occurred while downloading. Please try again.');
    }

    updateUI(state) {
        this.downloadBtn.disabled = state === 'downloading';
        this.downloadBtn.textContent = state === 'downloading' ? 'Downloading...' : 'Download';
        this.progressBar.style.display = state === 'downloading' ? 'block' : 'none';
        
        if (state === 'downloading') {
            this.simulateProgress();
        }
    }

    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            if (this.isDownloading && progress < 90) {
                progress += Math.random() * 10;
                this.progressBarFill.style.width = `${Math.min(progress, 90)}%`;
            } else {
                clearInterval(interval);
                if (!this.isDownloading) {
                    this.progressBarFill.style.width = '100%';
                    setTimeout(() => {
                        this.progressBar.style.display = 'none';
                        this.progressBarFill.style.width = '0%';
                    }, 300);
                }
            }
        }, 500);
    }

    showDownloadLink(data) {
        this.downloadResult.innerHTML = `
            <div class="download-success">
                <p>Download ready! Click below to download:</p>
                <a href="${data.download_url}" 
                   class="download-link" 
                   download 
                   target="_blank"
                   rel="noopener noreferrer">
                    Download Media
                </a>
            </div>
        `;
    }

    showError(message) {
        this.downloadResult.innerHTML = `
            <div class="download-error">
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize download manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DownloadManager();
});