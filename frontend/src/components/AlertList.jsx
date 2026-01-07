import React from 'react'
import { deleteAlert } from '../services/api'

const AlertList = ({ alerts, onRefresh }) => {
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'error':
        return 'border-red-500 bg-red-500/10'
      case 'warning':
        return 'border-yellow-500 bg-yellow-500/10'
      case 'info':
        return 'border-blue-500 bg-blue-500/10'
      default:
        return 'border-slate-500 bg-slate-500/10'
    }
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'error':
        return '❌'
      case 'warning':
        return '⚠️'
      case 'info':
        return 'ℹ️'
      default:
        return '📢'
    }
  }

  const handleDismiss = async (alertId) => {
    try {
      await deleteAlert(alertId)
      onRefresh()
    } catch (error) {
      console.error('Error dismissing alert:', error)
    }
  }

  if (alerts.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-slate-400 text-lg">No alerts at this time</p>
        <p className="text-slate-500 text-sm mt-2">All systems operational</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`card border-l-4 ${getSeverityColor(alert.severity)}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <span className="text-2xl">{getSeverityIcon(alert.severity)}</span>
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className={`px-2 py-1 rounded text-xs font-semibold uppercase ${
                    alert.severity === 'error' ? 'bg-red-500 text-white' :
                    alert.severity === 'warning' ? 'bg-yellow-500 text-black' :
                    'bg-blue-500 text-white'
                  }`}>
                    {alert.severity}
                  </span>
                  <span className="text-slate-400 text-sm">
                    {new Date(alert.timestamp).toLocaleString()}
                  </span>
                </div>
                <p className="text-white text-lg">{alert.message}</p>
                {alert.device_id && (
                  <p className="text-slate-400 text-sm mt-1">
                    Device ID: {alert.device_id}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={() => handleDismiss(alert.id)}
              className="ml-4 text-slate-400 hover:text-white transition-colors"
              title="Dismiss alert"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default AlertList
