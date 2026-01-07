import { useState, useEffect } from 'react'
import DeviceCard from './components/DeviceCard'
import AlertList from './components/AlertList'
import UptimeChart from './components/UptimeChart'
import TopologyView from './components/TopologyView'
import { connectWebSocket, disconnectWebSocket } from './services/websocket'
import { getDevices, getAlerts } from './services/api'

function App() {
  const [devices, setDevices] = useState([])
  const [alerts, setAlerts] = useState([])
  const [activeView, setActiveView] = useState('devices')
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    // Load initial data
    loadDevices()
    loadAlerts()

    // Connect to WebSocket
    const socket = connectWebSocket()

    socket.on('connect', () => {
      setConnected(true)
      console.log('WebSocket connected')
    })

    socket.on('disconnect', () => {
      setConnected(false)
      console.log('WebSocket disconnected')
    })

    socket.on('device_status_update', (data) => {
      setDevices(prev => prev.map(d => 
        d.id === data.id ? { ...d, status: data.status, last_seen: data.last_seen } : d
      ))
    })

    socket.on('device_status_change', (data) => {
      setDevices(prev => prev.map(d => 
        d.id === data.id ? { ...d, status: data.status, last_seen: data.timestamp } : d
      ))
    })

    socket.on('new_alert', (alert) => {
      setAlerts(prev => [alert, ...prev])
    })

    socket.on('uptime_update', (data) => {
      setDevices(prev => prev.map(d => {
        const deviceData = data.devices.find(ud => ud.id === d.id)
        return deviceData ? { ...d, uptime: deviceData.uptime } : d
      }))
    })

    return () => {
      disconnectWebSocket()
    }
  }, [])

  const loadDevices = async () => {
    try {
      const data = await getDevices()
      setDevices(data)
    } catch (error) {
      console.error('Error loading devices:', error)
    }
  }

  const loadAlerts = async () => {
    try {
      const data = await getAlerts()
      setAlerts(data)
    } catch (error) {
      console.error('Error loading alerts:', error)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">NetDash</h1>
            <div className="flex items-center space-x-2">
              <span className={`status-indicator ${connected ? 'status-online' : 'status-offline'}`}></span>
              <span className="text-sm text-slate-400">
                {connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
          <nav className="flex space-x-4">
            <button
              onClick={() => setActiveView('devices')}
              className={`px-4 py-2 rounded-lg ${
                activeView === 'devices'
                  ? 'bg-primary text-white'
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
            >
              Devices
            </button>
            <button
              onClick={() => setActiveView('topology')}
              className={`px-4 py-2 rounded-lg ${
                activeView === 'topology'
                  ? 'bg-primary text-white'
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
            >
              Topology
            </button>
            <button
              onClick={() => setActiveView('uptime')}
              className={`px-4 py-2 rounded-lg ${
                activeView === 'uptime'
                  ? 'bg-primary text-white'
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
            >
              Uptime
            </button>
            <button
              onClick={() => setActiveView('alerts')}
              className={`px-4 py-2 rounded-lg ${
                activeView === 'alerts'
                  ? 'bg-primary text-white'
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
            >
              Alerts {alerts.length > 0 && (
                <span className="ml-2 bg-red-500 text-white rounded-full px-2 py-0.5 text-xs">
                  {alerts.length}
                </span>
              )}
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {activeView === 'devices' && (
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white mb-2">Connected Devices</h2>
              <p className="text-slate-400">
                {devices.filter(d => d.status === 'online').length} of {devices.length} devices online
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {devices.map(device => (
                <DeviceCard key={device.id} device={device} />
              ))}
            </div>
          </div>
        )}

        {activeView === 'topology' && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-6">Network Topology</h2>
            <TopologyView />
          </div>
        )}

        {activeView === 'uptime' && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-6">Uptime Statistics</h2>
            <UptimeChart devices={devices} />
          </div>
        )}

        {activeView === 'alerts' && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-6">Alerts & Notifications</h2>
            <AlertList alerts={alerts} onRefresh={loadAlerts} />
          </div>
        )}
      </main>
    </div>
  )
}

export default App
