import React, { useCallback, useMemo } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'

/**
 * SkillTreeView Component
 * Phase 53: Animated skill-tree view
 *
 * Displays an interactive, animated RPG-style skill tree showing:
 * - Skills as nodes with proficiency-based coloring
 * - Prerequisites as connecting edges
 * - Hierarchical layout (foundational → advanced)
 * - Hover for details, click to highlight paths
 */
function SkillTreeView({ data, isLoading }) {
  // Transform backend data into React Flow nodes and edges
  const { initialNodes, initialEdges } = useMemo(() => {
    if (!data?.skill_tree) {
      return { initialNodes: [], initialEdges: [] }
    }

    const { nodes: treeNodes, edges: treeEdges } = data.skill_tree

    // Calculate layout positions using hierarchical layout
    const levelGroups = {}
    treeNodes.forEach(node => {
      const level = node.level || 0
      if (!levelGroups[level]) {
        levelGroups[level] = []
      }
      levelGroups[level].push(node)
    })

    // Position nodes in a hierarchical tree layout
    const nodes = []
    const horizontalSpacing = 250
    const verticalSpacing = 120

    Object.keys(levelGroups).sort((a, b) => a - b).forEach(level => {
      const nodesInLevel = levelGroups[level]
      const levelWidth = nodesInLevel.length * horizontalSpacing
      const startX = -levelWidth / 2

      nodesInLevel.forEach((node, index) => {
        const x = startX + (index * horizontalSpacing) + horizontalSpacing / 2
        const y = parseInt(level) * verticalSpacing

        // Color based on proficiency score
        const score = node.score || 0
        let bgColor, borderColor, textColor

        if (score >= 80) {
          bgColor = '#10b981' // green-500
          borderColor = '#059669' // green-600
          textColor = '#ffffff'
        } else if (score >= 60) {
          bgColor = '#3b82f6' // blue-500
          borderColor = '#2563eb' // blue-600
          textColor = '#ffffff'
        } else if (score >= 40) {
          bgColor = '#f59e0b' // amber-500
          borderColor = '#d97706' // amber-600
          textColor = '#ffffff'
        } else if (score > 0) {
          bgColor = '#6b7280' // gray-500
          borderColor = '#4b5563' // gray-600
          textColor = '#ffffff'
        } else {
          bgColor = '#e5e7eb' // gray-200
          borderColor = '#d1d5db' // gray-300
          textColor = '#6b7280' // gray-500
        }

        nodes.push({
          id: node.id,
          type: 'default',
          position: { x, y },
          data: {
            label: (
              <div className="text-center">
                <div className="font-semibold text-sm">{node.label}</div>
                <div className="text-xs mt-1">Score: {score}</div>
              </div>
            ),
            score: node.score,
            rationale: node.rationale,
            technology: node.technology,
          },
          style: {
            background: bgColor,
            color: textColor,
            border: `2px solid ${borderColor}`,
            borderRadius: '8px',
            padding: '10px',
            width: 180,
            fontSize: '12px',
            boxShadow: score > 0 ? '0 4px 6px rgba(0, 0, 0, 0.1)' : 'none',
          },
          draggable: true,
        })
      })
    })

    // Create edges with animated flow
    const edges = treeEdges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: true,
      style: {
        stroke: '#94a3b8',
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#94a3b8',
      },
    }))

    return { initialNodes: nodes, initialEdges: edges }
  }, [data])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  // Handle node click to highlight connected paths
  const onNodeClick = useCallback((event, node) => {
    // Find all connected nodes (prerequisites and dependents)
    const connectedNodeIds = new Set([node.id])

    // Find prerequisites (incoming edges)
    edges.forEach(edge => {
      if (edge.target === node.id) {
        connectedNodeIds.add(edge.source)
      }
    })

    // Find dependents (outgoing edges)
    edges.forEach(edge => {
      if (edge.source === node.id) {
        connectedNodeIds.add(edge.target)
      }
    })

    // Highlight connected nodes
    setNodes(nds =>
      nds.map(n => ({
        ...n,
        style: {
          ...n.style,
          opacity: connectedNodeIds.has(n.id) ? 1 : 0.3,
        },
      }))
    )

    // Highlight connected edges
    setEdges(eds =>
      eds.map(e => ({
        ...e,
        style: {
          ...e.style,
          opacity: (e.source === node.id || e.target === node.id) ? 1 : 0.2,
        },
      }))
    )
  }, [edges, setNodes, setEdges])

  // Reset highlighting on pane click
  const onPaneClick = useCallback(() => {
    setNodes(nds =>
      nds.map(n => ({
        ...n,
        style: {
          ...n.style,
          opacity: 1,
        },
      }))
    )
    setEdges(eds =>
      eds.map(e => ({
        ...e,
        style: {
          ...e.style,
          opacity: 1,
        },
      }))
    )
  }, [setNodes, setEdges])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading skill tree...</p>
        </div>
      </div>
    )
  }

  if (!data?.skill_tree || initialNodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-500">
          <svg
            className="w-16 h-16 mx-auto mb-4 text-gray-300"
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
          <p className="text-lg font-medium">No skill tree data available</p>
          <p className="text-sm mt-2">Analyze a repository to see the skill progression tree</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full w-full bg-gray-50 rounded-lg overflow-hidden">
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <h3 className="text-lg font-semibold text-gray-800">Skill Tree Visualization</h3>
        <p className="text-sm text-gray-600 mt-1">
          Click a skill to highlight its prerequisites and dependents
        </p>
      </div>

      <div className="h-[calc(100%-4rem)]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          fitView
          fitViewOptions={{
            padding: 0.2,
            includeHiddenNodes: false,
          }}
          minZoom={0.1}
          maxZoom={1.5}
          defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
        >
          <Background color="#e5e7eb" gap={16} />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              const score = node.data?.score || 0
              if (score >= 80) return '#10b981'
              if (score >= 60) return '#3b82f6'
              if (score >= 40) return '#f59e0b'
              if (score > 0) return '#6b7280'
              return '#e5e7eb'
            }}
            maskColor="rgba(0, 0, 0, 0.1)"
          />
        </ReactFlow>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3 text-xs">
        <div className="font-semibold mb-2">Proficiency Levels</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500 border-2 border-green-600"></div>
            <span>Expert (80-100)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-blue-500 border-2 border-blue-600"></div>
            <span>Advanced (60-79)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-amber-500 border-2 border-amber-600"></div>
            <span>Intermediate (40-59)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-500 border-2 border-gray-600"></div>
            <span>Beginner (1-39)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SkillTreeView
