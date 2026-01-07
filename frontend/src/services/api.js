import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Devices
export const getDevices = async () => {
  const response = await api.get('/devices')
  return response.data
}

export const getDevice = async (id) => {
  const response = await api.get(`/devices/${id}`)
  return response.data
}

export const addDevice = async (device) => {
  const response = await api.post('/devices', device)
  return response.data
}

// Alerts
export const getAlerts = async (severity = null) => {
  const params = severity ? { severity } : {}
  const response = await api.get('/alerts', { params })
  return response.data
}

export const deleteAlert = async (id) => {
  const response = await api.delete(`/alerts/${id}`)
  return response.data
}

// Uptime
export const getUptime = async (deviceId) => {
  const response = await api.get(`/uptime/${deviceId}`)
  return response.data
}

// Topology
export const getTopology = async () => {
  const response = await api.get('/topology')
  return response.data
}

export default api
