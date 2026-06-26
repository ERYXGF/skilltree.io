import React, { useState } from 'react'
import { Download, Copy, CheckCircle, FileText, Share2 } from 'lucide-react'

/**
 * ExportBar Component
 * Provides export functionality for markdown content
 * Can be used standalone or embedded in other components
 * Phase 60: Added share link functionality
 */
function ExportBar({
  content,
  filename = 'export.md',
  label = 'Export',
  className = '',
  shareId = null
}) {
  const [copySuccess, setCopySuccess] = useState(false)
  const [shareCopySuccess, setShareCopySuccess] = useState(false)

  /**
   * Handle copy to clipboard
   */
  const handleCopy = async () => {
    if (!content) return

    try {
      await navigator.clipboard.writeText(content)
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
      alert('Failed to copy to clipboard')
    }
  }

  /**
   * Handle download as file
   */
  const handleDownload = () => {
    if (!content) return

    try {
      const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download:', error)
      alert('Failed to download file')
    }
  }

  /**
   * Handle share link copy
   * Phase 60: Copy shareable link to clipboard
   */
  const handleShareCopy = async () => {
    if (!shareId) return

    try {
      const shareUrl = `${window.location.origin}/r/${shareId}`
      await navigator.clipboard.writeText(shareUrl)
      setShareCopySuccess(true)
      setTimeout(() => setShareCopySuccess(false), 2000)
    } catch (error) {
      console.error('Failed to copy share link:', error)
      alert('Failed to copy share link')
    }
  }

  /**
   * Render nothing if no content
   */
  if (!content) {
    return null
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {/* Share Link Button (Phase 60) */}
      {shareId && (
        <button
          onClick={handleShareCopy}
          className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors duration-200"
          title="Copy shareable link"
        >
          {shareCopySuccess ? (
            <>
              <CheckCircle className="w-4 h-4 mr-1.5" />
              <span>Link Copied!</span>
            </>
          ) : (
            <>
              <Share2 className="w-4 h-4 mr-1.5" />
              <span>Share</span>
            </>
          )}
        </button>
      )}

      {/* Copy Button */}
      <button
        onClick={handleCopy}
        disabled={!content}
        className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        title="Copy to clipboard"
      >
        {copySuccess ? (
          <>
            <CheckCircle className="w-4 h-4 mr-1.5 text-green-600" />
            <span className="text-green-600">Copied!</span>
          </>
        ) : (
          <>
            <Copy className="w-4 h-4 mr-1.5" />
            <span>Copy</span>
          </>
        )}
      </button>

      {/* Download Button */}
      <button
        onClick={handleDownload}
        disabled={!content}
        className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        title={`Download as ${filename}`}
      >
        <Download className="w-4 h-4 mr-1.5" />
        <span>{label}</span>
      </button>
    </div>
  )
}

export default ExportBar
