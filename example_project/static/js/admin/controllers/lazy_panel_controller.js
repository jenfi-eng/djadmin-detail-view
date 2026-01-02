import { Controller } from '@hotwired/stimulus'

/**
 * Stimulus controller for lazy loading admin panel content.
 *
 * Usage:
 * <div data-controller="lazy-panel"
 *      data-lazy-panel-url-value="/admin/app/model/1/lazy/fragment_key/">
 *   <div class="spinner-border"></div>
 * </div>
 *
 * The controller will:
 * 1. On connect, fetch content from the URL
 * 2. Replace the element's innerHTML with the response
 * 3. Handle errors with retry logic
 */
export default class extends Controller {
  static values = {
    url: String,
    retryCount: { type: Number, default: 0 },
    maxRetries: { type: Number, default: 3 },
  }

  connect() {
    this.load()
  }

  async load() {
    try {
      const response = await fetch(this.urlValue, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin',
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const html = await response.text()
      this.element.outerHTML = html
    } catch (error) {
      console.error('Lazy panel load failed:', error)

      if (this.retryCountValue < this.maxRetriesValue) {
        this.retryCountValue++
        // Exponential backoff: 1s, 2s, 3s
        setTimeout(() => this.load(), 1000 * this.retryCountValue)
      } else {
        this.element.innerHTML = `
          <div class="card mb-5">
            <div class="card-body">
              <div class="alert alert-warning mb-0">
                <strong>Failed to load content.</strong>
                <button class="btn btn-sm btn-outline-secondary ms-2" data-action="lazy-panel#load">
                  Retry
                </button>
              </div>
            </div>
          </div>
        `
      }
    }
  }
}
