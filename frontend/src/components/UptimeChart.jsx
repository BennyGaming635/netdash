import React from 'react'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const UptimeChart = ({ devices }) => {
  const data = {
    labels: devices.map(d => d.name),
    datasets: [
      {
        label: 'Uptime %',
        data: devices.map(d => d.uptime),
        backgroundColor: devices.map(d => {
          if (d.uptime >= 99) return 'rgba(16, 185, 129, 0.8)'
          if (d.uptime >= 95) return 'rgba(245, 158, 11, 0.8)'
          return 'rgba(239, 68, 68, 0.8)'
        }),
        borderColor: devices.map(d => {
          if (d.uptime >= 99) return 'rgba(16, 185, 129, 1)'
          if (d.uptime >= 95) return 'rgba(245, 158, 11, 1)'
          return 'rgba(239, 68, 68, 1)'
        }),
        borderWidth: 1
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f8fafc',
        bodyColor: '#f8fafc',
        borderColor: '#475569',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: function(context) {
            return `Uptime: ${context.parsed.y.toFixed(2)}%`
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          color: '#94a3b8',
          callback: function(value) {
            return value + '%'
          }
        },
        grid: {
          color: 'rgba(71, 85, 105, 0.3)'
        }
      },
      x: {
        ticks: {
          color: '#94a3b8'
        },
        grid: {
          color: 'rgba(71, 85, 105, 0.3)'
        }
      }
    }
  }

  return (
    <div className="card">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white mb-2">Device Uptime Overview</h3>
        <p className="text-slate-400 text-sm">
          Current uptime percentage for all monitored devices
        </p>
      </div>
      <div style={{ height: '400px' }}>
        <Bar data={data} options={options} />
      </div>
      
      {/* Statistics */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="bg-slate-700/50 rounded-lg p-4 text-center">
          <p className="text-slate-400 text-sm mb-1">Average Uptime</p>
          <p className="text-2xl font-bold text-white">
            {devices.length > 0 
              ? (devices.reduce((sum, d) => sum + d.uptime, 0) / devices.length).toFixed(2)
              : 0}%
          </p>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-4 text-center">
          <p className="text-slate-400 text-sm mb-1">Devices Online</p>
          <p className="text-2xl font-bold text-green-400">
            {devices.filter(d => d.status === 'online').length}
          </p>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-4 text-center">
          <p className="text-slate-400 text-sm mb-1">Devices Offline</p>
          <p className="text-2xl font-bold text-red-400">
            {devices.filter(d => d.status === 'offline').length}
          </p>
        </div>
      </div>
    </div>
  )
}

export default UptimeChart
