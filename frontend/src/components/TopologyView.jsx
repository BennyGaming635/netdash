import React, { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import cola from 'cytoscape-cola'
import { getTopology } from '../services/api'

// Register the layout
cytoscape.use(cola)

const TopologyView = () => {
  const containerRef = useRef(null)
  const cyRef = useRef(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTopology()
  }, [])

  const loadTopology = async () => {
    try {
      const data = await getTopology()
      initializeGraph(data)
      setLoading(false)
    } catch (error) {
      console.error('Error loading topology:', error)
      setLoading(false)
    }
  }

  const initializeGraph = (data) => {
    if (!containerRef.current) return

    // Clear existing graph if any
    if (cyRef.current) {
      cyRef.current.destroy()
    }

    const elements = [
      ...data.nodes.map(node => ({
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
          status: node.status
        }
      })),
      ...data.edges.map(edge => ({
        data: {
          source: edge.from,
          target: edge.to
        }
      }))
    ]

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#f8fafc',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 10,
            'width': 60,
            'height': 60,
            'border-width': 3,
            'border-color': '#1e293b',
            'font-size': 14,
            'font-weight': 'bold'
          }
        },
        {
          selector: 'node[status="online"]',
          style: {
            'background-color': '#10b981'
          }
        },
        {
          selector: 'node[status="offline"]',
          style: {
            'background-color': '#ef4444'
          }
        },
        {
          selector: 'node[type="router"]',
          style: {
            'shape': 'diamond'
          }
        },
        {
          selector: 'node[type="access_point"]',
          style: {
            'shape': 'triangle'
          }
        },
        {
          selector: 'node[type="switch"]',
          style: {
            'shape': 'rectangle'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 3,
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
          }
        },
        {
          selector: ':selected',
          style: {
            'border-width': 4,
            'border-color': '#0ea5e9'
          }
        }
      ],
      layout: {
        name: 'cola',
        animate: true,
        randomize: false,
        maxSimulationTime: 1500,
        fit: true,
        padding: 50,
        nodeDimensionsIncludeLabels: true
      }
    })

    // Add click handler for nodes
    cyRef.current.on('tap', 'node', function(evt) {
      const node = evt.target
      console.log('Clicked node:', node.data())
    })
  }

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white mb-2">Interactive Network Map</h3>
          <p className="text-slate-400 text-sm">
            Visual representation of network device connections
          </p>
        </div>
        <button
          onClick={loadTopology}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/80 transition-colors"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-96">
          <div className="text-slate-400">Loading topology...</div>
        </div>
      ) : (
        <div
          ref={containerRef}
          className="bg-slate-900 rounded-lg border border-slate-700"
          style={{ height: '600px', width: '100%' }}
        />
      )}

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center space-x-6">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-green-500 rounded-full"></div>
          <span className="text-slate-400 text-sm">Online</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-red-500 rounded-full"></div>
          <span className="text-slate-400 text-sm">Offline</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-slate-500" style={{ clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)' }}></div>
          <span className="text-slate-400 text-sm">Access Point</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-slate-500" style={{ transform: 'rotate(45deg)' }}></div>
          <span className="text-slate-400 text-sm">Router</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-slate-500"></div>
          <span className="text-slate-400 text-sm">Switch</span>
        </div>
      </div>
    </div>
  )
}

export default TopologyView
