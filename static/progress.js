/**
 * AI Progress Indicator System
 *
 * Shows real-time progress, time estimates, and streaming content for AI operations.
 */

class AIProgressIndicator {
    constructor() {
        this.startTime = null;
        this.estimatedDuration = 0;
        this.progressInterval = null;
        this.modal = null;
    }

    /**
     * Show progress modal for AI operation
     * @param {string} title - Operation title
     * @param {number} estimatedSeconds - Estimated duration in seconds
     * @returns {object} - Progress controller with update/complete/cancel methods
     */
    show(title, estimatedSeconds = 30) {
        this.startTime = Date.now();
        this.estimatedDuration = estimatedSeconds * 1000; // Convert to ms

        // Create modal
        this.modal = document.createElement('div');
        this.modal.className = 'ai-progress-modal';
        this.modal.innerHTML = `
            <div class="ai-progress-content">
                <div class="ai-progress-header">
                    <h3>${title}</h3>
                    <button class="ai-progress-cancel" title="Cancel">×</button>
                </div>
                <div class="ai-progress-body">
                    <div class="ai-progress-bar-container">
                        <div class="ai-progress-bar" style="width: 0%"></div>
                    </div>
                    <div class="ai-progress-stats">
                        <span class="ai-progress-percent">0%</span>
                        <span class="ai-progress-time">Estimated: ${estimatedSeconds}s</span>
                    </div>
                    <div class="ai-progress-status">Initializing...</div>
                    <div class="ai-progress-stream"></div>
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);

        // Start progress animation
        this.startProgressAnimation();

        // Return controller
        return {
            updateStatus: (status) => this.updateStatus(status),
            updateProgress: (percent) => this.updateProgress(percent),
            streamContent: (content) => this.streamContent(content),
            complete: () => this.complete(),
            cancel: () => this.cancel()
        };
    }

    startProgressAnimation() {
        const progressBar = this.modal.querySelector('.ai-progress-bar');
        const percentEl = this.modal.querySelector('.ai-progress-percent');
        const timeEl = this.modal.querySelector('.ai-progress-time');

        this.progressInterval = setInterval(() => {
            const elapsed = Date.now() - this.startTime;
            const progress = Math.min((elapsed / this.estimatedDuration) * 100, 95);

            progressBar.style.width = `${progress}%`;
            percentEl.textContent = `${Math.round(progress)}%`;

            const remaining = Math.max(0, this.estimatedDuration - elapsed) / 1000;
            if (remaining > 0) {
                timeEl.textContent = `~${Math.ceil(remaining)}s remaining`;
            } else {
                timeEl.textContent = 'Finishing up...';
            }
        }, 100);

        // Cancel button
        this.modal.querySelector('.ai-progress-cancel').addEventListener('click', () => {
            this.cancel();
        });
    }

    updateStatus(status) {
        if (this.modal) {
            this.modal.querySelector('.ai-progress-status').textContent = status;
        }
    }

    updateProgress(percent) {
        if (this.modal) {
            const progressBar = this.modal.querySelector('.ai-progress-bar');
            const percentEl = this.modal.querySelector('.ai-progress-percent');
            progressBar.style.width = `${percent}%`;
            percentEl.textContent = `${Math.round(percent)}%`;
        }
    }

    streamContent(content) {
        if (this.modal) {
            const streamEl = this.modal.querySelector('.ai-progress-stream');
            streamEl.textContent = content;
            // Auto-scroll
            streamEl.scrollTop = streamEl.scrollHeight;
        }
    }

    complete() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        if (this.modal) {
            // Show 100% complete
            const progressBar = this.modal.querySelector('.ai-progress-bar');
            const percentEl = this.modal.querySelector('.ai-progress-percent');
            progressBar.style.width = '100%';
            percentEl.textContent = '100%';
            this.modal.querySelector('.ai-progress-time').textContent = 'Complete!';
            this.modal.querySelector('.ai-progress-status').textContent = 'Done';

            // Auto-close after 1 second
            setTimeout(() => {
                this.modal.remove();
                this.modal = null;
            }, 1000);
        }
    }

    cancel() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        if (this.modal) {
            this.modal.remove();
            this.modal = null;
        }
    }
}

// Global instance
const aiProgress = new AIProgressIndicator();
