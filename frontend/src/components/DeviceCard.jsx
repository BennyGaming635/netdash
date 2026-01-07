import React from 'react'

const DeviceCard = ({ device }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return 'status-online'
      case 'offline':
        return 'status-offline'
      default:
        return 'status-warning'
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'router':
        return '🔀'
      case 'access_point':
        return '📡'
      case 'switch':
        return '🔌'
      default:
        return '💻'
    }
  }

  return (
    <div className="card hover:border-primary transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">{getTypeIcon(device.type)}</span>
          <div>
            <h3 className="text-lg font-semibold text-white">{device.name}</h3>
            <p className="text-sm text-slate-400 capitalize">{device.type.replace('_', ' ')}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`status-indicator ${getStatusColor(device.status)}`}></span>
          <span className={`text-sm font-medium ${
            device.status === 'online' ? 'text-green-400' : 'text-red-400'
          }`}>
            {device.status}
          </span>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-slate-400">IP Address:</span>
          <span className="text-white font-mono">{device.ip}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">MAC Address:</span>
          <span className="text-white font-mono text-sm">{device.mac}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Uptime:</span>
          <span className="text-white font-semibold">{device.uptime}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Last Seen:</span>
          <span className="text-white text-sm">
            {new Date(device.last_seen).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Uptime Progress Bar */}
      <div className="mt-4">
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              device.uptime >= 99 ? 'bg-green-500' :
              device.uptime >= 95 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${device.uptime}%` }}
          ></div>
        </div>
      </div>
    </div>
  )
}

export default DeviceCard
