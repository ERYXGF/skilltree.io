import React, { useState } from 'react'
import { Github, Search, AlertCircle, CheckCircle } from 'lucide-react'

/**
 * GitHub URL validation regex
 * Matches: https://github.com/user/repo or github.com/user/repo
 */
const GITHUB_URL_REGEX = /^(https?:\/\/)?(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/i

/**
 * Preset demo repositories for quick testing
 */
const PRESET_REPOS = [
  {
    url: 'https://github.com/facebook/react',
    label: 'React',
    description: 'Popular UI library'
  },
  {
    url: 'https://github.com/microsoft/vscode',
    label: 'VS Code',
    description: 'Code editor'
  },
  {
    url: 'https://github.com/vercel/next.js',
    label: 'Next.js',
    description: 'React framework'
  }
]

/**
 * RepoInput Component
 * Handles GitHub repository URL input with validation and preset examples
 */
function RepoInput({ onAnalyze, isLoading = false }) {
  const [url, setUrl] = useState('')
  const [validationState, setValidationState] = useState(null) // null, 'valid', 'invalid'
  const [touched, setTouched] = useState(false)

  /**
   * Validate GitHub URL format
   */
  const validateUrl = (value) => {
    if (!value.trim()) {
      return null
    }
    return GITHUB_URL_REGEX.test(value.trim()) ? 'valid' : 'invalid'
  }

  /**
   * Handle input change with real-time validation
   */
  const handleChange = (e) => {
    const value = e.target.value
    setUrl(value)

    if (touched) {
      setValidationState(validateUrl(value))
    }
  }

  /**
   * Handle input blur to show validation
   */
  const handleBlur = () => {
    setTouched(true)
    setValidationState(validateUrl(url))
  }

  /**
   * Handle form submission
   */
  const handleSubmit = (e) => {
    e.preventDefault()

    const trimmedUrl = url.trim()
    const state = validateUrl(trimmedUrl)

    setTouched(true)
    setValidationState(state)

    if (state === 'valid' && onAnalyze) {
      onAnalyze(trimmedUrl)
    }
  }

  /**
   * Handle preset chip click
   */
  const handlePresetClick = (presetUrl) => {
    setUrl(presetUrl)
    setValidationState('valid')
    setTouched(true)

    if (onAnalyze) {
      onAnalyze(presetUrl)
    }
  }

  /**
   * Get validation icon
   */
  const getValidationIcon = () => {
    if (!touched || !url.trim()) return null

    if (validationState === 'valid') {
      return <CheckCircle className="w-5 h-5 text-green-500" />
    }

    if (validationState === 'invalid') {
      return <AlertCircle className="w-5 h-5 text-red-500" />
    }

    return null
  }

  /**
   * Get input border color based on validation state
   */
  const getInputBorderClass = () => {
    if (!touched || !url.trim()) {
      return 'border-gray-300 focus:ring-primary-500 focus:border-primary-500'
    }

    if (validationState === 'valid') {
      return 'border-green-500 focus:ring-green-500 focus:border-green-500'
    }

    if (validationState === 'invalid') {
      return 'border-red-500 focus:ring-red-500 focus:border-red-500'
    }

    return 'border-gray-300 focus:ring-primary-500 focus:border-primary-500'
  }

  return (
    <div className="space-y-4">
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          {/* GitHub Icon */}
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Github className="h-5 w-5 text-gray-400" />
          </div>

          {/* Input Field */}
          <input
            type="text"
            value={url}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="https://github.com/username/repository"
            disabled={isLoading}
            className={`
              w-full pl-10 pr-10 py-3
              border rounded-lg
              outline-none transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
              ${getInputBorderClass()}
            `}
            aria-label="GitHub repository URL"
            aria-invalid={validationState === 'invalid'}
          />

          {/* Validation Icon */}
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            {getValidationIcon()}
          </div>
        </div>

        {/* Validation Message */}
        {touched && validationState === 'invalid' && (
          <div className="flex items-start space-x-2 text-sm text-red-600">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <p>
              Please enter a valid GitHub repository URL (e.g., https://github.com/user/repo)
            </p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || validationState === 'invalid' || !url.trim()}
          className="btn-primary w-full flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              <span>Analyze Repository</span>
            </>
          )}
        </button>
      </form>

      {/* Preset Repository Chips */}
      <div className="pt-4 border-t border-gray-200">
        <p className="text-sm font-medium text-gray-700 mb-3">
          Try these examples:
        </p>
        <div className="flex flex-wrap gap-2">
          {PRESET_REPOS.map((preset) => (
            <button
              key={preset.url}
              onClick={() => handlePresetClick(preset.url)}
              disabled={isLoading}
              className="
                inline-flex items-center px-4 py-2
                bg-gray-100 hover:bg-gray-200
                text-gray-700 text-sm font-medium
                rounded-full transition-colors duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
              "
              title={preset.description}
            >
              <Github className="w-4 h-4 mr-2" />
              {preset.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RepoInput
