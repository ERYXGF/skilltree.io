import React, { useState, useEffect, useRef } from 'react'
import confetti from 'canvas-confetti'
import { analyzeRepo } from './api'
import RepoInput from './components/RepoInput'
import LoadingState from './components/LoadingState'
import ResumePanel from './components/ResumePanel'
import ProficiencyChart from './components/ProficiencyChart'
import SkillTreeView from './components/SkillTreeView'

function App() {
  // Global state management
  const [repoData, setRepoData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [viewMode, setViewMode] = useState('chart') // 'chart' or 'tree'
  const hasShownConfetti = useRef(false) // Track if confetti has been shown

  /**
   * Trigger confetti celebration
   * Phase 59: Confetti on first analysis
   */
  const triggerConfetti = () => {
    const duration = 2000 // 2 seconds
    const end = Date.now() + duration

    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

    const frame = () => {
      confetti({
        particleCount: 3,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: colors
      })
      confetti({
        particleCount: 3,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: colors
      })

      if (Date.now() < end) {
        requestAnimationFrame(frame)
      }
    }

    frame()
  }

  /**
   * Handle repository analysis
   * Phase 56: Now accepts optional target_role parameter
   */
  const handleAnalyze = async (url, targetRole = null) => {
    // Reset state
    setErrorMessage('')
    setRepoData(null)
    setIsLoading(true)

    try {
      const data = await analyzeRepo(url, targetRole)
      setRepoData(data)

      // Trigger confetti on first successful analysis
      if (!hasShownConfetti.current) {
        triggerConfetti()
        hasShownConfetti.current = true
      }
    } catch (error) {
      setErrorMessage(error.message || 'Failed to analyze repository')
      console.error('Analysis error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header Section */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-primary-600">
                SkillTree.io
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                AI-Powered GitHub Repository Analyzer
              </p>
            </div>
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-500">
              <span className="inline-flex items-center px-3 py-1 rounded-full bg-primary-50 text-primary-700 font-medium">
                Beta
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="container mx-auto px-4 py-8">
        {/* Repository Input Section */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Analyze GitHub Repository
            </h2>

            {/* RepoInput Component */}
            <RepoInput onAnalyze={handleAnalyze} isLoading={isLoading} />

            {/* Error Display */}
            {errorMessage && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">
                  <strong>Error:</strong> {errorMessage}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Split-Screen Layout: Resume Panel (Left) + Chart/Tree Panel (Right) */}
        {(isLoading || repoData) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-24rem)]">
            {/* Left Panel: Resume */}
            <div className="panel-container">
              <ResumePanel data={repoData} isLoading={isLoading} />
            </div>

            {/* Right Panel: Proficiency Chart or Skill Tree */}
            <div className="panel-container">
              {/* View Mode Toggle */}
              <div className="bg-white border-b border-gray-200 px-4 py-2 flex gap-2">
                <button
                  onClick={() => setViewMode('chart')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    viewMode === 'chart'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  📊 Chart View
                </button>
                <button
                  onClick={() => setViewMode('tree')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    viewMode === 'tree'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  🌳 Skill Tree
                </button>
              </div>

              {/* Conditional View Rendering */}
              <div className="h-[calc(100%-3.5rem)]">
                {viewMode === 'chart' ? (
                  <ProficiencyChart data={repoData} isLoading={isLoading} />
                ) : (
                  <SkillTreeView data={repoData} isLoading={isLoading} />
                )}
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !repoData && !errorMessage && (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 mb-4">
              <svg
                className="w-8 h-8 text-primary-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              Ready to Analyze
            </h3>
            <p className="text-gray-600 max-w-md mx-auto">
              Enter a GitHub repository URL above to generate a professional resume
              and skill proficiency analysis powered by AI.
            </p>

            {/* Feature Highlights */}
            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="p-6 bg-white rounded-lg shadow-sm">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-800 mb-2">AI-Powered Analysis</h4>
                <p className="text-sm text-gray-600">
                  Advanced algorithms analyze your codebase to extract meaningful insights
                </p>
              </div>

              <div className="p-6 bg-white rounded-lg shadow-sm">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-800 mb-2">Skill Proficiency</h4>
                <p className="text-sm text-gray-600">
                  Visual charts showing your technical expertise across different technologies
                </p>
              </div>

              <div className="p-6 bg-white rounded-lg shadow-sm">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-800 mb-2">Export Ready</h4>
                <p className="text-sm text-gray-600">
                  Download professional resumes in markdown format for easy sharing
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-6 text-center text-sm text-gray-500 border-t border-gray-200">
        <div className="container mx-auto px-4">
          <p>
            SkillTree.io &copy; {new Date().getFullYear()} - Powered by AI
          </p>
          <p className="mt-1 text-xs">
            Analyze public GitHub repositories to generate professional skill assessments
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
