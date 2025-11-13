import { Controller } from "@hotwired/stimulus"

const STORAGE_KEY = "autodialer-theme"

export default class extends Controller {
  connect() {
    this.mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    this.mediaQueryListener = (event) => {
      if (!localStorage.getItem(STORAGE_KEY)) {
        this.applyTheme(event.matches ? "dark" : "light")
      }
    }

    this.mediaQuery.addEventListener("change", this.mediaQueryListener)
    this.applyTheme(this.initialTheme())
    this.element.classList.remove("preload")
  }

  disconnect() {
    this.mediaQuery?.removeEventListener("change", this.mediaQueryListener)
  }

  toggle() {
    const next = this.currentTheme === "dark" ? "light" : "dark"
    localStorage.setItem(STORAGE_KEY, next)
    this.applyTheme(next)
  }

  initialTheme() {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === "dark" || stored === "light") {
      return stored
    }
    return this.mediaQuery.matches ? "dark" : "light"
  }

  applyTheme(theme) {
    this.currentTheme = theme
    document.documentElement.dataset.theme = theme
    this.element.dataset.theme = theme
  }
}