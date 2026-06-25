import React from 'react'
import Plot from 'react-plotly.js'
import { BarChart3, Download, Info } from 'lucide-react'
import LoadingState from './LoadingState'

/**
 * ProficiencyChart Component
 * Displays an interactive horizontal bar chart of skill proficiency scores
 */
function ProficiencyChart({ data, isLoading = false }) {
  /**
   * Generate Plotly chart data from backend response
   */
  const generateChartData = () => {
    if (!data || !data.skills || data.skills.length === 0) {
      return null
    }

    // Sort skills by proficiency score (descending)
    const sortedSkills = [...data.skills].sort((a, b) => b.score - a.score)

    // Extract data for plotting
    const skillNames = sortedSkills.map(skill => skill.skill)
    const proficiencyScores = sortedSkills.map(skill => skill.score)
    const categories = sortedSkills.map(skill => skill.category || 'Other')

    // Color mapping for different categories
    const colorMap = {
      'Language': '#3b82f6',      // blue
      'Framework': '#8b5cf6',     // purple
      'Library': '#06b6d4',       // cyan
      'Tool': '#10b981',          // green
      'Database': '#f59e0b',      // amber
      'Cloud': '#ec4899',         // pink
      'Other': '#6b7280'          // gray
    }

    const colors = categories.map(cat => colorMap[cat] || colorMap['Other'])

    return {
      data: [
        {
          type: 'bar',
          x: proficiencyScores,
          y: skillNames,
          orientation: 'h',
          marker: {
            color: colors,
            line: {
              color: 'rgba(255, 255, 255, 0.5)',
              width: 1
            }
          },
          text: proficiencyScores.map(score => `${score.toFixed(1)}%`),
          textposition: 'outside',
          hovertemplate: '<b>%{y}</b><br>Proficiency: %{x:.1f}%<br><extra></extra>',
        }
      ],
      layout: {
        title: {
          text: 'Skill Proficiency Analysis',
          font: {
            size: 18,
            color: '#1f2937'
          }
        },
        xaxis: {
          title: 'Proficiency Score (%)',
          range: [0, 100],
          gridcolor: '#e5e7eb',
          showgrid: true,
          zeroline: false
        },
        yaxis: {
          title: '',
          automargin: true,
          tickfont: {
            size: 12
          }
        },
        margin: {
          l: 120,
          r: 80,
          t: 60,
          b: 60
        },
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        hovermode: 'closest',
        showlegend: false,
        font: {
          family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
      },
      config: {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        toImageButtonOptions: {
          format: 'png',
          filename: 'skill-proficiency-chart',
          height: 800,
          width: 1200,
          scale: 2
        }
      }
    }
  }

  /**
   * Handle chart download
   */
  const handleDownload = () => {
    // Plotly's built-in download will be triggered via the mode bar
    console.log('Use the camera icon in the chart toolbar to download')
  }

  /**
   * Render loading state
   */
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <LoadingState message="Generating proficiency chart..." />
      </div>
    )
  }

  /**
   * Render empty state
   */
  if (!data || !data.skills || data.skills.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
          <BarChart3 className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          No Chart Data
        </h3>
        <p className="text-sm text-gray-600 max-w-sm">
          Analyze a repository to generate a skill proficiency chart based on the codebase.
        </p>
      </div>
    )
  }

  const chartData = generateChartData()

  if (!chartData) {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-gray-600">Unable to generate chart data</p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-800">
            Skill Proficiency Chart
          </h3>
        </div>

        <div className="flex items-center space-x-2">
          {/* Info Tooltip */}
          <div className="group relative">
            <button className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200">
              <Info className="w-4 h-4" />
            </button>
            <div className="absolute right-0 top-full mt-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
              <p className="mb-2">
                Proficiency scores are calculated based on:
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li>Code complexity and patterns</li>
                <li>File count and usage frequency</li>
                <li>Best practices adherence</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Container */}
      <div className="flex-1 overflow-hidden">
        <Plot
          data={chartData.data}
          layout={chartData.layout}
          config={chartData.config}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%' }}
          className="w-full h-full"
        />
      </div>

      {/* Footer Stats */}
      {data.skills && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-primary-600">
                {data.skills.length}
              </p>
              <p className="text-xs text-gray-600">Total Skills</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-primary-600">
                {Math.max(...data.skills.map(s => s.score)).toFixed(0)}%
              </p>
              <p className="text-xs text-gray-600">Top Score</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-primary-600">
                {(data.skills.reduce((sum, s) => sum + s.score, 0) / data.skills.length).toFixed(0)}%
              </p>
              <p className="text-xs text-gray-600">Average</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProficiencyChart
