import React from 'react'
import ReactMarkdown from 'react-markdown'
import { FileText, Download, Copy, CheckCircle } from 'lucide-react'
import LoadingState from './LoadingState'

/**
 * ResumePanel Component
 * Displays the generated resume in markdown format with export options
 */
function ResumePanel({ data, isLoading = false }) {
  const [copySuccess, setCopySuccess] = React.useState(false)

  /**
   * Handle copy to clipboard
   */
  const handleCopy = async () => {
    if (!data?.resume_markdown) return

    try {
      await navigator.clipboard.writeText(data.resume_markdown)
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  /**
   * Handle download as markdown file
   */
  const handleDownload = () => {
    if (!data?.resume_markdown) return

    const blob = new Blob([data.resume_markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `resume-${Date.now()}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * Render loading state
   */
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <LoadingState message="Generating professional resume..." />
      </div>
    )
  }

  /**
   * Render empty state
   */
  if (!data || !data.resume_markdown) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
          <FileText className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          No Resume Generated
        </h3>
        <p className="text-sm text-gray-600 max-w-sm">
          Analyze a repository to generate a professional resume based on the codebase.
        </p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header with Actions */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-800">
            Professional Resume
          </h3>
        </div>

        <div className="flex items-center space-x-2">
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200"
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
            className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors duration-200"
            title="Download as markdown"
          >
            <Download className="w-4 h-4 mr-1.5" />
            <span>Download</span>
          </button>
        </div>
      </div>

      {/* Resume Content */}
      <div className="flex-1 overflow-auto scrollbar-thin">
        <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-a:text-primary-600 prose-strong:text-gray-900 prose-ul:text-gray-700 prose-ol:text-gray-700">
          <ReactMarkdown
            components={{
              // Custom heading styles
              h1: ({ node, ...props }) => (
                <h1 className="text-2xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-primary-600" {...props} />
              ),
              h2: ({ node, ...props }) => (
                <h2 className="text-xl font-semibold text-gray-900 mt-6 mb-3" {...props} />
              ),
              h3: ({ node, ...props }) => (
                <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2" {...props} />
              ),
              // Custom list styles
              ul: ({ node, ...props }) => (
                <ul className="list-disc list-inside space-y-1 my-3" {...props} />
              ),
              ol: ({ node, ...props }) => (
                <ol className="list-decimal list-inside space-y-1 my-3" {...props} />
              ),
              // Custom paragraph styles
              p: ({ node, ...props }) => (
                <p className="my-2 leading-relaxed" {...props} />
              ),
              // Custom link styles
              a: ({ node, ...props }) => (
                <a className="text-primary-600 hover:text-primary-700 underline" {...props} />
              ),
              // Custom code styles
              code: ({ node, inline, ...props }) => (
                inline ? (
                  <code className="px-1.5 py-0.5 bg-gray-100 text-gray-800 rounded text-sm font-mono" {...props} />
                ) : (
                  <code className="block px-4 py-3 bg-gray-50 text-gray-800 rounded-lg text-sm font-mono overflow-x-auto" {...props} />
                )
              ),
              // Custom blockquote styles
              blockquote: ({ node, ...props }) => (
                <blockquote className="border-l-4 border-primary-600 pl-4 italic text-gray-700 my-4" {...props} />
              ),
            }}
          >
            {data.resume_markdown}
          </ReactMarkdown>
        </div>
      </div>

      {/* Footer Info */}
      {data.metadata && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>
              Generated: {new Date().toLocaleDateString()}
            </span>
            {data.metadata.repo_name && (
              <span className="font-mono">
                {data.metadata.repo_name}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ResumePanel
