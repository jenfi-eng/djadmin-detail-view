import { Controller } from '@hotwired/stimulus'

/**
 * Stimulus controller for lazy loading admin panel content.
 *
 * Usage:
 * <div data-controller="lazy-panel"
 *      data-lazy-panel-url-value="/admin/app/model/1/lazy/fragment_key/">
 *   <div data-lazy-panel-target="content">
 *     <div class="card">
 *       <div class="card-header">Panel Name</div>
 *       <div class="card-body" data-lazy-panel-target="body">
 *         <div data-lazy-panel-target="spinner">...</div>
 *       </div>
 *     </div>
 *   </div>
 * </div>
 *
 * The controller will:
 * 1. On connect, show spinner and fetch content from the URL
 * 2. On success, replace the content target's innerHTML with the response
 * 3. On error, display error message in the card body with retry option
 *
 * The outer wrapper (with data-controller) persists for future features like refresh.
 */
export default class extends Controller {
  static targets = ['content', 'body', 'spinner']

  static values = {
    url: String,
    retryCount: { type: Number, default: 0 },
    maxRetries: { type: Number, default: 3 },
    loaded: { type: Boolean, default: false },
  }

  connect() {
    this.load()
  }

  /**
   * Refresh the panel content. Can be called externally or via data-action.
   */
  refresh() {
    this.retryCountValue = 0
    this.loadedValue = false
    this.restoreSpinner()
    this.load()
  }

  /**
   * Restore the spinner in the content area for refresh/retry operations.
   */
  restoreSpinner() {
    if (this.hasContentTarget) {
      this.contentTarget.innerHTML = `
        <div class="card mb-5">
          <div class="card-header">Loading...</div>
          <div class="card-body text-center py-5" data-lazy-panel-target="body">
            <div data-lazy-panel-target="spinner">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2 text-muted mb-0">Loading...</p>
            </div>
          </div>
        </div>
      `
    }
  }

  showSpinner() {
    if (this.hasSpinnerTarget) {
      this.spinnerTarget.classList.remove('d-none')
    }
  }

  hideSpinner() {
    if (this.hasSpinnerTarget) {
      this.spinnerTarget.classList.add('d-none')
    }
  }

  showError(message, statusCode = null) {
    this.hideSpinner()

    const statusText = statusCode ? ` (${statusCode})` : ''

    if (this.hasBodyTarget) {
      this.bodyTarget.innerHTML = `
        <div class="alert alert-danger mb-0">
          <div class="d-flex align-items-center justify-content-between">
            <div>
              <i class="fas fa-exclamation-triangle me-2"></i>
              <strong>Failed to load content${statusText}</strong>
              ${message ? `<div class="small mt-1">${message}</div>` : ''}
            </div>
            <button class="btn btn-sm btn-outline-danger" data-action="lazy-panel#retry">
              <i class="fas fa-redo me-1"></i>Retry
            </button>
          </div>
        </div>
      `
    }
  }

  retry() {
    // Reset retry count and reload
    this.retryCountValue = 0

    // Restore spinner in body target (when retrying from error state)
    if (this.hasBodyTarget) {
      this.bodyTarget.innerHTML = `
        <div class="text-center py-5" data-lazy-panel-target="spinner">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted mb-0">Loading...</p>
        </div>
      `
    }

    this.load()
  }

  async load() {
    this.showSpinner()

    try {
      const response = await fetch(this.urlValue, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin',
        redirect: 'error', // Treat redirects as errors
      })

      // Check for non-2xx responses
      if (!response.ok) {
        const errorText = await this.getErrorText(response)
        throw new HttpError(response.status, response.statusText, errorText)
      }

      const html = await response.text()

      // Success - replace content target's innerHTML (preserving outer wrapper)
      if (this.hasContentTarget) {
        this.contentTarget.innerHTML = html
      } else {
        // Fallback: replace element's innerHTML if no content target
        this.element.innerHTML = html
      }
      this.loadedValue = true
    } catch (error) {
      console.error('Lazy panel load failed:', error)

      if (error instanceof HttpError) {
        // HTTP error - show specific error message
        this.showError(error.message, error.status)
      } else if (error.name === 'TypeError' && error.message.includes('redirect')) {
        // Redirect error
        this.showError('Unexpected redirect', 'REDIRECT')
      } else if (this.retryCountValue < this.maxRetriesValue) {
        // Network error - retry with exponential backoff
        this.retryCountValue++
        const delay = 1000 * this.retryCountValue
        console.log(`Retrying in ${delay}ms (attempt ${this.retryCountValue}/${this.maxRetriesValue})`)
        setTimeout(() => this.load(), delay)
      } else {
        // Max retries exceeded
        this.showError('Network error after multiple retries')
      }
    }
  }

  async getErrorText(response) {
    try {
      const text = await response.text()
      // Try to extract a meaningful message from HTML error pages
      const match = text.match(/<title>(.*?)<\/title>/i)
      if (match) {
        return match[1]
      }
      // Return first 100 chars if it's plain text
      if (text.length < 200 && !text.includes('<')) {
        return text
      }
      return response.statusText
    } catch {
      return response.statusText
    }
  }
}

/**
 * Custom error class for HTTP errors
 */
class HttpError extends Error {
  constructor(status, statusText, message) {
    super(message || statusText)
    this.name = 'HttpError'
    this.status = status
    this.statusText = statusText
  }
}
