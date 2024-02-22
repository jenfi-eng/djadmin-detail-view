import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['navbarContainer']

  connect() {
    this.observeThemeAttribute()
  }

  observeThemeAttribute() {
    // Target the <html> element
    const targetNode = document.documentElement

    // Options for the observer
    const config = {
      attributes: true,
      attributeFilter: ['data-theme'],
    }

    // Callback function to execute when mutations are observed
    const callback = (mutationsList, observer) => {
      for (const mutation of mutationsList) {
        if (
          mutation.type === 'attributes' &&
          mutation.attributeName === 'data-theme'
        ) {
          const currentTheme = localStorage.getItem('theme')

          // Set data-bs-theme to the same value
          if (currentTheme === 'auto') {
            // Determine system's theme
            const systemTheme = this.getSystemTheme()
            targetNode.setAttribute('data-bs-theme', systemTheme)

            this._removeTheme()
            this._addTheme(systemTheme)
          } else {
            // Set data-bs-theme to the same value
            targetNode.setAttribute('data-bs-theme', currentTheme)

            this._removeTheme()
            this._addTheme(currentTheme)
          }
        }
      }
    }

    // Create an observer instance linked to the callback function
    const observer = new MutationObserver(callback)

    // Start observing the target node for configured mutations
    observer.observe(targetNode, config)
  }

  getSystemTheme() {
    // Check if the system's theme is set to dark
    if (
      window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    ) {
      return 'dark'
    } else {
      return 'light'
    }
  }

  disconnect() {
    // If you're disconnecting the controller and won't be using it again,
    // you should also disconnect the observer to avoid memory leaks.
    // Make sure to store the observer as an instance variable (e.g., this.observer) when you create it,
    // so you can reference it here.
    this.observer.disconnect()
  }

  _removeTheme() {
    this.navbarContainerTarget.classList.remove('navbar-light')
    this.navbarContainerTarget.classList.remove('bg-light')
    this.navbarContainerTarget.classList.remove('navbar-dark')
    this.navbarContainerTarget.classList.remove('bg-dark')
  }

  _addTheme(name) {
    this.navbarContainerTarget.classList.add(`navbar-${name}`)
    this.navbarContainerTarget.classList.add(`bg-${name}`)
  }
}
