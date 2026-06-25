import React, { useState, useEffect } from 'react'
import { Loader2, FileCode, GitBranch, Brain, Shield } from 'lucide-react'

/**
 * Loading status messages that cycle through during analysis
 */
const LOADING_STAGES = [
  {
    icon: FileCode,
    message: 'Ingesting repository files...',
    duration: 2000
  },
  {
    icon: GitBranch,
    message: 'Parsing code modules...',
    duration: 2500
  },
  {
    icon: Brain,
    message: 'Analyzing skill patterns...',
    duration: 3000
  },
  {
    icon: Shield,
    message: 'Grounding hallucination guard thresholds...',
    duration: 2500
  },
  {
    icon: Loader2,
    message: 'Finalizing analysis...',
    duration: 2000
  }
]

/**
 * LoadingState Component
 * Displays an animated loading indicator with cycling status messages
 */
function LoadingState({ message = null, compact = false }) {
  const [currentStageIndex, setCurrentStageIndex] = useState(0)

  /**
   * Cycle through loading stages
   */
  useEffect(() => {
    if (message) {
      // If custom message provided, don't cycle
      return
    }

    const currentStage = LOADING_STAGES[currentStageIndex]
    const timer = setTimeout(() => {
      setCurrentStageIndex((prev) => (prev + 1) % LOADING_STAGES.length)
    }, currentStage.duration)

    return () => clearTimeout(timer)
  }, [currentStageIndex, message])

  const currentStage = LOADING_STAGES[currentStageIndex]
  const CurrentIcon = currentStage.icon
  const displayMessage = message || currentStage.message

  if (compact) {
    return (
      <div className="flex items-center space-x-3">
        <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
        <span className="text-sm text-gray-600">{displayMessage}</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      {/* Animated Icon Container */}
      <div className="relative mb-6">
        {/* Outer pulse ring */}
        <div className="absolute inset-0 rounded-full bg-primary-100 animate-ping opacity-75"></div>

        {/* Inner rotating ring */}
        <div className="relative flex items-center justify-center w-20 h-20 rounded-full bg-primary-50 border-4 border-primary-200">
          <CurrentIcon className="w-10 h-10 text-primary-600 animate-pulse" />
        </div>
      </div>

      {/* Status Message */}
      <div className="text-center space-y-2">
        <h3 className="text-lg font-semibold text-gray-800">
          Agent is processing tree structures...
        </h3>
        <p className="text-sm text-gray-600 animate-pulse">
          {displayMessage}
        </p>
      </div>

      {/* Progress Dots */}
      <div className="flex items-center space-x-2 mt-6">
        {LOADING_STAGES.map((_, index) => (
          <div
            key={index}
            className={`
              h-2 rounded-full transition-all duration-300
              ${index === currentStageIndex
                ? 'w-8 bg-primary-600'
                : 'w-2 bg-gray-300'
              }
            `}
          />
        ))}
      </div>

      {/* Estimated Time */}
      <p className="mt-4 text-xs text-gray-500">
        This may take 30-60 seconds depending on repository size
      </p>
    </div>
  )
}

export default LoadingState
